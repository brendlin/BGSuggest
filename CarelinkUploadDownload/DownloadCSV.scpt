#!/usr/bin/osascript

on run argv

    set output to "Running script for the following dates:" & item 1 of argv & " to " & item 2 of argv
    try
        set output to "Running script for the following dates:" & item 1 of argv & " to " & item 2 of argv
    on error
        do shell script "echo " & "Error: missing 2 arguments!"
        error number -128
    end try

    do shell script "echo " & output
    do shell script "echo " & quoted form of output

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
    tell application "Safari" to set the URL of the front document to "https://carelink.minimed.com/patient/main/reports.do"

    delay 5

    tell application "Safari"
        do JavaScript "document.getElementById('startDate11').value = '" & item 1 of argv & "';" in document 1
        do JavaScript "document.getElementById('endDate11').value = '" & item 2 of argv & "';" in document 1
        do JavaScript "document.getElementById('reportPicker11').submit();" in document 1
    end tell
    -- you can check in the consule that these are correctly set.

    delay 20

    tell application "Safari"
        quit
    end tell

    do shell script "echo " & output

end run