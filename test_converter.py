import cv2
import numpy as np
from converter import LogoConverter
import os

def create_dummy_image(path):
    # Create a white image with a black circle
    img = np.full((500, 500), 255, dtype=np.uint8)
    cv2.circle(img, (250, 250), 100, 0, -1)
    # Add some noise
    noise = np.random.randint(0, 50, (500, 500), dtype=np.uint8)
    img = cv2.subtract(img, noise)
    cv2.imwrite(path, img)
    print(f"Created dummy image at {path}")

def test_conversion():
    dummy_path = "test_logo.png"
    output_path = "test_logo.stl"
    
    create_dummy_image(dummy_path)
    
    converter = LogoConverter()
    print("Processing...")
    try:
        converter.generate_stl(dummy_path, output_path)
        if os.path.exists(output_path):
            size = os.path.getsize(output_path)
            print(f"Success! STL created at {output_path} ({size/1024:.2f} KB)")
        else:
            print("Error: File not found after generation.")
    except Exception as e:
        print(f"Error during conversion: {e}")

if __name__ == "__main__":
    test_conversion()
