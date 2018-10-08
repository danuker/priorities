# In order to have high quality graphics, we work with SVG.
# However, Pygame does not support it, so we have to convert to PNG.
# This script takes all SVG files in the current directory, and generates PNGs from them into pngs/
# Requires imagemagick (of which mogrify is a component of)

# -background none: do not fill with white background
mogrify -path pngs/ -background none -format png *.svg
