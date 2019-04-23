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

-- Clear all the windows.
tell application "Safari"
    close every window
end tell

delay 3

tell application "Safari" to open location "https://carelink.minimed.com"

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

-- this is the new button
tell application "Safari"
     do JavaScript "document.getElementById('data_upload_from_uploader').click()" in document 1
end tell

-- gotta wait for the iframe to appear
delay 1

-- Here is where we get the token name
tell application "Safari"
     set myVar to do JavaScript "document.getElementsByTagName('iframe')[0].src" in document 1
     return myVar
end tell
