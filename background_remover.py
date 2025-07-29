"""
Optimized Background Remover using BackgroundRemover-main with single model approach
Optimized for Docker deployment with minimal image size
"""

import os
import io
import logging
import time
import gc
from typing import Optional, Dict, Any, Tuple, Union, List
from pathlib import Path
import requests
import hashlib

import numpy as np
from PIL import Image
import torch
import torchvision.transforms as transforms

# Import BackgroundRemover-main components
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backgroundremover-main'))

from backgroundremover.bg import remove, get_model

logger = logging.getLogger(__name__)

class BackgroundRemover:
    """
    Optimized Background Remover with single model approach and runtime model download
    """
    
    def __init__(self):
        self.device = self._get_device()
        self.model_cache = {}
        # Use local models directory for development, Docker path for production
        if os.path.exists("/app/models"):
            self.model_dir = Path("/app/models")
        else:
            self.model_dir = Path("./models")
        self.model_dir.mkdir(exist_ok=True)
        
        # Default to most efficient model
        self.default_model = "u2netp"
        
        logger.info(f"BackgroundRemover initialized with device: {self.device}")
        logger.info(f"Using models directory: {self.model_dir}")
        
    def _get_device(self) -> str:
        """Get the best available device (CPU optimized for deployment)"""
        # Force CPU for deployment to save memory and avoid CUDA dependencies
        if torch.cuda.is_available():
            logger.info("CUDA available but using CPU for deployment optimization")
        
        if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            logger.info("MPS available but using CPU for deployment optimization")
            
        return "cpu"
    
    def _download_model_if_needed(self, model_name: str) -> str:
        """Download model if not present, with fallback to bundled model"""
        model_filename = f"{model_name}.pth"
        model_path = self.model_dir / model_filename
        
        # Check if model exists locally
        if model_path.exists():
            logger.info(f"Using cached model: {model_path}")
            return str(model_path)
        
        # Check for bundled model
        bundled_model_path = Path(f"backgroundremover-main/models/{model_filename}")
        if bundled_model_path.exists():
            logger.info(f"Using bundled model: {bundled_model_path}")
            return str(bundled_model_path)
        
        # Model download URLs (GitHub releases or other sources)
        model_urls = {
            "u2netp": "https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2netp.pth",
            "u2net": "https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.pth",
            "u2net_human_seg": "https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net_human_seg.pth"
        }
        
        if model_name not in model_urls:
            logger.warning(f"Unknown model {model_name}, falling back to default")
            model_name = self.default_model
            model_filename = f"{model_name}.pth"
            model_path = self.model_dir / model_filename
        
        # Try to download model
        try:
            logger.info(f"Downloading model {model_name}...")
            response = requests.get(model_urls[model_name], timeout=30)
            response.raise_for_status()
            
            with open(model_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Model {model_name} downloaded successfully")
            return str(model_path)
            
        except Exception as e:
            logger.error(f"Failed to download model {model_name}: {e}")
            
            # Last resort: use any available model
            for existing_model in self.model_dir.glob("*.pth"):
                logger.info(f"Using fallback model: {existing_model}")
                return str(existing_model)
            
            raise RuntimeError(f"No model available for {model_name}")
    
    def _get_model_name_from_hint(self, hint: str) -> str:
        """Convert hint to actual model name"""
        model_mapping = {
            "human": "u2net_human_seg",
            "object": "u2net", 
            "general": "u2netp",
            "default": "u2netp"
        }
        return model_mapping.get(hint.lower(), self.default_model)
    
    def remove_background(
        self,
        image: Union[Image.Image, bytes],
        model_hint: str = "general",
        alpha_matting: bool = True,
        alpha_matting_foreground_threshold: int = 240,
        alpha_matting_background_threshold: int = 10,
        alpha_matting_erode_structure_size: int = 10,
        alpha_matting_base_size: int = 1000
    ) -> Tuple[Image.Image, Dict[str, Any]]:
        """
        Remove background from image with optimized single model approach
        """
        start_time = time.time()
        
        try:
            # Convert bytes to PIL Image if needed
            if isinstance(image, bytes):
                image = Image.open(io.BytesIO(image))
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Get model name from hint
            model_name = self._get_model_name_from_hint(model_hint)
            
            # For deployment optimization, always use the most efficient model
            if model_name != "u2netp":
                logger.info(f"Using u2netp instead of {model_name} for deployment optimization")
                model_name = "u2netp"
            
            # Ensure model is available
            model_path = self._download_model_if_needed(model_name)
            
            # Convert PIL to bytes for the remove function
            img_bytes = io.BytesIO()
            image.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            # First try with alpha matting if enabled
            if alpha_matting:
                try:
                    logger.info("Attempting background removal with alpha matting...")
                    # Use much more conservative alpha matting parameters
                    output_bytes = remove(
                        data=img_bytes.getvalue(),
                        alpha_matting=True,
                        alpha_matting_foreground_threshold=200,  # Much lower threshold
                        alpha_matting_background_threshold=50,   # Much higher threshold
                        alpha_matting_erode_structure_size=3,    # Minimal erosion
                        alpha_matting_base_size=300,            # Minimal base size
                        model_name=model_name
                    )
                    processed_image = Image.open(io.BytesIO(output_bytes))
                    alpha_matting_used = True
                    logger.info("Alpha matting successful")
                except Exception as e:
                    if "Cholesky" in str(e):
                        logger.warning("Cholesky decomposition failed, trying without alpha matting")
                    else:
                        logger.warning(f"Alpha matting failed: {e}")
                    
                    # Immediately fall back to no alpha matting
                    logger.info("Falling back to no alpha matting...")
                    output_bytes = remove(
                        data=img_bytes.getvalue(),
                        alpha_matting=False,
                        model_name=model_name
                    )
                    processed_image = Image.open(io.BytesIO(output_bytes))
                    alpha_matting_used = False
                    logger.info("Non-alpha matting successful")
            else:
                # Direct processing without alpha matting
                output_bytes = remove(
                    data=img_bytes.getvalue(),
                    alpha_matting=False,
                    model_name=model_name
                )
                processed_image = Image.open(io.BytesIO(output_bytes))
                alpha_matting_used = False
            
            # Force garbage collection to free memory
            gc.collect()
            torch.cuda.empty_cache() if torch.cuda.is_available() else None
            
            processing_time = time.time() - start_time
            
            metadata = {
                "model_used": model_name,
                "processing_time": processing_time,
                "alpha_matting_enabled": alpha_matting,
                "alpha_matting_used": alpha_matting_used,
                "device": self.device,
                "input_size": image.size,
                "output_size": processed_image.size
            }
            
            logger.info(f"Background removal completed in {processing_time:.2f}s using {model_name}")
            logger.info(f"Alpha matting {'used' if alpha_matting_used else 'not used'}")
            
            return processed_image, metadata
            
        except Exception as e:
            logger.error(f"Background removal failed: {e}")
            # Last resort fallback to simple processing
            try:
                logger.info("Attempting simple background removal fallback...")
                processed_image = self._simple_remove_background(image)
                processing_time = time.time() - start_time
                
                metadata = {
                    "model_used": "simple_fallback",
                    "processing_time": processing_time,
                    "alpha_matting_enabled": False,
                    "alpha_matting_used": False,
                    "device": self.device,
                    "input_size": image.size,
                    "output_size": processed_image.size,
                    "fallback_used": True
                }
                
                return processed_image, metadata
            except Exception as fallback_error:
                logger.error(f"Simple fallback also failed: {fallback_error}")
                raise RuntimeError(f"Background removal failed: {str(e)}")

    def _simple_remove_background(self, image: Image.Image) -> Image.Image:
        """Simple fallback background removal using basic image processing"""
        try:
            # Convert to RGBA
            image = image.convert('RGBA')
            
            # Convert to numpy array
            data = np.array(image)
            
            # Create a simple mask based on brightness
            r, g, b, a = data.T
            brightness = (r + g + b) / 3
            
            # Use Otsu's method for thresholding
            from scipy import ndimage
            thresh = ndimage.gaussian_filter(brightness, sigma=2)
            mask = brightness > thresh.mean()
            
            # Apply some basic morphological operations
            mask = ndimage.binary_opening(mask, structure=np.ones((3,3)))
            mask = ndimage.binary_closing(mask, structure=np.ones((3,3)))
            
            # Expand mask to match image dimensions
            mask = np.stack([mask] * 4, axis=-1)
            
            # Create output array
            output = np.zeros_like(data)
            output[mask] = data[mask]
            
            return Image.fromarray(output, 'RGBA')
            
        except Exception as e:
            logger.error(f"Simple background removal failed: {e}")
            # If all else fails, just make the background transparent
            image = image.convert('RGBA')
            data = np.array(image)
            data[..., 3] = (data[..., :3].mean(axis=2) > 128) * 255
            return Image.fromarray(data, 'RGBA')
    
    def health_check(self) -> Dict[str, Any]:
        """Check health status of the background remover"""
        try:
            # Check if PyTorch is working
            torch_version = torch.__version__
            
            # Check available models
            available_models = []
            for model_file in self.model_dir.glob("*.pth"):
                available_models.append(model_file.stem)
            
            # Check bundled models
            bundled_models = []
            bundled_dir = Path("backgroundremover-main/models")
            if bundled_dir.exists():
                for model_file in bundled_dir.glob("*.pth"):
                    bundled_models.append(model_file.stem)
            
            # Memory usage
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            return {
                "status": "healthy",
                "device": self.device,
                "torch_version": torch_version,
                "available_models": available_models,
                "bundled_models": bundled_models,
                "default_model": self.default_model,
                "memory_usage_mb": round(memory_mb, 2),
                "model_cache_size": len(self.model_cache)
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        models = []
        
        # Check cached models
        for model_file in self.model_dir.glob("*.pth"):
            models.append(model_file.stem)
        
        # Check bundled models
        bundled_dir = Path("backgroundremover-main/models")
        if bundled_dir.exists():
            for model_file in bundled_dir.glob("*.pth"):
                if model_file.stem not in models:
                    models.append(model_file.stem)
        
        # Always include default models that can be downloaded
        default_models = ["u2netp", "u2net", "u2net_human_seg"]
        for model in default_models:
            if model not in models:
                models.append(model)
        
        return sorted(models)
    
    def clear_cache(self):
        """Clear model cache to free memory"""
        self.model_cache.clear()
        gc.collect()
        logger.info("Model cache cleared")
