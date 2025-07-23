Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Get the current directory
currentDir = fso.GetAbsolutePathName(".")

' Create the shortcut
Set oShellLink = WshShell.CreateShortcut(WshShell.SpecialFolders("Desktop") & "\XENOscribe.lnk")

' Set shortcut properties
oShellLink.TargetPath = currentDir & "\run.bat"
oShellLink.WorkingDirectory = currentDir
oShellLink.Description = "XENOscribe by Xenovative - AI Transcription Tool"

' Try to use .ico file first, then fallback to .png
If fso.FileExists(currentDir & "\assets\favicon.ico") Then
    oShellLink.IconLocation = currentDir & "\assets\favicon.ico"
ElseIf fso.FileExists(currentDir & "\assets\xeno.png") Then
    oShellLink.IconLocation = currentDir & "\assets\xeno.png"
End If

' Save the shortcut
oShellLink.Save

WScript.Echo "Desktop shortcut created successfully!"
