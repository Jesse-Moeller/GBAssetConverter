# GB Asset Converter
This repo contains a script I wrote which converts (probably) any image into a gbdk compatible sprite (.c) file.

## Requirements
Using python 3 install these packages with pip:

<code> pip install pillow </code>

<code> pip install numpy </code>

## Execution

<code> python .\gbac.py {image or directory} {options} {directory} </code>

### options:
  <code>-p</code> Preview any files as they are being converted.
  
  <code>-r</code> Apply conversions to all images in all subfolders.
  
  <code>-s</code> Save copy of the image as it would appear on the GB screen.
  
  <code>-v</code> Verbose output (not really sure what I'm doing with this, just kind of larping).

## To Do
  1. Develop better workflow for tilemaps
  
