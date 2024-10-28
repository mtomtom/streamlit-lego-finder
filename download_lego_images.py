import requests
import pandas as pd

def bing_image_search(part_number):
    subscription_key = 'YOUR_BING_API_KEY'  # Replace with your actual Bing API key
    search_url = "https://api.bing.microsoft.com/v7.0/images/search"
    headers = {"Ocp-Apim-Subscription-Key": subscription_key}
    params = {"q": f"LEGO part {part_number}", "count": 1}  # Remove license temporarily

    # Perform the request to the Bing API
    try:
        print(f"Searching for: {params['q']}")
        response = requests.get(search_url, headers=headers, params=params)
        print(f"Request URL: {response.url}")  # Debug: print the request URL
        print(f"Request Headers: {headers}")  # Debug: print the headers
        response.raise_for_status()  # Raises an error for HTTP errors
        search_results = response.json()

        # Download the first image
        if "value" in search_results and len(search_results["value"]) > 0:
            img_url = search_results["value"][0]["contentUrl"]
            img_data = requests.get(img_url).content
            
            # Save the image
            with open(f"{part_number}.jpg", 'wb') as handler:
                handler.write(img_data)
            print(f"Downloaded image for part number {part_number}: {img_url}")
        else:
            print(f"No images found for part number {part_number}.")
    
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
if __name__ == "__main__":
    parts = pd.read_csv("inventory.csv")["Part Number"].unique()
    for part in parts:
        bing_image_search(part)