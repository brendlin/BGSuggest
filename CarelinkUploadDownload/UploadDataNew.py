#!/usr/bin/python

import os
import sys
import time
import Quartz.CoreGraphics
import time

def UploadDataNew() :

    # Prepare the browser, and then ask the user if he's ready for an upload.
    if os.system('''osascript GetUploadToken.scpt >& token.txt''') :
        print 'Okay. Not uploading.'
        return False

    # Quit
    time.sleep(1)
    os.system('''/usr/bin/osascript -e 'tell application "Safari" \n quit \n end tell' ''')

    token = open('token.txt').readlines()[0].replace('\n','')
    cmd = 'cd /Library/Application\ Support/Medtronic/CareLink/Uploader/DSS'
    cmd += ' && jre/bin/java -jar uploader.jar '
    cmd += token
    os.system(cmd)

    # Notify user that we are done.
    os.system('''/usr/bin/osascript -e 'display notification "Probably ready to go."' ''')

    return True

if __name__ == "__main__":
    UploadDataNew()
