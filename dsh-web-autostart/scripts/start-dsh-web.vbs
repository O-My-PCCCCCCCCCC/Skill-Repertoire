' DSH Web 隐藏启动器 — 保持与 start-dsh.bat 同一目录
' 用 wscript 运行（GUI 程序，永不弹控制台窗口），隐藏调用 bat
Set fso = CreateObject("Scripting.FileSystemObject")
Set sh = CreateObject("WScript.Shell")
batPath = fso.GetParentFolderName(WScript.ScriptFullName) & "\start-dsh.bat"
sh.Run "cmd /c """ & batPath & """", 0, False
