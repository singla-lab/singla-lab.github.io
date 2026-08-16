<#
.SYNOPSIS
  Fetch a YouTube thumbnail and store it locally as 16:9.

.DESCRIPTION
  The Recommended page shows video cards. Hot-linking i.ytimg.com would hand
  Google the IP of every reader on page load and break if they ever change the
  URL scheme, so the picture is copied into the repository instead.

  maxresdefault is preferred; when a video has none we fall back to hqdefault,
  which is 480x360 with 45px letterbox bars top and bottom -- those get cropped
  off to recover the real 16:9 frame.

.EXAMPLE
  .\tools\add-thumb.ps1 -VideoId oZ72uTWla5Q
#>
param(
  [Parameter(Mandatory = $true)][string] $VideoId,
  [int] $Width = 640,
  [string] $OutDir = 'assets/img/media/yt'
)

Add-Type -AssemblyName System.Drawing
$ErrorActionPreference = 'Stop'

if (-not (Test-Path $OutDir)) { New-Item -ItemType Directory -Force -Path $OutDir | Out-Null }
$dest = Join-Path $OutDir "$VideoId.jpg"
$tmp  = [System.IO.Path]::GetTempFileName() + '.jpg'

$src = $null
foreach ($name in @('maxresdefault', 'sddefault', 'hqdefault')) {
  try {
    Invoke-WebRequest -Uri "https://i.ytimg.com/vi/$VideoId/$name.jpg" -OutFile $tmp -UseBasicParsing
    # YouTube answers a missing size with a 120x90 grey placeholder, not a 404
    $probe = [System.Drawing.Image]::FromFile($tmp)
    $ok = $probe.Width -ge 320
    $probe.Dispose()
    if ($ok) { $src = $name; break }
  } catch { }
}
if (-not $src) { throw "No usable thumbnail for $VideoId" }

$img = [System.Drawing.Image]::FromFile($tmp)
try {
  # crop to 16:9 about the centre -- this is what strips hqdefault's bars
  $want = $img.Width * 9.0 / 16.0
  if ($img.Height -gt $want + 1) {
    $cropH = [int]$want
    $cropY = [int](($img.Height - $cropH) / 2)
  } else {
    $cropH = $img.Height
    $cropY = 0
  }
  $w = [Math]::Min($Width, $img.Width)
  $h = [int]($w * 9.0 / 16.0)

  $bmp = New-Object System.Drawing.Bitmap($w, $h)
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.InterpolationMode = 'HighQualityBicubic'
  $g.PixelOffsetMode = 'HighQuality'
  $g.SmoothingMode = 'HighQuality'
  $g.DrawImage($img, (New-Object System.Drawing.Rectangle(0, 0, $w, $h)),
                     (New-Object System.Drawing.Rectangle(0, $cropY, $img.Width, $cropH)),
                     [System.Drawing.GraphicsUnit]::Pixel)
  $g.Dispose()

  $codec = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() |
           Where-Object { $_.MimeType -eq 'image/jpeg' }
  $prm = New-Object System.Drawing.Imaging.EncoderParameters(1)
  $prm.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter(
      [System.Drawing.Imaging.Encoder]::Quality, 82)
  $bmp.Save((Resolve-Path -LiteralPath (Split-Path $dest)).Path + '\' + (Split-Path $dest -Leaf), $codec, $prm)
  $bmp.Dispose()
} finally {
  $img.Dispose()
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}

$kb = [int]((Get-Item $dest).Length / 1KB)
Write-Host ("{0}  <- {1}  ({2} KB)" -f $dest, $src, $kb)
