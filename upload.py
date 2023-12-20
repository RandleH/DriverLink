

import sys
from drive import MyDrive
import argparse


def usage():
    print("USAGE:")
    print("> python upload.py --local <local file path> --drive <google drive path> [-jpg] [--rename_folder <name>] [-a]")
    print("\n\n")
    exit(1)

parser = argparse.ArgumentParser()
parser.add_argument("-jpg", "--jpg_only", action='store_const', default=False, const=True)
parser.add_argument("-a", "--all", action='store_const', default=False, const=True)
parser.add_argument("--local", type=str, help="Your local directory", default="")
parser.add_argument("--drive", type=str, help="Your Google Drive directory", default="")
parser.add_argument("--rename_folder", type=str, help="The destination folder name on Google Drive", default="")
(params, unknown_args) = parser.parse_known_args()


def main():
    if not params.local or not params.drive:
        usage()

    drv = MyDrive(params)
    drv.upload()



if __name__=="__main__":
    main()