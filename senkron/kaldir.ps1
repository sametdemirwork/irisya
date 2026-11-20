# İrisya otomatik eşitlemeyi kapatır. Klasöre ve dosyalara dokunmaz.
Unregister-ScheduledTask -TaskName 'Irisya GitHub Senkron' -Confirm:$false -ErrorAction SilentlyContinue
Write-Host 'Otomatik eşitleme kapatıldı. Klasör olduğu gibi duruyor.' -ForegroundColor Green
