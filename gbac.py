from PIL import Image
import numpy as np
import sys
import os

LUMINOSITY_TO_GB_COLOR = np.vectorize(lambda x: (x <= 58) * 3 + (58 < x <= 110) * 2 + (110 < x <= 151) * 1 + (151 < x) * 0)
GB_COLOR_MAP = {
    3 : [15, 56, 15],
    2 : [48, 98, 48],
    1 : [139, 172, 15],
    0 : [155, 188, 15]
}

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
    
    if len(args) < 3:
        print('Error: Argument format is <input_path> <options> <output_dir>')
        exit()

    input_dict = {
        "input_path" : "",
        "single_file" : False,
        "directory" : False,
        "preview" : False,
        "recursive" : False,
        "verbose" : False,
        "output_dir" : ""
    }

    input_dict["input_path"] = args[1]

    if os.path.isfile(input_dict["input_path"]):
        input_dict["single_file"] = True

    elif os.path.isdir(input_dict["input_path"]):
        input_dict["directory"] = True

    else:
        print(f"'{input_dict['input_path']}' is not recognized as a valid file or directory.")
        exit()

    options = args[2:-1]

    for arg in options:
        if arg not in ['-p','-r','-s','-v']:
            print(f"Warning: Argument {arg} not recognized.")

    if '-p' in options:
        if input_dict["directory"]:
            print("Warning: Using '-p' while targeting a directory will preview each image file as it is being converted. Do you wish to proceed?")
            response = ''
            while(response!='Y' and response!='N'):
                response = input("[Y/N]:")
            if response == 'N':
                exit()
        input_dict["preview"] = True

    if '-s' in options:
        input_dict["save"] = True

    if '-r' in options:
        if input_dict["single_file"]:
            print("Bro: The '-r' argument only makes sense when targeting a directory.")
        else:
            input_dict["recursive"] = True

    if '-v' in options:
        input_dict["verbose"] = True

    input_dict["output_dir"] = args[-1]
    
    return input_dict

def is_valid_image(path, verbose = False):
    try:
        Image.open(path)
        (w,h) = Image.open(path).size
        assert w % 8 == 0
        assert h % 8 == 0
    except IOError:
        if verbose:
            print(f"Warning: Cannot convert '{path}', it is not recognized as an image file.")
        return False
    except AssertionError:
        if verbose:
            print(f"Warning: Cannot convert '{path}', the dimensions need to be divisible by 8.")
        return False
    return True


class WorkTree:
    
    def __init__(self, in_path : str, out_path :str, image_paths = [], dirs = []):
        self.in_path = in_path
        self.out_path = out_path
        self.image_paths = image_paths
        self.dirs = dirs
    
    def get_children(self, recursive = False, verbose = False) -> None:
        _, dir_names, file_names = next(os.walk(self.in_path))

        if recursive:
            self.dirs = [WorkTree(in_path = self.in_path + dir_name, out_path = self.out_path + dir_name) for dir_name in dir_names]
            for dir in self.dirs:
                dir.get_children(recursive = True)
        
        self.image_paths = []
        for file_name in file_names:
            if is_valid_image(self.in_path + '\\' + file_name, verbose):
                file_name_nx = os.path.splitext(file_name)[0]
                self.image_paths.append((self.in_path + '\\' + file_name, self.out_path + '\\' + file_name_nx + '.c'))

    def _print(self) -> None:
        print(self.image_paths)
        for dir in self.dirs:
            dir._print()
    
    def convert(self, input_dict):
        if not os.path.exists(self.out_path):
            os.mkdir(self.out_path)
        # except OSError:
        #     print(f"Error: '{self.out_path}' is not a valid directory name.")
        #     quit()
        # except FileNotFoundError:
        #     print(f"Error: Cannot find '{self.out_path}'.")
        #     quit()
        # except FileExistsError:
        #     if input_dict["verbose"]:
        #         print("directory {self.out_path} already exists")

        for image_path in self.image_paths:
            process_image(image_path, input_dict)
        
        if input_dict["recursive"]:
            for dir in self.dirs:
                dir.convert(input_dict = input_dict)

def no_extension(file_path : str) -> str:
    return os.path.splitext(os.path.basename(file_path))[0]

