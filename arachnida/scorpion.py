#!/usr/bin/env python3

import argparse, os, datetime
from PIL import Image
from PIL.ExifTags import TAGS

def get_args():
    parser = argparse.ArgumentParser(description="Scorpion script print metadatas of pictures on the console")
    parser.add_argument("files", help="File(s) to handle", nargs="+")
    args = parser.parse_args()
    return args

def check_valid_files(args):
    valid_ext = (".jpg", ".jpeg", ".png", ".gif", ".bmp")
    valid_list = []
    for file in args.files:
        file = os.path.abspath(os.path.expanduser(file))
        if os.path.isfile(file) and file.lower().endswith(valid_ext):
            valid_list.append(file)
        else:
            print(f"❌ File {file} does not exist or bad extension")
    return valid_list

def display_metadata(files):
    for image in files:
        print(f"--- Metadata of image {image}---")
        try:
            img = Image.open(image)
            creation_time = datetime.datetime.fromtimestamp(os.path.getctime(image))
            creation_time = creation_time.strftime("%d-%m-%Y %H:%M:%S")
            print(f"File creation date on system : {creation_time}")
            print(f"Image format : {img.format}")
            print(f"Image size : {img.size}")
            print(f"Image mode : {img.mode}")

            exif_data = img._getexif()
            if exif_data:
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    print(f"{tag:25}: {value}")
            else:
                print("❌ No EXIF data found")
        except Exception as e:
            print(f"Error while reading image {image}")
        print("\n")

def main():
    args = get_args()
    files = check_valid_files(args)
    if not files:
        exit(1)
    display_metadata(files)

if __name__ == "__main__":
    main()