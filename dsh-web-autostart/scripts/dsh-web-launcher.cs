// DSH Web 桌面启动器源码（可选）。
// 编译成 exe 后，桌面快捷方式直接指向它，无黑窗打开默认浏览器。
// 编译（Windows 自带 .NET Framework 编译器）：
//   C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe /nologo /target:winexe ^
//     /win32icon:你的图标.ico /out:dsh-web-launcher.exe dsh-web-launcher.cs
using System;
using System.Diagnostics;

class DshWebLauncher
{
    [STAThread]
    static void Main()
    {
        try
        {
            // 端口按实际配置修改（默认规范端口 10101）
            Process.Start("http://127.0.0.1:10101");
        }
        catch
        {
        }
    }
}
