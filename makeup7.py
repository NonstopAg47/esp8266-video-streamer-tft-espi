import subprocess
import numpy as np
import ffmpeg
from pathlib import Path
from os import scandir
from PIL import Image
import struct  # for packing data as binary
import os
import shutil
import argparse

image_extensions = [".jpg", ".jpeg", ".png", ".tif", ".tiff"]

class Pathex:
    def scantree(self, path):
        """Recursively yield DirEntry objects for given directory."""
        for entry in scandir(path):
            if entry.is_dir(follow_symlinks=False):
                yield from self.scantree(entry.path)  # see below for Python 2.x
            else:
                yield entry
            
    def get_first_file_by_stem (self, dir_path, stem, exts=None):
        dir_path = Path (dir_path)
        stem = stem.lower()

        if dir_path.exists():
            for x in sorted(list(scandir(str(dir_path))), key=lambda x: x.name):
                if not x.is_file():
                    continue
                xp = Path(x.path)
                if xp.stem.lower() == stem and (exts is None or xp.suffix.lower() in exts):
                    return xp

        return None

    def get_image_paths(self, dir_path, image_extensions=image_extensions, subdirs=False, return_Path_class=False):
        dir_path = Path (dir_path)

        result = []
        if dir_path.exists():

            if subdirs:
                gen = self.scantree(str(dir_path))
            else:
                gen = scandir(str(dir_path))

            for x in list(gen):
                if any([x.name.lower().endswith(ext) for ext in image_extensions]):
                    result.append( x.path if not return_Path_class else Path(x.path) )
        return sorted(result)

class Preprocess_Utils:
    # Function to convert an image to binary RGB565 and save it
    def convert_and_save_image_binary(self, image_path, output_dir):
        # Open an image
        image = Image.open(image_path)

        # Convert the image to RGB mode if it's not already
        image = image.convert('RGB')

        # Resize the image to 128x160
        new_size = (128, 160)
        image = image.resize(new_size)

        # Get the dimensions of the resized image
        width, height = image.size

        # Create a list to store binary pixel data
        binary_data = bytearray()

        # Loop through each pixel and convert to 16-bit RGB565 and then as raw bytes
        for y in range(height):
            for x in range(width):
                r, g, b = image.getpixel((x, y))
                rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                # Pack as 2-byte binary (big endian)
                binary_data += struct.pack('>H', rgb565)

        # Get the image file name without extension
        image_name = os.path.splitext(os.path.basename(image_path))[0]

        # Create the folder if it doesn't exist
        save_dir = os.path.join(output_dir, image_name)
        os.makedirs(save_dir, exist_ok=True)

	# write the entire binary data to one file
        output_file = os.path.join(save_dir, f'output.bin')
        with open(output_file, 'wb') as f:
                 f.write(binary_data)

        print(f"Processed '{image_name}' to binary file.")

        # Split binary data into chunks of 1792 pixels (each pixel = 2 bytes)
        #chunk_size = 1792 * 2  # 1792 pixels (128x14) * 2 bytes per pixel
        #for i in range(0, len(binary_data), chunk_size):
        #    chunk = binary_data[i:i + chunk_size]
        #    output_file = os.path.join(save_dir, f'output_{i // chunk_size + 1}.bin')
        #    with open(output_file, 'wb') as f:
        #        f.write(chunk)

        #print(f"Processed and split '{image_name}' into {len(binary_data) // chunk_size + (1 if len(binary_data) % chunk_size else 0)} binary files.")
    

def extract_video(input_file, output_dir):
    pathex = Pathex()

    output_ext = "jpg"
    fps = 0
    
    input_file_path = Path(input_file)
    output_path = Path(output_dir)

    if not output_path.exists():
        output_path.mkdir(exist_ok=True)


    if input_file_path.suffix == '.*':
        input_file_path = pathex.get_first_file_by_stem (input_file_path.parent, input_file_path.stem)
    else:
        if not input_file_path.exists():
            input_file_path = None

    for filename in pathex.get_image_paths (output_path, ['.'+output_ext]):
        Path(filename).unlink()

    job = ffmpeg.input(str(input_file_path))

    kwargs = {'pix_fmt': 'rgb24'}
    if fps != 0:
        kwargs.update ({'r':str(fps)})

    kwargs.update ({'q:v':'2'}) #highest quality for jpg

    job = job.output( str (output_path / ('%5d.'+output_ext)), **kwargs )

    try:
        job = job.run()
        print("vid -> jpg converted")
    except:
        print("ffmpeg fail, job commandline:" + str(job.compile()) )

