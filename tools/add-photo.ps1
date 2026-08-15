<#
.SYNOPSIS
  Add or replace a person photo on the Singla Lab site.

.DESCRIPTION
  Centre-crops the source image to a square (biased toward the top, where faces
  usually sit), resizes it to 480x480 and writes it as a JPEG into
  assets/img/people/<slug>.jpg. Uses only .NET imaging — nothing to install.

.EXAMPLE
  .\tools\add-photo.ps1 -Source "C:\photos\Ravi.jpg" -Slug ravi-kumar

  Then reference it from _data/people.json:
      { "name": "Ravi Kumar", "role": "Ph.D. Student", "photo": "ravi-kumar" }
  and rebuild:
      python build.py
#>
param(
    [Parameter(Mandatory = $true)][string] $Source,
    [Parameter(Mandatory = $true)][string] $Slug,
    [int]    $Size    = 480,
    [int]    $Quality = 84,
    [double] $TopBias = 0.18   # 0 = crop from the very top, 0.5 = dead centre
)

Add-Type -AssemblyName System.Drawing

$repo = Split-Path -Parent $PSScriptRoot
$dest = Join-Path $repo "assets\img\people\$Slug.jpg"

if (-not (Test-Path -LiteralPath $Source)) { throw "Source image not found: $Source" }
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $dest) | Out-Null

$img  = [System.Drawing.Image]::FromFile((Resolve-Path -LiteralPath $Source))
$side = [Math]::Min($img.Width, $img.Height)
$sx   = [int](($img.Width  - $side) / 2)
$sy   = [int](($img.Height - $side) * $TopBias)

$bmp = New-Object System.Drawing.Bitmap($Size, $Size)
$bmp.SetResolution(96, 96)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CompositingQuality = [System.Drawing.Drawing2D.CompositingQuality]::HighQuality
$g.InterpolationMode  = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$g.SmoothingMode      = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
$g.PixelOffsetMode    = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
$g.Clear([System.Drawing.Color]::White)
$g.DrawImage($img,
    (New-Object System.Drawing.Rectangle(0, 0, $Size, $Size)),
    (New-Object System.Drawing.Rectangle($sx, $sy, $side, $side)),
    [System.Drawing.GraphicsUnit]::Pixel)

$codec = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq 'image/jpeg' }
$ep = New-Object System.Drawing.Imaging.EncoderParameters(1)
$ep.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter([System.Drawing.Imaging.Encoder]::Quality, [int]$Quality)
$bmp.Save($dest, $codec, $ep)

$ep.Dispose(); $g.Dispose(); $bmp.Dispose(); $img.Dispose()

Write-Output ("Wrote {0} ({1:N0} KB)" -f $dest, ((Get-Item $dest).Length / 1KB))
Write-Output ('Now add  "photo": "{0}"  to that person''s entry in _data/, then run: python build.py' -f $Slug)
