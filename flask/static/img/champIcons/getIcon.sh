#!/bin/bash
names=("https://opgg-static.akamaized.net/meta/images/lol/champion/TwistedFate.png?image=c_crop,h_103,w_103,x_9,y_9/q_auto,f_webp,w_160,h_160&v=1702977255104")
for i in "${names[@]}"; do
    echo "${i}.png"
    wget "$i"
done