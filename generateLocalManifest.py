import os
import json
from dotenv import load_dotenv

# IMPORTANT: You will need to install the `python-dotenv` library.
# Run this command in your terminal:
# pip install python-dotenv

# --- Configuration and Environment Variables ---
# Load environment variables from the .env file
load_dotenv()

# Get the local directory from environment variables
LOCAL_DIRECTORY = os.getenv("LOCAL_DIRECTORY")

# Manifest file path to store uploaded file details
MANIFEST_FILE_PATH = os.path.join(LOCAL_DIRECTORY, ".sync_manifest.json")

# --- Main Function to Generate the Manifest ---
def generate_local_manifest():
    """
    Walks the local directory and generates a manifest of all files and their sizes.
    This manifest can be used for rapid synchronization without a remote server check.
    """
    if not LOCAL_DIRECTORY:
        print("Error: The LOCAL_DIRECTORY environment variable is not set. Please check your .env file.")
        return

    manifest = {}
    print(f"Building manifest for local directory: {LOCAL_DIRECTORY}")

    # Walk through the local directory to find all files and folders
    for root, dirs, files in os.walk(LOCAL_DIRECTORY):
        for file_name in files:
            local_path = os.path.join(root, file_name)
            
            # Calculate the relative path from the base directory
            relative_path = os.path.relpath(local_path, LOCAL_DIRECTORY)
            
            # Use forward slashes for cross-platform compatibility
            remote_path_key = relative_path.replace("\\", "/")
            
            # Get the file size
            local_size = os.path.getsize(local_path)
            
            # Add the file path and size to the manifest
            manifest[remote_path_key] = local_size

    # Save the manifest to a JSON file
    with open(MANIFEST_FILE_PATH, 'w') as f:
        json.dump(manifest, f, indent=4)
    
    print(f"Manifest generated successfully with {len(manifest)} files.")
    print(f"File saved to: {MANIFEST_FILE_PATH}")

# --- Main execution block ---
if __name__ == "__main__":
    generate_local_manifest()
