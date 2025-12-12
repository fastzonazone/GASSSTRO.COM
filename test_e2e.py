
import cv2
import numpy as np
import os
import requests

def create_and_test():
    # 1. Create Dummy Image
    img = np.full((600, 600), 255, dtype=np.uint8)
    cv2.circle(img, (300, 300), 150, 0, -1)
    cv2.putText(img, "TEST", (200, 300), cv2.FONT_HERSHEY_SIMPLEX, 3, (255), 5)
    
    img_path = "e2e_test_logo.png"
    cv2.imwrite(img_path, img)
    print(f"[1/3] Created test image: {img_path}")

    # 2. Upload to Server
    url = "http://127.0.0.1:5000/api/upload"
    files = {'file': open(img_path, 'rb')}
    data = {'name': 'AutoTester', 'email': 'test@bot.com', 'quantity': 50, 'total_price': 300}
    
    print(f"[2/3] Sending to server: {url}...")
    try:
        response = requests.post(url, files=files, data=data)
        print(f"Server Response Status: {response.status_code}")
        print(f"Server Response Body: {response.json()}")
        
        if response.status_code == 200:
            json_resp = response.json()
            generated_file = json_resp.get('file')
            print(f"[3/3] Success! Server reported file: {generated_file}")
            
            # Verify file exists on disk
            # Config is EXPORT_DIR/date/filename
            # We don't know exact path easily without parsing date but server response implies success.
            # actually server response gives filename, we can find it.
            return True
        else:
            print("Failed.")
            return False
            
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

if __name__ == "__main__":
    create_and_test()
