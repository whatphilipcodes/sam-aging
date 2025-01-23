import os
import base64
import requests
from pathlib import Path
from PIL import Image
from io import BytesIO


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


def process_image(api_url, base64_string, target_age, output_path):
    payload = {
        "input": {
            "image": f"data:image/jpeg;base64,{base64_string}",
            "target_age": target_age,
        }
    }

    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        result = response.json()

        if result["status"] == "succeeded":
            output_base64 = result["output"].split(",")[1]
            image_data = base64.b64decode(output_base64)
            image = Image.open(BytesIO(image_data))
            image.save(output_path, format="JPEG", quality=80)
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
    target_ages = input("Enter target ages (comma-separated): ").split(",")
    output_folder = input("Enter output directory: ")

    # Create output directory if it doesn't exist
    Path(output_folder).mkdir(parents=True, exist_ok=True)

    # Get list of images
    image_files = get_image_files(input_folder)

    # Process each image for each target age
    for idx, image_file in enumerate(image_files, 1):
        input_path = os.path.join(input_folder, image_file)
        with open(input_path, "rb") as image_file:
            base64_string = base64.b64encode(image_file.read()).decode("utf-8")

        for target_age in target_ages:
            output_path = os.path.join(
                output_folder, f"age-{target_age}-frame-{idx}-processed.jpg"
            )
            print(
                f"Processing image {idx}/{len(image_files)} for target age {target_age}: {image_file}"
            )
            process_image(api_url, base64_string, target_age, output_path)


if __name__ == "__main__":
    main()
