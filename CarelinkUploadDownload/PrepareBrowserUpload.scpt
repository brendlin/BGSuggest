#!/usr/bin/osascript

tell application "Safari" to open location "https://carelink.minimed.com"

delay 5

set newFile to ((path to me as text) & "::noupload.txt")
set theFileContents to paragraph 1 of (read file newFile)

tell application "Safari"
    do JavaScript "document.getElementById('j_username').value = 'kurtbrendlinger';" in document 1
    do JavaScript "document.getElementById('j_password').value = '" & theFileContents & "';" in document 1
    do JavaScript "document.getElementById('loginButton').click();" in document 1
end tell

delay 5

-- tell application "Safari" to open location "https://carelink.minimed.com/patient/main/reports.do"
tell application "Safari" to set the URL of the front document to "https://carelink.minimed.com/patient/main/deviceUpload.do"

delay 20

set theDialogText to "Please let me initiate a Carelink Upload."
display dialog theDialogText

