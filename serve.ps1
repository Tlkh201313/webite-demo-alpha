# Local preview server for Cursor Browser (http only — file:// is blocked)
$Port = if ($args[0]) { [int]$args[0] } else { 8080 }
$Root = $PSScriptRoot
Set-Location $Root
Write-Host "Serving $Root at http://127.0.0.1:$Port/"
Write-Host "  Home:       http://127.0.0.1:$Port/main.html"
Write-Host "  About Us:   http://127.0.0.1:$Port/about/about-us.html"
Write-Host "Press Ctrl+C to stop."
python -m http.server $Port
