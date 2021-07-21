# GB Asset Converter

GBAC is a command line script to convert Game Boy assets (images, tilemaps and sound) into their less-operable GBDK .C encodings. The main idea being that this gives the user the ability to edit the tangible assets however they so choose, leaving conversion to .C encodings as a build step, rather than force the user to edit assets with an editor that is GBDK friendly out-of-the-box.

## Requirements

Using python 3 install these packages with pip:

<code> pip install pillow </code>

<code> pip install numpy </code>

## Execution

<code> python .\gbac.py {image or directory} {options} {directory} </code>

For example, you might try

<code> python .\gbac.py .\test\ -r -s .\assets\ </code>

### options:

  <code>-p</code> Preview any image files as they are being converted.
  
  <code>-r</code> Apply conversions to all relevant files (for now, just images) in all subfolders.
  
  <code>-s</code> Save a copy of the converted image in the original image format next to its GBDK encoding.
  
  <code>-v</code> Verbose output (not really sure what I'm doing with this, just kind of larping).

## To Do (no particular order)

  0. Write out the accompanying .h files
  1. Better heuristic for color mapping (e.g. maximize preservation of Shannon information)
  2. Expand to sound & tilemaps
  
