#!/bin/bash

# Your JSON file
json_file="items.json"

# Loop through each element in the JSON
for key in $(jq 'keys[]' "$json_file" | tr -d '"'); do
    # Form the URL
    url="https://opgg-static.akamaized.net/meta/images/lol/14.1.1/item/${key}.png"

    # Download the file using wget
    wget "$url" -O "${key}.png"
done
