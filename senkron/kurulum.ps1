# İrisya: masaüstündeki İrisya klasörünü GitHub deposuyla otomatik eşitlenen bir kopyaya çevirir.
# Bir kez çalıştırılır. PowerShell'e şunu yapıştırın:
#   iex ((irm https://raw.githubusercontent.com/sametdemirwork/irisya/main/senkron/kurulum.ps1).TrimStart([char]0xFEFF))
#
# Yaptıkları:
#   1. Git yüklü mü bakar.
#   2. Masaüstündeki İrisya klasörü bu deponun kopyası değilse, onu "İrisya-yedek-<tarih>" adıyla
#      saklar (hiçbir şey silinmez) ve depoyu aynı yere indirir (main dalı).
#   3. GitHub girişini bir kez ister (Git Credential Manager penceresi).
#   4. "Irisya GitHub Senkron" adında, oturum açıkken her dakika çalışan gizli bir görev kurar.
# Kaldırmak için: senkron\kaldir.ps1

$ErrorActionPreference = 'Continue'   # git yazdığı uyarılar kurulumu kesmesin; hatalar aşağıda tek tek kontrol ediliyor
$RepoUrl = 'https://github.com/sametdemirwork/irisya.git'
$TaskName = 'Irisya GitHub Senkron'
$FolderName = [string][char]0x130 + 'risya'   # "İrisya" (kodlama sorunlarına karşı harf koduyla)
$Target = Join-Path ([Environment]::GetFolderPath('Desktop')) $FolderName

function Say([string]$m, [string]$color = 'Cyan') { Write-Host $m -ForegroundColor $color }

# 1. Git
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Say 'Git yüklü değil. Önce şunu çalıştırın, sonra PowerShell penceresini kapatıp açın ve kurulumu tekrarlayın:' 'Yellow'
    Say '  winget install --id Git.Git -e' 'Yellow'
    return
}

# 2. Klasör
$isClone = $false
if (Test-Path (Join-Path $Target '.git')) {
    $origin = (& git -C $Target remote get-url origin 2>$null)
    $isClone = $origin -match 'sametdemirwork/irisya'
}
if (-not $isClone) {
    if (Test-Path $Target) {
        $backup = '{0}-yedek-{1:yyyyMMdd-HHmm}' -f $Target, (Get-Date)
        Rename-Item -Path $Target -NewName (Split-Path $backup -Leaf) -ErrorAction Stop
        Say "Eski klasör saklandı: $backup"
    }
    Say 'Depo GitHub''dan indiriliyor...'
    & git clone --branch main $RepoUrl $Target
    if ($LASTEXITCODE -ne 0) { throw 'git clone başarısız.' }
} else {
    Say "Klasör zaten deponun kopyası: $Target"
}

# Commit'lerde görünecek isim/e-posta: bilgisayarda ayarlı değilse depodaki son commit'inkini kullan
if (-not (& git -C $Target config user.name)) {
    & git -C $Target config user.name ((& git -C $Target log -1 --format=%an).Trim())
}
if (-not (& git -C $Target config user.email)) {
    & git -C $Target config user.email ((& git -C $Target log -1 --format=%ae).Trim())
}

# 3. GitHub girişi (gerekirse tarayıcı/pencere açılır, bir kez)
Say 'GitHub erişimi kontrol ediliyor (giriş penceresi açılırsa giriş yapın)...'
& git -C $Target push --dry-run origin HEAD
if ($LASTEXITCODE -ne 0) { Say 'GitHub''a gönderme izni alınamadı. Giriş yaptıktan sonra kurulumu tekrar çalıştırın.' 'Yellow'; return }

# 4. Zamanlanmış görev (pencere açmadan, her dakika)
$vbs = Join-Path $Target 'senkron\senkron-gizli.vbs'
$action = New-ScheduledTaskAction -Execute 'wscript.exe' -Argument "`"$vbs`""
$every = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 1)
$logon = New-ScheduledTaskTrigger -AtLogOn -User "$env:USERDOMAIN\$env:USERNAME"
$logon.Repetition = $every.Repetition   # oturum açılınca da her dakika tekrar etsin
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable `
    -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 10)
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger @($every, $logon) -Settings $settings `
    -Principal $principal -Force -ErrorAction Stop | Out-Null

# İlk tur hemen
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $Target 'senkron\senkron.ps1')

Say ''
Say "Hazır. $Target artık GitHub'daki main dalıyla her dakika eşitleniyor." 'Green'
Say 'Kayıt dosyası: senkron.log  |  Durdurmak için: senkron\kaldir.ps1' 'Green'
