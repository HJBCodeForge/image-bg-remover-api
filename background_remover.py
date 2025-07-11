import io
import time
from PIL import Image
from typing import Tuple
import gc

class BackgroundRemover:
    def __init__(self):
        # Import rembg here to handle different versions
        try:
            from rembg import remove, new_session
            self.remove_func = remove
            try:
                # Try to create a session with u2net model (more memory efficient)
                self.session = new_session('u2net')
            except Exception:
                # If u2net fails, use default
                try:
                    self.session = new_session()
                except Exception:
                    self.session = None
        except ImportError:
            # Fallback if rembg import fails
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
