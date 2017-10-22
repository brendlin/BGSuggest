#!/usr/bin/osascript

on WaitUntilSafariWindowHasLoaded()
    delay 3
    tell application "System Events"
        tell application "Safari"
            set the_state to missing value
            repeat until the_state is "complete"
                set the_state to (do JavaScript "document.readyState" in document 1)
                delay 0.2
            end repeat
        end tell
    end tell
end WaitUntilSafariWindowHasLoaded

tell application "Safari" to open location "https://carelink.minimed.com"

WaitUntilSafariWindowHasLoaded()

set newFile to ((path to me as text) & "::noupload.txt")
set theFileContents to paragraph 1 of (read file newFile)

tell application "Safari"
    do JavaScript "document.getElementById('j_username').value = 'kurtbrendlinger';" in document 1
    do JavaScript "document.getElementById('j_password').value = '" & theFileContents & "';" in document 1
    do JavaScript "document.getElementById('loginButton').click();" in document 1
end tell

WaitUntilSafariWindowHasLoaded()

-- tell application "Safari" to open location "https://carelink.minimed.com/patient/main/reports.do"
tell application "Safari" to set the URL of the front document to "https://carelink.minimed.com/patient/main/deviceUpload.do"

-- Hard to get around this.
delay 20

set theDialogText to "Please let me initiate a Carelink Upload."
display dialog theDialogText

set empty to ""

