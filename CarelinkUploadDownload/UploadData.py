#!/usr/bin/python

import os
import sys
import time
import Quartz.CoreGraphics
import time

def mouseEvent(type, posx, posy,pid=''):
    theEvent = CGEventCreateMouseEvent(None, type, (posx,posy), kCGMouseButtonLeft)
    if pid :
        # This will fail.
        Quartz.CGEventPostToPid(pid, theEvent)
    else :
        Quartz.CoreGraphics.CGEventPost(kCGHIDEventTap, theEvent)

def mousemove(posx,posy,pid=''):
    mouseEvent(kCGEventMouseMoved, posx,posy,pid);

def mouseclick(posx,posy,pid=''):
    mouseEvent(kCGEventLeftMouseDown, posx,posy,pid);
    time.sleep(0.1)
    mouseEvent(kCGEventLeftMouseUp, posx,posy,pid);

ourEvent = CGEventCreate(None);
currentpos = CGEventGetLocation(ourEvent); # Save current mouse position

# Prepare the browser, and then ask the user if he's ready for an upload.
if os.system('''osascript PrepareBrowserUpload.scpt''') :
    print 'Okay. Not uploading.'
    sys.exit()

# Do the quick clicks!
os.system('''/usr/bin/osascript -e 'tell application "Safari" to activate' ''')
time.sleep(0.1)
for i in range(5) :
    mouseclick(500,620)
mouseclick(570,620)

# Move everything back in place.
os.system('''/usr/bin/osascript -e 'tell application "System Events" to keystroke tab using command down' ''')
mousemove(int(currentpos.x),int(currentpos.y)); # Restore mouse position

# Quit; notify user that we are done.
time.sleep(720)
os.system('''/usr/bin/osascript -e 'tell application "Safari" \n quit \n end tell" ''')
os.system('''/usr/bin/osascript -e 'display notification "You have an updated BG thingy."' ''')

print 'finished.'
