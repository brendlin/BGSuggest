#!/usr/bin/python

import time
import os
from CheckForUSB import CheckForUSB
from DownloadCSVAndMoveIntoPosition import DownloadCSVAndMoveIntoPosition
from UploadData import UploadData
import datetime

# configuration
hibernate_hours = 1
heartbeat_seconds = 5

last_upload = 0

while True :

    time.sleep(heartbeat_seconds)

    # print time.time() - last_upload
    if time.time() - last_upload > float(60*60*hibernate_hours) :

        # Make sure that the USB is plugged in.
        if not CheckForUSB() :
            os.system('''/usr/bin/osascript -e 'display notification "Connect your USB device."' ''')
            # continue without resetting the last_upload time.
            continue

        # Run the upload and the download
        UploadData()

        # Run the download
        today = datetime.date.today()
        today_str = today.strftime("%m/%d/%Y")
        monday = today - datetime.timedelta(days=today.weekday())
        monday_str = monday.strftime("%m/%d/%Y")
        DownloadCSVAndMoveIntoPosition(monday_str,today_str)

        # at the end of everything...
        last_upload = time.time()

print 'Exiting.'
