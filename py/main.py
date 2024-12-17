import os
import base64
import requests
from PIL import Image
from pathlib import Path


def get_image_files(folder_path):
    """Get sorted list of image files from folder"""
    files = [
        f for f in os.listdir(folder_path) if f.endswith((".png", ".jpg", ".jpeg"))
    ]
    return sorted(files)


def image_to_base64(image_path):
    """Convert image to base64 string"""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")


def process_image(base64_string, output_path, api_url):
    """Send POST request and save response"""
    headers = {"Content-Type": "application/json"}
    payload = {"image": base64_string}

    try:
        # Set timeout to 120 seconds (2 minutes)
        response = requests.post(api_url, json=payload, headers=headers, timeout=120)
        if response.status_code == 200:
            # Assuming the response contains image data
            with open(output_path, "wb") as f:
                f.write(response.content)
            return True
    except requests.exceptions.Timeout:
        print("Request timed out after 120 seconds")
        return False
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return False
    return False


def main():
    # Configuration
    input_folder = input("Enter path to image sequence folder: ")
    api_url = input("Enter API URL: ")
    output_folder = "./out"

    # Create output directory if it doesn't exist
    Path(output_folder).mkdir(parents=True, exist_ok=True)

    # Get list of images
    image_files = get_image_files(input_folder)

    # Process each image
    for idx, image_file in enumerate(image_files, 1):
        input_path = os.path.join(input_folder, image_file)
        output_path = os.path.join(output_folder, f"processed_{idx}.png")

        print(f"Processing image {idx}/{len(image_files)}: {image_file}")

        # Convert to base64
        base64_string = image_to_base64(input_path)

        # Send request and save result
        if process_image(base64_string, output_path, api_url):
            print(f"Successfully processed and saved: {output_path}")
        else:
            print(f"Failed to process: {image_file}")


if __name__ == "__main__":
    main()
