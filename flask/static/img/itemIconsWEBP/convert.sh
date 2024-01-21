#!/bin/bash

# Specify the input and output directories
input_directory="."
output_directory="./converted/"

# Ensure the output directory exists
mkdir -p "$output_directory"

# Loop through each PNG file in the input directory
for png_file in "$input_directory"/*.png; do
    # Check if the file is a regular file
    if [ -f "$png_file" ]; then
        # Get the file name without extension
        file_name=$(basename -- "$png_file")
        file_name_no_extension="${file_name%.*}"

        # Convert PNG to WebP using cwebp
        cwebp -q 30 "$png_file" -o "$output_directory/$file_name_no_extension.webp"

        echo "Converted $file_name to WebP"
    fi
done

echo "Conversion complete."