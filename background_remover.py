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
        
        try:
            logger.info("Attempting to import rembg...")
            from rembg import remove
            self.remove_func = remove
            logger.info("Successfully imported rembg.remove")
            
            # Try to import new_session for newer versions
            try:
                from rembg import new_session
                logger.info("Attempting to create rembg session...")
                # Try to create a session with u2net model (more memory efficient)
                try:
                    self.session = new_session('u2net')
                    logger.info("Successfully created u2net session")
                except Exception as e:
                    logger.warning(f"Failed to create u2net session: {e}")
                    # If u2net fails, use default
                    try:
                        self.session = new_session()
                        logger.info("Successfully created default session")
                    except Exception as e2:
                        logger.warning(f"Failed to create default session: {e2}")
                        self.session = None
            except ImportError as e:
                logger.warning(f"new_session not available: {e}")
                self.session = None
                
        except ImportError as e:
            logger.error(f"Failed to import rembg: {e}")
            # Fallback if rembg import fails
            self.remove_func = None
            self.session = None
        except Exception as e:
            logger.error(f"Unexpected error initializing rembg: {e}")
            self.remove_func = None
            self.session = None
    
    def remove_background(self, image_bytes: bytes) -> Tuple[bytes, float]:
        """
        Remove background from image bytes and return processed image bytes and processing time
        """
        if not self.remove_func:
            raise Exception("Background removal service not available")
            
        start_time = time.time()
        
        try:
            # Open the image
            input_image = Image.open(io.BytesIO(image_bytes))
            
            # Resize large images to reduce memory usage
            max_size = 1024  # Max dimension in pixels
            if max(input_image.size) > max_size:
                input_image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
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
