import instaloader
import re
import os

async def download_instagram_post_imageV2(url, unique_id):
    # Create an instance of Instaloader
    loader = instaloader.Instaloader()

    # Define the regex pattern to extract the shortcode from the URL
    # shortcode_pattern = r"instagram\.com/p/([a-zA-Z0-9-_]+)/"
    shortcode_pattern = r"instagram\.com/(?:p|reel)/([a-zA-Z0-9-_]+)/"
    match = re.search(shortcode_pattern, url)
    
    # List to store file paths
    file_paths = []

    if match:
        shortcode = match.group(1)
        
        try:
            print(f"Downloading media from: {url}")
            
            # Define the full target directory path
            target_dir = unique_id  # Only use unique_id, no need for the "downloads" prefix
            
            # Ensure the target directory exists
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            
            # Download the post's media into the specified folder
            loader.download_post(instaloader.Post.from_shortcode(loader.context, shortcode), target=target_dir)
            
            # Traverse the target directory to collect all file paths (images and videos)
            for root, dirs, files in os.walk(target_dir):
                for file in files:
                    file_paths.append(os.path.join(root, file))
            
            print("Download complete!")
        except Exception as e:
            print(f'[ERROR] {e}')
    else:
        print("Invalid Instagram post URL")
    
    # Return the list of downloaded file paths
    return file_paths