def drop_frames(folder_path, interval = 31):
    # Specify the interval (keep every nth image)   set it bw 30 and 40  if vid is fast reduce interval

    #dont drop frames
    if interval == 0:
        return

    # Get a list of all files in the folder
    files = os.listdir(folder_path)

    # Sort the files to ensure they are in the correct order
    files.sort()

    # Initialize a counter to keep track of the current file
    current_file = 1

    # Loop through the files in the folder
    for file_name in files:
        if current_file % interval != 1:
            # If it's not the nth image (or the first image), delete it
            file_path = os.path.join(folder_path, file_name)
            os.remove(file_path)
        current_file += 1
    print(f"Images have been processed. Every {interval} image has been kept, and the rest have been deleted.")

def rotate_images(input_folder):
    # Input folder path

    # List all files in the input folder
    image_files = [f for f in os.listdir(input_folder) if f.endswith(('.jpg', '.jpeg', '.png', '.gif'))]

    for filename in image_files:
        input_path = os.path.join(input_folder, filename)

        try:
            # Open the image
            img = Image.open(input_path)

            # Rotate the image by 90 degrees to the right
            img = img.transpose(Image.ROTATE_270)

            # Save the rotated image, overwriting the original file
            img.save(input_path)

            print(f"Rotated and replaced {filename}")            
        except Exception as e:
            print(f"Error processing {filename}: {e}")
    print("images rotated")

def rename_files(folder_path):
    # Initialize counter
    counter = 1

    # Get list of files (exclude directories)
    files = [f for f in os.listdir(folder_path) 
             if os.path.isfile(os.path.join(folder_path, f))]

    # Sort files to maintain consistent order
    files.sort()

    for filename in files:
        old_path = os.path.join(folder_path, filename)
        
        # Get file extension
        _, extension = os.path.splitext(filename)
        
        # Format as 5-digit number (00001, 00002, ...)
        new_name = f"{counter:05d}{extension}"
        new_path = os.path.join(folder_path, new_name)
        
        # Rename file
        os.rename(old_path, new_path)
        
        counter += 1
    print("Files have been renamed in numerical order.")

def convert_to_bin(temp_dir, output_dir):
    preprocess_utils = Preprocess_Utils() 
    # Iterate through all image files in the input folder and process each one
    for filename in os.listdir(temp_dir):
        if filename.lower().endswith('.jpg'):
            image_path = os.path.join(temp_dir, filename)
            preprocess_utils.convert_and_save_image_binary(image_path, output_dir)
    print(".bin files created")



def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--extract_video", type=str)
    parser.add_argument("--drop_frames", type=str)
    parser.add_argument("--rotate_images", type=str)
    parser.add_argument("--rename_files", type=str)
    parser.add_argument("--convert_to_bin", type=str)
    parser.add_argument("--all", type=str)

    args = parser.parse_args()

    if args.all:
        input_video, temp_dir, interval, output_dir = args.all.split(",")
        #input_video = f'"{input_video}"'
        #temp_dir = f'"{temp_dir}"'
        #output_dir = f'"{output_dir}"'
        extract_video(input_video, temp_dir)
        drop_frames(temp_dir, int(interval))
        rotate_images(temp_dir)
        rename_files(temp_dir)
        convert_to_bin(temp_dir, output_dir)
        return

    if args.extract_video:
        input_video, temp_dir = args.extract_video.split(",")
        #input_video = f'"{input_video}"'
        #temp_dir = f'"{temp_dir}"'
        extract_video(input_video, temp_dir)

    if args.drop_frames:
        temp_dir, interval = args.drop_frames.split(",")
        #temp_dir = f'"{temp_dir}"'
        drop_frames(temp_dir, int(interval))

    if args.rotate_images:
        #args.rotate_images = f'"{args.rotate_images}"'
        rotate_images(args.rotate_images)

    if args.rename_files:
        #args.rename_files = f'"{args.rename_files}"'
        rename_files(args.rename_files)

    if args.convert_to_bin:
        temp_dir, output_dir = args.convert_to_bin.split(",")
        #temp_dir = f'"{temp_dir}"'
        #output_dir = f'"{output_dir}"'
        convert_to_bin(temp_dir, output_dir)

if __name__ == "__main__":
    print("Running...")
    main()
