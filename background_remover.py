import io
import time
from PIL import Image, ImageEnhance, ImageFilter
from typing import Tuple, Optional
import gc
import logging
import numpy as np
import os

# Force OpenCV to use headless mode
os.environ['OPENCV_HEADLESS'] = '1'
os.environ['DISPLAY'] = ''

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import hybrid system, fallback to legacy if not available
try:
    # Temporarily disable hybrid system for Railway deployment
    # from hybrid_remover import HybridBackgroundRemover
    HYBRID_AVAILABLE = False
    HybridBackgroundRemover = None
    logger.info("Hybrid system temporarily disabled for Railway deployment")
except ImportError as e:
    HYBRID_AVAILABLE = False
    logger.warning(f"Hybrid system not available, using legacy rembg only: {str(e)}")
    HybridBackgroundRemover = None

class BackgroundRemover:
    def __init__(self):
        # Initialize hybrid MediaPipe + rembg system if available
        if HYBRID_AVAILABLE:
            try:
                self.hybrid_remover = HybridBackgroundRemover()
                logger.info("Hybrid system initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize hybrid system: {str(e)}, falling back to legacy")
                self.hybrid_remover = None
        else:
            self.hybrid_remover = None
        
        # Keep legacy rembg support for fallback
        self.remove_func = None
        self.session = None
        self.sessions = {}  # Store multiple sessions for different models
        self._session_initialized = False
        
        # Available models in order of preference for quality
        self.available_models = [
            'u2net_human_seg',    # Best for people/portraits
            'u2net_cloth_seg',    # Best for clothing/fashion
            'isnet-general-use',  # General purpose (if available)
            'silueta',           # Good general purpose, memory efficient
            'u2net',             # Original, reliable fallback
            'u2net_lite'         # Fastest, least memory
        ]
        
        try:
            logger.info("Attempting to import rembg for fallback...")
            
            # Try to import rembg without cv2 dependency first
            try:
                from rembg import remove
                self.remove_func = remove
                logger.info("Successfully imported rembg.remove")
            except ImportError as cv2_error:
                logger.warning(f"rembg import failed (likely cv2 issue): {cv2_error}")
                # Try to work around cv2 issue
                try:
                    # Force headless mode for OpenCV
                    import os
                    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
                    from rembg import remove
                    self.remove_func = remove
                    logger.info("Successfully imported rembg.remove with headless workaround")
                except ImportError as e:
                    logger.error(f"Could not import rembg even with workaround: {e}")
                    self.remove_func = None
            
            # Import new_session but don't create session until needed (lazy loading)
            if self.remove_func:
                try:
                    from rembg import new_session
                    self.new_session = new_session
                    logger.info("Successfully imported new_session - will create sessions on first use")
                except ImportError as e:
                    logger.warning(f"new_session not available: {e}")
                    self.new_session = None
            else:
                self.new_session = None
                
        except ImportError as e:
            logger.error(f"Failed to import rembg: {e}")
            # Fallback if rembg import fails
            self.remove_func = None
            self.new_session = None
        except Exception as e:
            logger.error(f"Unexpected error initializing rembg: {e}")
            self.remove_func = None
            self.new_session = None
    
    def _ensure_session(self, model_name='auto'):
        """
        Lazy initialization of rembg session to save memory on startup
        Now supports multiple models and automatic model selection
        """
        if not self._session_initialized and self.new_session:
            self._session_initialized = True
            
        if model_name == 'auto':
            # Try to create the best available session
            for model in self.available_models:
                if model not in self.sessions:
                    try:
                        logger.info(f"Creating session for model: {model}")
                        session = self.new_session(model)
                        self.sessions[model] = session
                        logger.info(f"Successfully created {model} session")
                        # Set as default session if it's the first successful one
                        if not self.session:
                            self.session = session
                        return session
                    except Exception as e:
                        logger.warning(f"Failed to create {model} session: {e}")
                        continue
                else:
                    # Return existing session
                    return self.sessions[model]
        else:
            # Try to create specific model session
            if model_name not in self.sessions:
                try:
                    logger.info(f"Creating session for specific model: {model_name}")
                    session = self.new_session(model_name)
                    self.sessions[model_name] = session
                    logger.info(f"Successfully created {model_name} session")
                    return session
                except Exception as e:
                    logger.warning(f"Failed to create {model_name} session: {e}")
                    # Fall back to auto mode
                    return self._ensure_session('auto')
            else:
                return self.sessions[model_name]
        
        # If all models fail, return None
        logger.error("Failed to create any session")
        return None
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Apply pre-processing to improve background removal accuracy
        """
        try:
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Enhance contrast for better edge detection
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.2)
            
            # Enhance sharpness slightly for better edge definition
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.1)
            
            # Apply subtle brightness adjustment if image is too dark
            stat = image.histogram()
            avg_brightness = sum(i * w for i, w in enumerate(stat[:256])) / sum(stat[:256])
            if avg_brightness < 100:  # Image is quite dark
                enhancer = ImageEnhance.Brightness(image)
                image = enhancer.enhance(1.15)
            
            return image
            
        except Exception as e:
            logger.warning(f"Pre-processing failed: {e}, using original image")
            return image
    
    def _postprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Apply post-processing to improve the quality of the result
        """
        try:
            # Convert to RGBA if not already
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            # Get image data as numpy array for processing
            img_array = np.array(image)
            
            # Improve alpha channel (transparency) quality
            alpha = img_array[:, :, 3]
            
            # Apply median filter to reduce noise in alpha channel
            # Note: This requires converting back and forth from PIL
            alpha_img = Image.fromarray(alpha, mode='L')
            alpha_img = alpha_img.filter(ImageFilter.MedianFilter(size=3))
            alpha_filtered = np.array(alpha_img)
            
            # Enhance alpha channel contrast for cleaner edges
            alpha_min, alpha_max = alpha_filtered.min(), alpha_filtered.max()
            if alpha_max > alpha_min:
                alpha_enhanced = ((alpha_filtered - alpha_min) / (alpha_max - alpha_min) * 255).astype(np.uint8)
            else:
                alpha_enhanced = alpha_filtered
            
            # Apply the enhanced alpha channel back
            img_array[:, :, 3] = alpha_enhanced
            
            # Convert back to PIL Image
            processed_image = Image.fromarray(img_array, 'RGBA')
            
            return processed_image
            
        except Exception as e:
            logger.warning(f"Post-processing failed: {e}, using original result")
            return image
    
    def _detect_image_type(self, image: Image.Image) -> str:
        """
        Detect the type of image to choose the best model
        """
        try:
            # Simple heuristic based on image characteristics
            width, height = image.size
            aspect_ratio = width / height
            
            # If image is roughly portrait-oriented and not too wide, likely a person
            if 0.5 <= aspect_ratio <= 2.0 and height >= 400:
                return 'human'
            
            # If image is very wide or square and large, might be product/object
            if aspect_ratio > 2.0 or (0.8 <= aspect_ratio <= 1.2 and min(width, height) >= 300):
                return 'object'
            
            # Default to general purpose
            return 'general'
            
        except Exception as e:
            logger.warning(f"Image type detection failed: {e}")
            return 'general'
    
    def _choose_best_model(self, image_type: str) -> str:
        """
        Choose the best model based on image type
        """
        if image_type == 'human':
            return 'u2net_human_seg'  # Best for people
        elif image_type == 'object':
            return 'silueta'  # Good for objects
        else:
            return 'auto'  # Let the system choose
    
    def remove_background(self, image_bytes: bytes, model_hint: Optional[str] = None, 
                         enhance_quality: bool = True) -> Tuple[bytes, float]:
        """
        Remove background using hybrid MediaPipe + rembg system if available,
        otherwise fallback to enhanced rembg system
        
        Args:
            image_bytes: Input image as bytes
            model_hint: Specific model to use ('human', 'object', 'general') or None for auto-detection
            enhance_quality: Whether to apply pre/post processing for better quality
        """
        start_time = time.time()
        
        try:
            # Open the image
            input_image = Image.open(io.BytesIO(image_bytes))
            
            # Smart resizing - preserve detail for better results
            max_size = 1200
            if max(input_image.size) > max_size:
                input_image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Apply pre-processing if enabled
            if enhance_quality:
                input_image = self._preprocess_image(input_image)
            else:
                # Basic conversion to RGB if needed
                if input_image.mode != 'RGB':
                    input_image = input_image.convert('RGB')
            
            # Try hybrid system first if available
            if self.hybrid_remover:
                try:
                    output_image, detection_result = self.hybrid_remover.process_image(input_image)
                    
                    # Log the detection and processing result
                    logger.info(f"Hybrid processing: {detection_result['primary_type']} "
                               f"(confidence: {detection_result['confidence']:.2f}) "
                               f"-> {detection_result['recommended_remover']} "
                               f"({detection_result.get('recommended_model', 'default')})")
                    
                except Exception as e:
                    logger.error(f"Hybrid processing failed: {str(e)}, falling back to legacy rembg")
                    # Fall through to legacy system
                    output_image = None
            else:
                output_image = None
            
            # Fallback to legacy rembg system if hybrid failed or not available
            if output_image is None:
                if not self.remove_func:
                    raise Exception("Both hybrid and legacy systems unavailable - rembg not properly initialized")
                
                # Use legacy detection and removal
                if model_hint:
                    image_type = model_hint
                else:
                    image_type = self._detect_image_type(input_image)
                
                best_model = self._choose_best_model(image_type)
                logger.info(f"Attempting legacy processing with model: {best_model} for type: {image_type}")
                
                session = self._ensure_session(best_model)
                
                if session:
                    logger.info("Using session-based removal")
                    output_image = self.remove_func(input_image, session=session)
                else:
                    logger.info("Using basic removal without session")
                    output_image = self.remove_func(input_image)
                
                logger.info(f"Legacy processing completed: {best_model} for {image_type}")
            
            # Apply post-processing if enabled
            if enhance_quality:
                output_image = self._postprocess_image(output_image)
            
            # Convert to PNG bytes with optimization
            output_buffer = io.BytesIO()
            output_image.save(output_buffer, format='PNG', optimize=True, compress_level=6)
            output_bytes = output_buffer.getvalue()
            
            # Clean up memory
            input_image.close()
            output_image.close()
            output_buffer.close()
            gc.collect()
            
            processing_time = time.time() - start_time
            logger.info(f"Background removal completed in {processing_time:.2f}s")
            
            return output_bytes, processing_time
            
        except Exception as e:
            # Clean up on error
            gc.collect()
            logger.error(f"Error processing image: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            
            # Log more details for debugging
            if hasattr(e, '__traceback__'):
                import traceback
                logger.error(f"Full traceback: {traceback.format_exc()}")
            
            raise Exception(f"Error processing image: {str(e)}")
    
    def validate_image(self, image_bytes: bytes) -> bool:
        """
        Validate if the uploaded file is a valid image
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))
            # Check if it's a valid image format
            image.verify()
            image.close()
            return True
        except Exception:
            return False
    
    def cleanup(self):
        """Clean up resources"""
        if hasattr(self, 'hybrid_remover') and self.hybrid_remover:
            self.hybrid_remover.cleanup()
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()
