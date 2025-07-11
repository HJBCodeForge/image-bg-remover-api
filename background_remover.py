import io
import time
from PIL import Image
from typing import Tuple
import gc
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BackgroundRemover:
    def __init__(self):
        # Import rembg here to handle different versions
        self.remove_func = None
        self.session = None
        self._session_initialized = False
        
        try:
            logger.info("Attempting to import rembg...")
            from rembg import remove
            self.remove_func = remove
            logger.info("Successfully imported rembg.remove")
            
            # Import new_session but don't create session until needed (lazy loading)
            try:
                from rembg import new_session
                self.new_session = new_session
                logger.info("Successfully imported new_session - will create session on first use")
            except ImportError as e:
                logger.warning(f"new_session not available: {e}")
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
    
    def _ensure_session(self):
        """Lazy initialization of rembg session to save memory on startup"""
        if not self._session_initialized and self.new_session:
            try:
                logger.info("Creating rembg session on first use...")
                # Try u2net_lite first (most memory efficient)
                try:
                    self.session = self.new_session('u2net_lite')
                    logger.info("Successfully created u2net_lite session")
                except Exception as e:
                    logger.warning(f"Failed to create u2net_lite session: {e}")
                    # Try silueta (also memory efficient)
                    try:
                        self.session = self.new_session('silueta')
                        logger.info("Successfully created silueta session")
                    except Exception as e2:
                        logger.warning(f"Failed to create silueta session: {e2}")
                        # Fall back to default u2net
                        try:
                            self.session = self.new_session('u2net')
                            logger.info("Successfully created u2net session")
                        except Exception as e3:
                            logger.warning(f"Failed to create u2net session: {e3}")
                            self.session = None
            except Exception as e:
                logger.error(f"Failed to create any session: {e}")
                self.session = None
            finally:
                self._session_initialized = True
    
    def remove_background(self, image_bytes: bytes) -> Tuple[bytes, float]:
        """
        Remove background from image bytes and return processed image bytes and processing time
        """
        if not self.remove_func:
            raise Exception("Background removal service not available")
            
        start_time = time.time()
        
        try:
            # Ensure session is created (lazy loading)
            self._ensure_session()
            
            # Open the image
            input_image = Image.open(io.BytesIO(image_bytes))
            
            # More aggressive resizing to save memory
            max_size = 800  # Reduced from 1024 to save memory
            if max(input_image.size) > max_size:
                input_image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Convert to RGB if needed (some formats cause issues)
            if input_image.mode != 'RGB':
                input_image = input_image.convert('RGB')
            
            # Remove background using rembg with session if available
            if self.session:
                output_image = self.remove_func(input_image, session=self.session)
            else:
                output_image = self.remove_func(input_image)
            
            # Convert to PNG bytes
            output_buffer = io.BytesIO()
            output_image.save(output_buffer, format='PNG', optimize=True)
            output_bytes = output_buffer.getvalue()
            
            # Clean up memory
            input_image.close()
            output_image.close()
            output_buffer.close()
            gc.collect()
            
            processing_time = time.time() - start_time
            
            return output_bytes, processing_time
            
        except Exception as e:
            # Clean up on error
            gc.collect()
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
