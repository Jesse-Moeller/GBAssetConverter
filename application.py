from PIL import Image
import numpy as np
import sys
import os


def check_image_with_pil(path):
    try:
        Image.open(path)
    except IOError:
        return False
    return True

def byte_to_hex(array):
    base_2 = [int(128 / 2**i) for i in range(8)]
    integer = base_2 @ array
    token = hex(integer)
    contents = token[2:].upper()
    if len(contents)==1:
        contents = '0' + contents
    return '0x'+contents +','

def consume_args():
    if len(sys.argv) < 2:
        print('No input provided.')
        exit()

    input_path = sys.argv[1]
    options = [token for token in sys.argv[1:] if token[0] == '-']
    # if sys.argv[-1]!='-': output_path = sys.argv[-1] 

    # if sys.argv[-1] not in options:
    #     output_path = sys.argv[-1]


    # if os.path.isdir(input_path):
    #     print("this is a directory")
    #     exit()

    if os.path.isfile(input_path):
        if check_image_with_pil(input_path):
            return input_path, options
        else:
            print(f"Input file '{input_path}' is not a recognized image file.")
            exit()

    else:
        print(f"Input argument '{input_path}' is not a valid image.")
        exit()

def process_input(input_path, options):
    name, extension = os.path.splitext(input_path)
    img = Image.open(input_path).convert('RGBA')
    h,w = img.height, img.width
    white_background = Image.new('RGB', size=(w,h), color=(255,255,255))
    white_background.paste(img, (0,0), mask=img)
    img = white_background

    img = img.convert('L')
    img = np.array(img)
    color_map = np.vectorize(lambda x: int((1-x/255)*3))
    abstractly_colored_img = color_map(img)

    if ('-p' in options or '-ps' in options):
        gb_color_map = {
            3 : [15, 56, 15],
            2 : [48, 98, 48],
            1 : [139, 172, 15],
            0 : [155, 188, 15]
        }
        image_preview = np.zeros((h,w,3)).astype('uint8')
        for i in range(h):
            for j in range(w):
                image_preview[i,j] = gb_color_map[abstractly_colored_img[i,j]]
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

    shade_1 = ((abstractly_colored_img == 1) + (abstractly_colored_img == 3)) % 2
    shade_2 = ((abstractly_colored_img == 2) + (abstractly_colored_img == 3)) % 2
    cols = int(w/8)
    byte_array = []
    for j in range(cols):
        for i in range(h):
            img_row = [byte_to_hex(shade_1[i][8 * j: 8 * j +8]),byte_to_hex(shade_2[i][8 * j: 8 * j +8])]
            byte_array += img_row
    out_string = f'unsigned char {os.path.basename(input_path).split(".")[0]}[] ='
    out_string += '\n{\n'
    for i in range(int(len(byte_array)/8)):
        row = '    ' + ''.join(byte_array[i*8:(i+1)*8]) + '\n'
        out_string += row
    out_string = out_string[:-2]
    out_string += '\n}'
    print(out_string)

    


def main():
    input_path, options = consume_args()
    recolored_image = process_input(input_path, options)
        

    

if __name__ == "__main__":
    "[input file] [options] [output file]"
    main()