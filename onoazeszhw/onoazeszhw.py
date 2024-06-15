import wget
import os

def download_files():
    # Initialize an empty list to store file URLs
    file_urls = []

    # Ask the user for URLs
    print("Enter the URLs of the files to download. Type 'q' to terminate programme:\n")

    while True:
        url = input("Enter URL: ")
        if url.lower() == 'q':
            break
        if url:  # Check if the input is not empty
            file_urls.append(url)

    # Define the directory to save the downloaded files
    download_directory = './Downloaded_Files/'

    # Create the directory if it does not exist
    if not os.path.exists(download_directory):
        os.makedirs(download_directory)

    # Download each file
    for url in file_urls:
        # Extract the filename from the URL
        filename = url.split('/')[-1]
        
        # Define the full path to save the file
        file_path = os.path.join(download_directory, filename)
        
        # Check if the file already exists
        if not os.path.isfile(file_path):
            print(f"Downloading {filename}...")
            wget.download(url, out=file_path)
            print(f"\n{filename} downloaded and saved to {file_path}.")
        else:
            print(f"{filename} already exists, skipping download.")

    print("All files processed.")

if __name__ == "__main__":
    download_files()