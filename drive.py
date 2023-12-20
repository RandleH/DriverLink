from pydrive.drive import GoogleDrive 
from pydrive.auth import GoogleAuth 

from pydrive.auth import AuthenticationRejected

from googleapiclient.errors import HttpError

import shutil
import os
import httplib2
import argparse


NO_ERROR   = 0
ERR_SOLVED = 1
ERR_FATAL  = 2
ERR_SKIP   = 3


# https://console.developers.google.com/apis/credentials


class MyDrive:
    global NO_ERROR,ERR_SOLVED,ERR_FATAL,ERR_SKIP

    def __init__(self, params, offline=False) -> None:
        self.user_params = params
        self.logger = print
        self.cache_id = dict()
        self.offline = offline
        
        # don't start path with '/', as this causes it to look relative to the root folder    
        client_json_path = os.path.join( os.getcwd(), "client_secrets.json")
        GoogleAuth.DEFAULT_SETTINGS['client_config_file'] = client_json_path
        # Below code does the authentication 
        # part of the code 
        self.gauth = GoogleAuth()

        if(offline==False):
            self.reconnect()

        # Creates local webserver and auto 
        # handles authentication. 
        self.drive = GoogleDrive(self.gauth)
        pass
    
    def _string_verdict(self, word):
        if( "~" not in word):
            # self.logger("Please use \"~\" as the root path")
            return 1
        return 0
    
    def _string_split(self, word):
        return os.path.split( self._string_expand(word))
    
    def _string_expand(self, word):
        return word.replace( "~", "root")
    
    def reconnect(self):
        try:
            self.gauth.LoadCredentialsFile(os.path.join( os.getcwd(), "temp_creds.txt"))
            if self.gauth.credentials is None:
                self.gauth.LocalWebserverAuth()
            elif self.gauth.access_token_expired:
                self.gauth.Refresh()
            else:
                self.gauth.Authorize()

            # Save the current credentials to a file
            self.gauth.SaveCredentialsFile("temp_creds.txt")

        except AuthenticationRejected as error:
            self.logger(f"An error occurred: {error}")


    def create_folder( self, f_drv_path_name:str, skip_check=False):
        self._string_verdict(f_drv_path_name)
        f_drv_path, f_drv_name = self._string_split(f_drv_path_name)

        f_drv_id = self.path_id(f_drv_path)
        assert f_drv_id!=None
        
        f_metadata = {
            'title': f_drv_name,
            'parents': [{'id': f_drv_id}],
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        try:
            if( (skip_check==True) or (False==self.is_folder_exist( f_drv_path_name))):
                folder = self.drive.CreateFile(f_metadata)
                folder.Upload()
                return 0
            return 1
        
        except HttpError as error:
            self.logger(f"An error occurred: {error}")
        

    def is_folder_exist( self, f_drv_path_name:str):
        self._string_verdict(f_drv_path_name)
        self._string_expand(f_drv_path_name)
        return self.path_id(f_drv_path_name)!=None
    
    def __upload__(self, f_local_path, f_drv_path):
        errorCode = NO_ERROR
        try:
            self.create_folder(f_drv_path)
            
            if( True==os.path.isfile(f_local_path) ):
                if(self.user_params.all!=True and True==os.path.basename(f_local_path).startswith('.')):
                    return
                elif self.user_params.jpg_only==True and not (f_local_path.endswith(".jpg") or f_local_path.endswith(".JPG") or f_local_path.endswith(".JPEG") or f_local_path.endswith(".jpeg")):
                    return

                self.logger( f"Uploading from {f_local_path} to {f_drv_path}")
                
                f_drv_id = self.path_id(f_drv_path)
                assert f_drv_id!=None

                f_metadata = {
                    'title': os.path.basename(f_local_path),
                    'parents':[{"id":f_drv_id}]
                }

                f = self.drive.CreateFile(f_metadata)
                f.SetContentFile(f_local_path)
                f.Upload()
            else:
                f_drv_path_next   = os.path.join(f_drv_path, os.path.basename(f_local_path))
                for item in os.listdir(f_local_path):
                    f_local_path_next = os.path.join(f_local_path, item)
                    self.__upload__( f_local_path_next, f_drv_path_next)

        except TimeoutError:
            print("[ERROR]:Timeout!")
            ans = input("Reconnect? [Y/N] ")
            if(ans=="Y" or ans=="y"):
                self.logger("Reconnecting...")
                self.reconnect()
                errorCode = ERR_SOLVED
            else:
                errorCode = ERR_FATAL

        # except httplib2.error.RedirectMissingLocation:
        except Exception as e:
            print("[ERROR]:Upload failed! [Reason]={}".format(e))
            ans = input("Retry? [Y/N] ")
            if(ans=="Y" or ans=="y"):
                errorCode = ERR_SOLVED
            else:
                errorCode = ERR_SKIP
            
        finally:
            if(errorCode==ERR_SOLVED):
                self.__upload__(f_local_path, f_drv_path)
            elif(errorCode==ERR_SKIP):
                return
            elif(errorCode==ERR_FATAL):
                exit(9)


    def upload( self):
        f_local_path = os.path.expanduser(self.user_params.local)
        if self.user_params.rename_folder:
            f_drv_path   = os.path.join( self._string_expand(self.user_params.drive), self.user_params.rename_folder)
            for item in os.listdir(f_local_path):
                f_local_path_next = os.path.join(f_local_path, item)
                self.__upload__( f_local_path_next, f_drv_path)
        else:
            f_drv_path   = self._string_expand(self.user_params.drive)
            self.__upload__(f_local_path, f_drv_path)


    def path_id(self, f_drv_path:str):
        
        def path_id_recursive( self, f_drv_path:str, id):
            tmp = f_drv_path.split("/", 1)
            stupid = f"\'{id}\' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
            file_list = self.drive.ListFile({'q': stupid}).GetList()
            for file in file_list:
                if(file['title'] == tmp[0]):
                    if(len(tmp)==1):
                        return file['id']
                    else:
                        return path_id_recursive(self, tmp[1], file['id'])
            return None
        
        # Standardize the path format
        f_drv_path = self._string_expand(f_drv_path)

        if(f_drv_path in self.cache_id.keys()):
            return self.cache_id[f_drv_path]

        # Get the first root name
        tmp = f_drv_path.split("/", 1)

        assert tmp[0]=='root' , "Path MUST begin with \'root\'"
        if(len(tmp)==1):
            return 'root'
        
        f_drv_id = path_id_recursive( self, tmp[1], 'root')
        if(f_drv_id):
            self.cache_id[f_drv_path] = f_drv_id

        return f_drv_id
    

    def test(self):
        assert "1m6bCbq1J7hGtbUZjKCU2PhrKJrY-3bNC"==self.path_id(r"~/WiFi-Localization/Week01")
        assert "1EIh4Y4hQqIcRuJce4lnOSDf4LSF2whJE"==self.path_id(r"~/WiFi-Localization/Week02")
        assert "1PCo4S2t-ey8r55h1688UdcVbmqS-yPd_"==self.path_id(r"~/WiFi-Localization/Week03")
        assert "1quxHHAa0IRJ2izytW0eZEmpLGYfBsZNg"==self.path_id(r"~/WiFi-Localization/Week04")
        assert "1BmYokIjVLXszXTRjR8Bz8UaEasilHO4e"==self.path_id(r"~/WiFi-Localization/Week05")
        self.logger("Passed.")

    def move(self, f_local_src_path, f_local_dst_path, ignore_hidden_file=True):
        errorCode    = NO_ERROR

        f_local_dst_path = os.path.expanduser(f_local_dst_path)
        f_local_src_path = os.path.expanduser(f_local_src_path)

        try:

        # if(True):
            if(False==os.path.exists(f_local_dst_path)):
                os.mkdir(f_local_dst_path)

            if(ignore_hidden_file==True and True==os.path.basename(f_local_src_path).startswith('.')):
                return

            if( True==os.path.isfile(f_local_src_path) ):
                shutil.copy(f_local_src_path, os.path.join(f_local_dst_path, os.path.basename(f_local_src_path)))
            else:
                f_local_dst_path_next = os.path.join(f_local_dst_path, os.path.basename(f_local_src_path))
                for item in os.listdir(f_local_src_path):
                    f_local_src_path_next = os.path.join(f_local_src_path, item)    
                    self.move(f_local_src_path_next, f_local_dst_path_next)

        except IOError as e:
            print(f"[ERROR]:Upload failed! Signature: {e}")
            ans = input("Retry? [Y/N] ")
            if(ans=="Y" or ans=="y"):
                errorCode = ERR_SOLVED
            else:
                errorCode = ERR_SKIP

        finally:
            if(errorCode==ERR_SOLVED):
                self.move( f_local_src_path, f_local_dst_path, ignore_hidden_file)
            elif(errorCode==ERR_SKIP):
                return
            elif(errorCode==ERR_FATAL):
                exit(9)
            

def main():
    drv = MyDrive()
    drv.test()
    



if __name__=="__main__":
    main()

    