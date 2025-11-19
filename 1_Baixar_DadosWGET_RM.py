import os
import subprocess

# List with the station codes for download
folders_to_download = ["MGMC"]

base_download_dir = "dados_baixados_Matheus/"                     # Directory where the file will be saved
local_wget = r"C:\Users\seiti\OneDrive\Desktop\IC\comandos_instalados\comandos_instalados\wget.exe"  # Location where wget is installed

# Configuration options
APAGAR = 1  # Set to 1 to delete old .zip files, 0 to keep them
TUDO = 1    # Set to 1 to download all .zip files or 0 to download by year range

# Year range configuration (if TUDO = 0)
start_year = 2024  # Start year
end_year = 2024    # End year


####################### DO NOT EDIT BELOW THIS LINE ####################

# Generate file patterns based on the year range (if necessary)
if not TUDO:
    years = [str(year) for year in range(start_year, end_year + 1)]

# Function to delete old .zip files in the output directory
def delete_old_zip_files(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".zip"):
                file_path = os.path.join(root, file)
                os.remove(file_path)
                print(f"Deleted old .zip file: {file_path}")

# Main loop for each station
for folder_name in folders_to_download:
    # Constructs the full path using the base directory
    output_dir = os.path.join(base_download_dir, folder_name)
    base_url = f"https://geodesy.unr.edu/gps_timeseries/trop/{folder_name}/"

    # Delete old files if APAGAR is set to 1
    if APAGAR:
        if os.path.exists(output_dir):
            print(f"Deleting old .zip files in {output_dir}...")
            delete_old_zip_files(output_dir)

    # Define the acceptance pattern based on the TUDO configuration
    if TUDO:
        accepted_patterns = "*.zip"  # Download all .zip files
    else:
        accepted_patterns = ",".join([f"{folder_name}.{year}.trop.zip" for year in years])

    os.makedirs(output_dir, exist_ok=True)  # Checks if the output directory exists

    # Wget command to download files with the specified pattern
    wget_command = [
        local_wget,
        "-r",
        "-np",
        "-nH",
        "--cut-dirs=4",
        "--timeout=30",
        "--tries=3",
        f"--accept={accepted_patterns}",
        "-P", output_dir,
        base_url
    ]

    print(f"Starting download for station {folder_name}...")
    if not TUDO:
        print(f"Downloading files for years {start_year}-{end_year}...")
    else:
        print("Downloading all available files...")

    process = subprocess.run(wget_command, shell=False)

    if process.returncode == 0:
        print(f"Download completed for station {folder_name}.")
    else:
        print(f"Error downloading data for station {folder_name}. Check the log.")
        break  # Stops the program if there is an error

print("Download completed for all stations.")
