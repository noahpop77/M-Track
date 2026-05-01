#!/bin/bash

# Your JSON file
json_file="champs.json"

# Loop through each element in the JSON
for key in $(jq 'keys[]' "$json_file" | tr -d '"'); do
    # Form the URL
    url="https://opgg-static.akamaized.net/meta/images/lol/16.9.1/champion/${key}.png"

    # Download the file using wget
    wget "$url" -O "./champIcons2/${key}.png"
done