def get_work_tree(input_dict : dict) -> WorkTree:
    if input_dict["single_file"]:
        if is_valid_image(input_dict["input_path"], verbose = input_dict["verbose"]):
            parent_dir = os.path.dirname(input_dict["input_path"])
            file_name_nx = no_extension(input_dict["input_path"])
            image_paths = [(input_dict["input_path"], input_dict["output_dir"] + file_name_nx + '.c')]
            return WorkTree(in_path = parent_dir, out_path = input_dict["output_dir"], image_paths = image_paths)
        else:
            quit()
    
    elif input_dict["directory"]:
        work_tree = WorkTree(in_path = input_dict["input_path"], out_path = input_dict["output_dir"])
        work_tree.get_children(recursive = input_dict["recursive"])
        return work_tree


def process_image(image_paths, input_dict) -> None:
    input_path, output_path = image_paths
    name, extension = os.path.splitext(input_path)
    name_nx = no_extension(name)
    
    # open image assuming a white background, convert to luminosity
    img = Image.open(input_path).convert('RGBA')
    h,w = img.height, img.width
    white_background = Image.new('RGB', size=(w,h), color=(255,255,255))
    white_background.paste(img, (0,0), mask=img)
    img = white_background
    img = img.convert('L')
    img = np.array(img)
    
    # use the luminosity to paint the picture with gb colors, preview (and save) if desired
    color_by_index = LUMINOSITY_TO_GB_COLOR(img)
    if (input_dict["preview"] or input_dict["save"]):
        image_preview = np.zeros((h,w,3)).astype('uint8')
        for i in range(h):
            for j in range(w):
                image_preview[i,j] = GB_COLOR_MAP[color_by_index[i,j]]
        image_preview = Image.fromarray(image_preview)

        if input_dict["preview"]:
            image_preview.show()

        if input_dict["save"]:
            out_parent_dir = os.path.dirname(output_path)
            image_preview.save(f"{out_parent_dir}/{name_nx}-gb{extension}")

    '''
    The asset files are stored as lists of an even number of bytes. Each pair of bytes encodes a (1x8) row of pixels; the first byte describes
    shade 1 and the second byte describes shade 2. The byte describes which pixels are shaded by converting the byte to its binary representation,
    and shading each pixel in the row of 8 if there's a 1 and not shading if there's a 0. The resulting shades are added to give the actual
    image that is displated. For example, suppose a row is described by the pair (0x03, 0x01).

    Since 0x03 hex = 0x00000011 bin and 0x01 hex = 0x00000001 bin, 

    shade 1 :   [      ░░]

    shade 2 :   [       ▒]

    displayed : [      ░▓]

    If the width of the image is larger than 8, the rows are traversed top->bottom left->right in that order. This is called "unrolling" in the code below.
    '''

    shading = np.zeros((2,h,w))
    shading[0,:,:] = ((color_by_index == 1) + (color_by_index == 3)) % 2
    shading[1,:,:] = ((color_by_index == 2) + (color_by_index == 3)) % 2

    tile_cols = int(w / 8)
    unrolled_shading = np.zeros((2, h * tile_cols, 8))
    for j in range(tile_cols):
        unrolled_shading[:,j*h:(j+1)*h,:] = shading[:,:,j*8:(j+1)*8]
    base_2 = np.array([128, 64, 32, 16, 8, 4, 2, 1]).reshape((8,1))
    unrolled_ints = (unrolled_shading @ base_2).reshape(2, tile_cols * h)
    np_format_hex = np.vectorize(format_hex)
    unrolled_hex = np_format_hex(unrolled_ints).T.reshape((2*tile_cols*h))

    out_string = f'unsigned char {os.path.basename(input_path).split(".")[0]}[] =\n'
    out_string += '{\n'
    for i in range(int(2*tile_cols*h/8)):
        row = '    ' + ''.join(unrolled_hex[i*8:(i+1)*8]) + '\n'
        out_string += row
    out_string = out_string[:-2]
    out_string += '\n}\n'

    with open(output_path, mode='w') as file:
        file.write(out_string)

def main(args: list) -> int:
    input_dict = handle_inputs(args)
    work_tree = get_work_tree(input_dict)
    work_tree.convert(input_dict)

if __name__ == "__main__":
    exit(main(sys.argv))