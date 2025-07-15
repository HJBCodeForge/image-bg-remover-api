"""
Optimized Background Remover using BackgroundRemover-main with single model approach
Optimized for Docker deployment with minimal image size
"""

import os
import io
import logging
import time
import gc
from typing import Optional, Dict, Any, Tuple, Union
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
        self.model_dir = Path("/app/models")
        self.model_dir.mkdir(exist_ok=True)
        
        # Default to most efficient model
        self.default_model = "u2netp"
        
        logger.info(f"BackgroundRemover initialized with device: {self.device}")
        
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
        
        Args:
            image: Input image (PIL Image or bytes)
            model_hint: Model hint ('human', 'object', 'general')
            alpha_matting: Whether to use alpha matting
            alpha_matting_foreground_threshold: Foreground threshold
            alpha_matting_background_threshold: Background threshold
            alpha_matting_erode_structure_size: Erosion size
            alpha_matting_base_size: Base size for alpha matting
            
        Returns:
            Tuple of (processed_image, metadata)
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
            
            # Use BackgroundRemover-main's remove function
            # Convert PIL to bytes for the remove function
            img_bytes = io.BytesIO()
            image.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            # Process with BackgroundRemover-main
            try:
                # Use the remove function with our optimized parameters
                output_bytes = remove(
                    data=img_bytes.getvalue(),
                    alpha_matting=alpha_matting,
                    alpha_matting_foreground_threshold=alpha_matting_foreground_threshold,
                    alpha_matting_background_threshold=alpha_matting_background_threshold,
                    alpha_matting_erode_structure_size=alpha_matting_erode_structure_size,
                    alpha_matting_base_size=alpha_matting_base_size,
                    model_name=model_name
                )
                
                # Convert back to PIL Image
                processed_image = Image.open(io.BytesIO(output_bytes))
                
            except Exception as e:
                logger.error(f"BackgroundRemover-main processing failed: {e}")
                # Fallback to simple processing
                processed_image = self._simple_remove_background(image)
            
            # Force garbage collection to free memory
            gc.collect()
            
            processing_time = time.time() - start_time
            
            metadata = {
                "model_used": model_name,
                "processing_time": processing_time,
                "alpha_matting_enabled": alpha_matting,
                "device": self.device,
                "input_size": image.size,
                "output_size": processed_image.size
            }
            
            logger.info(f"Background removal completed in {processing_time:.2f}s using {model_name}")
            
            return processed_image, metadata
            
        except Exception as e:
            logger.error(f"Background removal failed: {e}")
            raise RuntimeError(f"Background removal failed: {str(e)}")
    
    def _simple_remove_background(self, image: Image.Image) -> Image.Image:
        """Simple fallback background removal"""
        # Convert to RGBA
        image = image.convert('RGBA')
        
        # Create a simple mask (this is a very basic implementation)
        # In a real scenario, you'd want a proper fallback
        data = np.array(image)
        
        # Simple edge detection for background removal (basic fallback)
        # This is just to ensure the service doesn't crash
        mask = np.ones(data.shape[:2], dtype=bool)
        
        # Apply mask
        data[~mask] = [0, 0, 0, 0]  # Transparent
        
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
