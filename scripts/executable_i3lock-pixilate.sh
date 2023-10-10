#!/usr/bin/env sh

# take a screenshot
import -window root $HOME/Pictures/Screenshots/pixalated.png

img=$HOME/Pictures/Screenshots/pixalated.png

convert "$img" -scale 20x20% -modulate 100,50 -scale 500x500% "$img"

i3lock --image $img
