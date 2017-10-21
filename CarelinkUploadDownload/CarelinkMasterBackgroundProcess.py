#!/usr/bin/python

import time
import os
from CheckForUSB import CheckForUSB
import datetime

# configuration
hibernate_hours = 10/(60.*60.)
heartbeat_seconds = 5

last_upload = 0

while True :

    time.sleep(heartbeat_seconds)

    #os.system('''/usr/bin/osascript -e 'display notification "You have an updated BG thingy."' ''')
    
    print time.time() - last_upload
    if time.time() - last_upload > 60*60*hibernate_hours :

        if last_upload == 0 :
            os.system('''/usr/bin/osascript -e 'display notification "First notification."' ''')
        else :
            os.system('''/usr/bin/osascript -e 'display notification "%2.3f hours have passed."' '''%(hibernate_hours))

        # Make sure that the USB is plugged in.
        if not CheckForUSB() :
            # continue without resetting the last_upload time.
            continue

        # Run the upload and the download
        print 'python UploadData.py'
        #os.system('python UploadData.py')

        # Run the download
        today = datetime.date.today()
        monday = today - datetime.timedelta(days=today.weekday())
        today_str = monday.strftime("%m/%d/%Y")
        monday_str = today.strftime("%m/%d/%Y")
        cmd = 'osascript DownloadCSV.scpt %s %s'%(monday_str,today_str)
        print cmd
        #os.system('osascript DownloadCSV.scpt 10/9/2017 10/13/2017')

        # at the end of everything...
        last_upload = time.time()

print 'Exiting.'
