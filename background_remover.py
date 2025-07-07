import io
import time
from PIL import Image
from rembg import remove
from typing import Tuple

class BackgroundRemover:
    def __init__(self):
        pass
    
    def remove_background(self, image_bytes: bytes) -> Tuple[bytes, float]:
        """
        Remove background from image bytes and return processed image bytes and processing time
        """
        start_time = time.time()
        
        try:
            # Open the image
            input_image = Image.open(io.BytesIO(image_bytes))
            
            # Remove background using rembg
            output_image = remove(input_image)
            
            # Convert to PNG bytes
            output_buffer = io.BytesIO()
            output_image.save(output_buffer, format='PNG')
            output_bytes = output_buffer.getvalue()
            
            processing_time = time.time() - start_time
            
            return output_bytes, processing_time
            
        except Exception as e:
            raise Exception(f"Error processing image: {str(e)}")
    
    def validate_image(self, image_bytes: bytes) -> bool:
        """
        Validate if the uploaded file is a valid image
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))
            # Check if it's a valid image format
            image.verify()
            return True
        except Exception:
            return False
