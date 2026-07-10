# Update heading colors in stylesheet
$path = "D:\TRAINPULSE\static\style.css"
$content = Get-Content $path -Raw
$content = $content -replace 'color: #ffc9c9;', 'color: #c9213a;'
$content = $content -replace 'color: #ffffff;', 'color: #c9213a;'
Set-Content $path $content -Encoding UTF8
Write-Host "✓ Headings updated to #c9213a"
