from PIL import Image
import numpy as np

# Create a simple test image
width, height = 200, 200
image_array = np.zeros((height, width, 3), dtype=np.uint8)

# Create a simple pattern - red circle on blue background
center_x, center_y = width // 2, height // 2
radius = 50

for y in range(height):
    for x in range(width):
        # Blue background
        image_array[y, x] = [0, 0, 255]
        
        # Red circle in center
        distance = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
        if distance <= radius:
            image_array[y, x] = [255, 0, 0]

# Convert to PIL Image and save
image = Image.fromarray(image_array)
image.save('test_image.png')
print("✅ Test image created: test_image.png")
