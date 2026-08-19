# dsh-mode-status 一键安装脚本
# 1) 复制插件到 C:\Users\Administrator\DSH-Plugin\dsh-mode-status
# 2) 注册 ~/.dsh/profiles/web/package.json（依赖 + bundles）
# 3) profile 目录 pnpm install
# 4) 提示重启 DSH Web
$ErrorActionPreference = 'Stop'

$pluginDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$src = Join-Path $pluginDir 'plugin'
$dst = 'C:\Users\Administrator\DSH-Plugin\dsh-mode-status'
$profilePkg = "$env:USERPROFILE\.dsh\profiles\web\package.json"
$pnpm = 'C:\Users\Administrator\.dsh-runtime\node\pnpm.ps1'

Write-Host '==> 1/3 复制插件' -ForegroundColor Cyan
if (Test-Path $dst) {
    Write-Host "  目标已存在: $dst（先删除旧版）" -ForegroundColor Yellow
    Remove-Item $dst -Recurse -Force
}
New-Item -ItemType Directory -Path $dst -Force | Out-Null
Copy-Item "$src\*" $dst -Recurse -Force
Write-Host "  已复制到 $dst"

Write-Host '==> 2/3 注册 profile' -ForegroundColor Cyan
$pkg = Get-Content $profilePkg -Raw | ConvertFrom-Json
if (-not ($pkg.dependencies.'@dsh-external/dsh-client-ui-mode-status')) {
    $pkg.dependencies | Add-Member -NotePropertyName '@dsh-external/dsh-client-ui-mode-status' -NotePropertyValue 'link:C:/Users/Administrator/DSH-Plugin/dsh-mode-status'
}
if ($pkg.dsh.profile.bundles -notcontains '@dsh-external/dsh-client-ui-mode-status') {
    $pkg.dsh.profile.bundles = @($pkg.dsh.profile.bundles + '@dsh-external/dsh-client-ui-mode-status')
}
$pkg | ConvertTo-Json -Depth 8 | Set-Content $profilePkg -Encoding UTF8
Write-Host '  package.json 已更新'

Write-Host '==> 3/3 pnpm install' -ForegroundColor Cyan
Push-Location "$env:USERPROFILE\.dsh\profiles\web"
if (Test-Path $pnpm) { & $pnpm install --no-frozen-lockfile }
else { & pnpm install --no-frozen-lockfile }
Pop-Location

Write-Host ''
Write-Host '安装完成！下一步：' -ForegroundColor Green
Write-Host '  运行: powershell -ExecutionPolicy Bypass -File restart-dsh-web.ps1'
Write-Host '  然后刷新浏览器页面，侧栏底部即出现模式状态点。'
