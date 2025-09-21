import os
import requests
from urllib.parse import urlparse
import hashlib
import sys

def generate_filename_from_url(url):
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)
    if not filename:
        filename = "downloaded_image"
    return filename

def hash_content(content):
    return hashlib.md5(content).hexdigest()

def fetch_images(urls):
    directory = "Fetched_Images"
    os.makedirs(directory, exist_ok=True)

    # Maintain a set of hashes to prevent duplicates
    existing_hashes = set()

    # Preload existing files' hashes to avoid duplicates on disk
    for file in os.listdir(directory):
        filepath = os.path.join(directory, file)
        with open(filepath, "rb") as f:
            file_hash = hash_content(f.read())
        existing_hashes.add(file_hash)

    for url in urls:
        url = url.strip()
        if not url:
            continue

        try:
            headers = {
                "User-Agent": "UbuntuImageFetcher/1.0 (+https://github.com/your-username/Ubuntu_Requests)"
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            # Check HTTP headers (content-type)
            content_type = response.headers.get("Content-Type", "")
            if not content_type.startswith("image/"):
                print(f"✗ URL does not point to an image: {url}", file=sys.stderr)
                continue

            content_hash = hash_content(response.content)
            if content_hash in existing_hashes:
                print(f"✗ Duplicate image detected, skipping: {url}")
                continue

            filename = generate_filename_from_url(url)
            filepath = os.path.join(directory, filename)

            # Handle duplicate filenames by appending a suffix
            base, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(filepath):
                filepath = os.path.join(directory, f"{base}_{counter}{ext}")
                counter += 1

            with open(filepath, "wb") as file:
                file.write(response.content)

            existing_hashes.add(content_hash)

            print(f"✓ Successfully fetched: {os.path.basename(filepath)}")
            print(f"✓ Image saved to {filepath}")

        except requests.exceptions.RequestException as e:
            print(f"✗ Connection error for URL {url}: {e}", file=sys.stderr)
        except Exception as e:
            print(f"✗ An error occurred for URL {url}: {e}", file=sys.stderr)

    print("\nConnection strengthened. Community enriched.")

def main():
    print("Welcome to the Ubuntu Image Fetcher")
    print("A tool for mindfully collecting images from the web\n")
    user_input = input("Please enter one or more image URLs (comma-separated): ")
    urls = user_input.split(",")
    fetch_images(urls)

if __name__ == "__main__":
    main()
