#!/bin/bash

# Your JSON file containing the mapping of id numbers to names
items_json="items.json"

# Loop through each entry in the JSON
for id in $(jq -r 'keys_unsorted[]' "$items_json"); do
    # Extract name from the JSON entry
    name=$(jq -r ".[\"$id\"]" "$items_json")

    # Check if the file with the current id exists
    if [ -e "${id}.png" ]; then
        # Rename the file to the corresponding name
        mv "${id}.png" "${name}.png"
        echo "Renamed ${id}.png to ${name}.png"
    fi
done
