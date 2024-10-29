import requests
import pandas as pd
import os
import sys
from PIL import Image
from io import BytesIO

def bing_image_search(part_number, subscription_key):
    search_url = "https://api.bing.microsoft.com/v7.0/images/search"
    headers = {"Ocp-Apim-Subscription-Key": subscription_key}
    params = {"q": f"LEGO part {part_number}", "count": 5}  # Download 5 images

    # Perform the request to the Bing API
    try:
        print(f"Searching for: {params['q']}")
        response = requests.get(search_url, headers=headers, params=params)
        print(f"Request URL: {response.url}")  # Debug: print the request URL
        print(f"Request Headers: {headers}")  # Debug: print the headers
        response.raise_for_status()  # Raises an error for HTTP errors
        search_results = response.json()

        # Download the images
        for img_info in search_results.get("value", []):
            img_url = img_info["contentUrl"]
            try:
                img_data = requests.get(img_url).content
                img = Image.open(BytesIO(img_data))
                img.verify()  # Verify that it is an actual image

                # Save the first valid image
                with open(f"{part_number}.jpg", 'wb') as handler:
                    handler.write(img_data)
                print(f"Downloaded image for part number {part_number}: {img_url}")
                break  # Exit after saving the first valid image
            except Exception as e:
                print(f"Failed to download or verify image from {img_url}: {e}")
        else:
            print(f"No valid images found for part number {part_number}.")
    
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python download_lego_images.py <BING_API_KEY>")
        sys.exit(1)

    subscription_key = sys.argv[1]
    parts = pd.read_csv("updated_lego_data (1).csv")["ElementID"].unique()
    for part in parts:
        bing_image_search(part, subscription_key)