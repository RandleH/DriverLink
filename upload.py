

import sys
from drive import MyDrive



def usage():
    print("USAGE:")
    print("> python upload.py <local file path> <google drive path>")
    print("> python upload.py <local file path> <google drive path> [-a include hidden files]")
    print("\n\n")
    exit(1)


def main():
    if(len(sys.argv)<3):
        usage()

    FLAG__ignore_hidden_file = True

    if "-a" in sys.argv:
        FLAG__ignore_hidden_file = False
        sys.argv.remove("-a")

    drv = MyDrive()
    drv.upload( sys.argv[1], sys.argv[2], FLAG__ignore_hidden_file)



if __name__=="__main__":
    main()