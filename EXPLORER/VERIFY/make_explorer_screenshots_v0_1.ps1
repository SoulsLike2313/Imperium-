Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$RunId = "RUN-" + (Get-Date -Format "yyyyMMdd-HHmmss")
$ShotRoot = "E:\IMPERIUM\EXPLORER\SCREENSHOTS\$RunId"

New-Item -ItemType Directory -Force -Path $ShotRoot | Out-Null

function Take-FullscreenShot {
    param(
        [string]$Name
    )

    $bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
    $bitmap = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)

    $graphics.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size)

    $path = Join-Path $ShotRoot $Name
    $bitmap.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)

    $graphics.Dispose()
    $bitmap.Dispose()

    Write-Host "Saved screenshot: $path"
}

Write-Host ""
Write-Host "IMPERIUM Explorer screenshot collector"
Write-Host "Run folder: $ShotRoot"
Write-Host ""

Write-Host "Starting Explorer v0.4..."
Start-Process -FilePath "python" -ArgumentList "E:\IMPERIUM\EXPLORER\imperium_explorer_v0_4.py"

Start-Sleep -Seconds 4

Write-Host ""
Write-Host "1) Оставь Explorer открытым на стартовом виде."
Read-Host "Нажми Enter для screenshot_01_start"
Take-FullscreenShot "screenshot_01_start.png"

Write-Host ""
Write-Host "2) В Explorer кликни E:\IMPERIUM или верхний root."
Read-Host "Нажми Enter для screenshot_02_root"
Take-FullscreenShot "screenshot_02_root.png"

Write-Host ""
Write-Host "3) Кликни E:\IMPERIUM\ARTIFACTS."
Read-Host "Нажми Enter для screenshot_03_artifacts"
Take-FullscreenShot "screenshot_03_artifacts.png"

Write-Host ""
Write-Host "4) Кликни E:\IMPERIUM\ARTIFACTS\_MANUAL_PROOFS."
Read-Host "Нажми Enter для screenshot_04_manual_proofs"
Take-FullscreenShot "screenshot_04_manual_proofs.png"

Write-Host ""
Write-Host "5) Кликни E:\IMPERIUM\EXPLORER\imperium_explorer_v0_4.py."
Read-Host "Нажми Enter для screenshot_05_explorer_v0_4"
Take-FullscreenShot "screenshot_05_explorer_v0_4.png"

Write-Host ""
Write-Host "6) Кликни E:\IMPERIUM\ARCHIVE. Важно: только верх, без захода глубоко."
Read-Host "Нажми Enter для screenshot_06_archive_top"
Take-FullscreenShot "screenshot_06_archive_top.png"

$ManifestPath = Join-Path $ShotRoot "SCREENSHOT_MANIFEST.txt"

Get-ChildItem $ShotRoot -Filter "*.png" | ForEach-Object {
    "$($_.Name)`t$($_.FullName)"
} | Set-Content -Path $ManifestPath -Encoding UTF8

Write-Host ""
Write-Host "DONE."
Write-Host "Screenshots folder:"
Write-Host $ShotRoot
Write-Host "Manifest:"
Write-Host $ManifestPath
