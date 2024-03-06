#!/bin/bash

# Input and output directories
input_dir="itemIconsTest"
output_dir="resizedItems"

# Ensure output directory exists
mkdir -p "$output_dir"

# Loop through each PNG file in the input directory
for file in "$input_dir"/*.png; do
    if [ -f "$file" ]; then
        # Extract file name without extension
        filename=$(basename -- "$file")
        filename_noext="${filename%.*}"

        # Use ffmpeg to resize the image
        ffmpeg -i "$file" -vf "scale=25:25" "$output_dir/${filename_noext}_resized.png"
        
        echo "Resized: $file"
    fi
done

echo "Conversion complete!"
