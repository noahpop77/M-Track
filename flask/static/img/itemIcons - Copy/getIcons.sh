#!/bin/bash

for i in {1..10000}; do
    url="https://opgg-static.akamaized.net/meta/images/lol/item/${i}.png"
    output_file="item_${i}.png"
    echo "item_${i}.png"
    wget "$url" -O "$output_file"
done