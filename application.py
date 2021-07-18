from typing import Tuple
from PIL import Image
import numpy as np
import sys
import os


GB_COLOR_MAP = {
    3 : [15, 56, 15],
    2 : [48, 98, 48],
    1 : [139, 172, 15],
    0 : [155, 188, 15]
}

def check_image_with_pil(path):
    try:
        Image.open(path)
    except IOError:
        return False
    return True

def format_hex(integer):
    token = hex(int(integer))
    contents = token[2:].upper()
    if len(contents)==1:
        contents = '0' + contents
    return '0x'+contents +','

def handle_inputs(args : list) -> dict:
    
    if len(args) < 2:
        print('No input provided.')
        exit()

    input_dict = {
        "input_path" : "",
        "single_file" : False,
        "directory" : False,
        "preview" : False,
        "preview_save" : False,
        "recursive" : False,
        "verbose" : False,
        "output_path" : ""
    }

## sanitize input_path

    input_dict["input_path"] = args[1]

    if os.path.isfile(input_dict["input_path"]):
        input_dict["single_file"] = True

    elif os.path.isdir(input_dict["input_path"]):
        input_dict["directory"] = True

    else:
        print(f"'{input_dict['input_path']}' is not recognized as a valid file or directory.")
        exit()

## handle options

    options = args[1:-1]

    for arg in options:
        if arg not in ['-p','-ps','-r','-v']:
            print(f"Warning: Argument {arg} not recognized.")

    if '-p' in options or '-ps' in options:
        if input_dict["directory"]:
            print("Warning: Using '-p' while targeting a directory will preview each image file in the directory as it is being converted. Do you wish to proceed?")
            response = ''
            while(response!='Y' and response!='N'):
                response = input("[Y/N]:")
            if response == 'N':
                exit()
        input_dict["preview"] = True

    if '-ps' in options:
        input_dict["preview_save"] = True
        print("Just so you know: All previews will be saved next to their corresponding original image files.")

    if '-r' in options:
        if input_dict["single_file"]:
            print("Bro: The '-r' argument only makes sense when targeting a directory.")
        else:
            input_dict["recursive"] = True

    if '-v' in options:
        input_dict["verbose"] = True

## sanitize output_path

    input_dict["output_path"] = args[-1]

    if not os.path.isdir(input_dict["output_path"]):
        print("Output target must be a directory.")
        quit()
    
    return input_dict

def find_images(path : str) -> list:
    _, dirnames, filenames = os.walk(path)
    list_of_images = [filename for filename in filenames if check_image_with_pil(filename)]
    for dir in dirnames:
        list_of_images += find_images(dir)
    return list_of_images

def resolve_paths(input_dict) -> list:
    if input_dict["single_file"]:




def process_input(input_path, options):
    name, extension = os.path.splitext(input_path)
    color_map = np.vectorize(lambda x: (x <= 58) * 3 + (58 < x <= 110) * 2 + (110 < x <= 151) * 1 + (151 < x) * 0)
    
    
    img = Image.open(input_path).convert('RGBA')
    h,w = img.height, img.width
    white_background = Image.new('RGB', size=(w,h), color=(255,255,255))
    white_background.paste(img, (0,0), mask=img)
    img = white_background
    img = img.convert('L')
    img = np.array(img)
    
    color_by_index = color_map(img)
    if ('-p' in options or '-ps' in options):
        image_preview = np.zeros((h,w,3)).astype('uint8')
        for i in range(h):
            for j in range(w):
                image_preview[i,j] = GB_COLOR_MAP[color_by_index[i,j]]
        image_preview = Image.fromarray(image_preview)
        if '-ps' in options:
            image_preview.save(f"{name}-gb{extension}")
        image_preview.show()

    if w%8!=0:
        print(f"Width of input image '{input_path}' is not a multiple of 8.")
        exit()

    if h%8!=0:
        print(f"Height of input image '{input_path}' is not a multiple of 8.")
        exit()

    shading = np.zeros((2,h,w))
    shading[0,:,:] = ((color_by_index == 1) + (color_by_index == 3)) % 2
    shading[1,:,:] = ((color_by_index == 2) + (color_by_index == 3)) % 2
    tile_cols = int(w / 8)
    unrolled_shading = np.zeros((2, h * tile_cols, 8))
    for j in range(tile_cols):
        unrolled_shading[:,j*h:(j+1)*h,:] = shading[:,:,j*8:(j+1)*8]
    base_2 = np.array([128, 64, 32, 16, 8, 4, 2, 1]).reshape((8,1))
    unrolled_ints = (unrolled_shading @ base_2).reshape(2, tile_cols * h)
    fast_format_hex = np.vectorize(format_hex)
    unrolled_hex = fast_format_hex(unrolled_ints).T.reshape((2*tile_cols*h))
    out_string = f'unsigned char {os.path.basename(input_path).split(".")[0]}[] =\n'
    out_string += '{\n'
    for i in range(int(2*tile_cols*h/8)):
        row = '    ' + ''.join(unrolled_hex[i*8:(i+1)*8]) + '\n'
        out_string += row
    out_string = out_string[:-2]
    out_string += '\n}\n'
    return out_string

def main(args: list) -> int:
    input_dict = handle_inputs(args)
    work_paths = resolve_paths(input_dict)
    recolored_image = process_input(input_path, options)

if __name__ == "__main__":
    exit(main(sys.argv))