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

    WaitUntilSafariWindowHasLoaded()

    tell application "Safari"
        do JavaScript "browser.submit()" in document 1
    end tell

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
    -- tell application "Safari" to set the URL of the front document to "https://carelink.minimed.com/patient/main/reports.do"
    tell application "Safari" to set the URL of the front document to "https://carelink.minimed.com/patient/main/proReports.do"

    WaitUntilSafariWindowHasLoaded()

    tell application "Safari"
        do JavaScript "document.getElementById('periodButton0').click()" in document 1
        do JavaScript "document.getElementsByName('daterangepicker_start')[0].value = '" & item 1 of argv & "';" in document 1
        do JavaScript "document.getElementsByName('daterangepicker_end')[0].value = '"   & item 2 of argv & "';" in document 1
        do JavaScript "document.getElementsByClassName('applyBtn btn btn-sm periodButton')[0].click()" in document 1
        do JavaScript "document.getElementById('reportNav_button1').click()" in document 1
    end tell
    -- you can check in the consule that these are correctly set.

    WaitUntilSafariWindowHasLoaded()
    delay 10

    tell application "Safari"
        quit
    end tell

    do shell script "echo " & output

end run
