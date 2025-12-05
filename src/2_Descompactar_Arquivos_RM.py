import os
import zipfile
import shutil
import gzip

# List with the station codes for download
folders_to_download = ["MGMC"]

# Path to the main folder
base_dir = "dados_Baixados_Matheus"

# Function to extract .gz files
def extract_gz(file_path, extract_to):
    with gzip.open(file_path, 'rb') as f_in:
        with open(extract_to, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    # Remove the original .gz file after extraction
    os.remove(file_path)
    print(f".gz file removed: {file_path}")

# Function to extract .zip files and any .gz files inside them
def extract_zip(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # Directory where the .zip files will be extracted
        extract_dir = zip_path.replace('.zip', '')
        zip_ref.extractall(extract_dir)
        print(f"Files extracted to: {extract_dir}")
        
        # Navigate through the extracted folder to decompress .gz files
        for root, _, files in os.walk(extract_dir):
            for file in files:
                if file.endswith('.gz'):
                    gz_file_path = os.path.join(root, file)
                    output_file = gz_file_path.replace('.gz', '')
                    extract_gz(gz_file_path, output_file)
                    print(f".gz file extracted: {output_file}")

    # Remove the original .zip file after extraction
    os.remove(zip_path)
    print(f".zip file removed: {zip_path}")

# Main function to extract .zip files in the listed folders
def main():
    for folder in folders_to_download:
        folder_path = os.path.join(base_dir, folder)
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith('.zip'):
                    zip_path = os.path.join(root, file)
                    print(f"Extracting {zip_path} in folder {folder}...")
                    extract_zip(zip_path)

if __name__ == "__main__":
    main()
