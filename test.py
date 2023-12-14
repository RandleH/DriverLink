


# from drive import MyDrive



class Test:
    def __init__(self) -> None:
        pass



def main():
    print("[ERROR]:Timeout!")
    ans = input("Reconnect? [Y/N] ")
    if(ans=="Y" or ans=="y"):
        print("Reconnecting...")
    else:
        exit(9)



if __name__=="__main__":
    main()