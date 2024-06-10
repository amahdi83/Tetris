#!/bin/bash

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null
then
    echo "PyInstaller could not be found. Installing PyInstaller..."
    pip install pyinstaller
fi

# Navigate to the directory containing the script
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$script_dir"

# Define the paths for the additional data
LEADERBOARD="leaderboard.txt"
ASSETS="assets"

# Run PyInstaller to create an executable with additional data
pyinstaller --onefile --add-data="${LEADERBOARD}:." --add-data="${ASSETS}:assets" --windowed test.py

# Move the executable to the desired location (optional)
# mv dist/test /desired/location/

# Clean up the build files created by PyInstaller (optional)
rm -rf build
rm -rf *.spec
rm -rf __pycache__

echo "Deployment complete. Executable created in the 'dist' directory."
