#!/usr/bin/python

import os
import sys
import time
import Quartz.CoreGraphics
import time

def mouseEvent(type, posx, posy,pid=''):
    theEvent = Quartz.CoreGraphics.CGEventCreateMouseEvent(None, type, (posx,posy), Quartz.CoreGraphics.kCGMouseButtonLeft)
    if pid :
        # This will fail.
        Quartz.CGEventPostToPid(pid, theEvent)
    else :
        Quartz.CoreGraphics.CGEventPost(Quartz.CoreGraphics.kCGHIDEventTap, theEvent)

def mousemove(posx,posy,pid=''):
    mouseEvent(Quartz.CoreGraphics.kCGEventMouseMoved, posx,posy,pid);

def mouseclick(posx,posy,pid=''):
    mouseEvent(Quartz.CoreGraphics.kCGEventLeftMouseDown, posx,posy,pid);
    time.sleep(0.1)
    mouseEvent(Quartz.CoreGraphics.kCGEventLeftMouseUp, posx,posy,pid);

def UploadData() :

    ourEvent = Quartz.CoreGraphics.CGEventCreate(None);
    currentpos = Quartz.CoreGraphics.CGEventGetLocation(ourEvent); # Save current mouse position

    # Prepare the browser, and then ask the user if he's ready for an upload.
    if os.system('''osascript PrepareBrowserUpload.scpt''') :
        # print 'Okay. Not uploading.'
        return False

    # Do the quick clicks!
    os.system('''/usr/bin/osascript -e 'tell application "Safari" to activate' ''')
    time.sleep(0.1)
    for i in range(5) :
        mouseclick(500,605)
    mouseclick(570,605)

    # Move everything back in place.
    os.system('''/usr/bin/osascript -e 'tell application "System Events" to keystroke tab using command down' ''')
    mousemove(int(currentpos.x),int(currentpos.y)); # Restore mouse position

    # Wait. Hard to get around this.
    time.sleep(180)

    # Quit; notify user that we are done.
    os.system('''/usr/bin/osascript -e 'tell application "Safari" \n quit \n end tell' ''')
#     os.system('''/usr/bin/osascript -e 'display notification "New data (probably) uploaded."' ''')

    return True

if __name__ == "__main__":
    UploadData()
