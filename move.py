

import sys
from drive import MyDrive



def usage():
    print("USAGE:")
    print("> python move.py <local dst file path> <local src file path>")
    print("> python move.py <local dst file path> <local src file path> [-a include hidden files]")
    print("\n\n")
    exit(1)


def main():
    if(len(sys.argv)<3):
        usage()

    FLAG__ignore_hidden_file = True

    if "-a" in sys.argv:
        FLAG__ignore_hidden_file = False
        sys.argv.remove("-a")

    drv = MyDrive(offline=True)
    drv.move(sys.argv[1], sys.argv[2], FLAG__ignore_hidden_file)


if __name__=="__main__":
    main()