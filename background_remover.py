import io
import time
from PIL import Image
from rembg import remove, Session
from typing import Tuple
import gc

class BackgroundRemover:
    def __init__(self):
        # Use a more memory-efficient model
        self.session = Session('u2net')  # Smaller model than default
    
    def remove_background(self, image_bytes: bytes) -> Tuple[bytes, float]:
        """
        Remove background from image bytes and return processed image bytes and processing time
        """
        start_time = time.time()
        
        try:
            # Open the image
            input_image = Image.open(io.BytesIO(image_bytes))
            
            # Resize large images to reduce memory usage
            max_size = 1024  # Max dimension in pixels
            if max(input_image.size) > max_size:
                input_image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Remove background using rembg with session
            output_image = remove(input_image, session=self.session)
            
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
