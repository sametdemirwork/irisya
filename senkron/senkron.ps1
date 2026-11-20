# İrisya: yerel klasör <-> GitHub otomatik eşitleme (tek tur).
# Görev Zamanlayıcı bunu her dakika arka planda çalıştırır (kurulum.ps1 kurar).
#
# Bir turda:
#   1. Yerel değişiklik varsa hepsini commit'ler.
#   2. GitHub'daki yenilikleri çeker (git pull --rebase).
#   3. Yerel commit'leri GitHub'a gönderir (git push).
# İki tarafta aynı satır değiştiyse (çakışma) hiçbir şeyi bozmadan durur,
# masaüstüne IRISYA-SENKRON-SORUN.txt yazar ve sorun çözülene kadar beklemede kalır.
# Kayıt: depo kökündeki senkron.log (git'e girmez).

$ErrorActionPreference = 'Continue'
$repo = Split-Path -Parent $PSScriptRoot
$log = Join-Path $repo 'senkron.log'
$stopFile = Join-Path $repo '.git\senkron-durdu'
$desktopNote = Join-Path ([Environment]::GetFolderPath('Desktop')) 'IRISYA-SENKRON-SORUN.txt'

function Write-Log([string]$msg) {
    $line = '{0:yyyy-MM-dd HH:mm:ss}  {1}' -f (Get-Date), $msg
    Add-Content -Path $log -Value $line -Encoding UTF8
}

function Invoke-Git {
    $out = & git -C $repo @args 2>&1 | Out-String
    [pscustomobject]@{ Code = $LASTEXITCODE; Out = $out.Trim() }
}

function Stop-WithProblem([string]$why) {
    Set-Content -Path $stopFile -Value $why -Encoding UTF8
    $text = @"
İrisya otomatik eşitleme durdu ($(Get-Date -Format 'yyyy-MM-dd HH:mm')).

Neden: $why

Ne yapmalı: Claude'a bu dosyayı ve senkron.log'u gösterin ya da çakışan dosyaları
elle düzeltip PowerShell'de şunu çalıştırın:
  cd "$repo"
  git status
Sorun çözülünce şu dosyayı silin, eşitleme kendiliğinden yeniden başlar:
  $stopFile
"@
    Set-Content -Path $desktopNote -Value $text -Encoding UTF8
    Write-Log "DURDU: $why"
}

# Aynı anda iki tur çalışmasın
$mutex = New-Object System.Threading.Mutex($false, 'Local\IrisyaSenkron')
if (-not $mutex.WaitOne(0)) { exit 0 }
try {
    if (-not (Test-Path (Join-Path $repo '.git'))) { Write-Log "Git deposu değil: $repo"; exit 1 }
    if (Test-Path $stopFile) { exit 0 }   # önceki çakışma çözülmeden devam etme
    if ((Test-Path (Join-Path $repo '.git\rebase-merge')) -or (Test-Path (Join-Path $repo '.git\rebase-apply')) -or
        (Test-Path (Join-Path $repo '.git\MERGE_HEAD'))) {
        Stop-WithProblem 'Yarım kalmış bir birleştirme (merge/rebase) var.'
        exit 1
    }

    $branch = (Invoke-Git rev-parse --abbrev-ref HEAD).Out
    if ($branch -eq 'HEAD' -or -not $branch) { Write-Log 'Bir dalda değil (detached HEAD), tur atlandı.'; exit 0 }

    # 1. Yerel değişiklikleri kaydet
    if ((Invoke-Git status --porcelain).Out) {
        $null = Invoke-Git add -A
        $msg = 'Otomatik senkron: {0}, {1:yyyy-MM-dd HH:mm}' -f $env:COMPUTERNAME, (Get-Date)
        $c = Invoke-Git commit -q -m $msg
        if ($c.Code -ne 0) { Write-Log "commit başarısız: $($c.Out)"; exit 1 }
        Write-Log "Yerel değişiklikler kaydedildi ($branch)."
    }

    # 2. GitHub'dan çek (internet yoksa sessizce sonraki tura bırak)
    $f = Invoke-Git fetch -q origin
    if ($f.Code -ne 0) { Write-Log "fetch başarısız (internet?): $($f.Out)"; exit 0 }

    $hasUpstream = (Invoke-Git rev-parse --abbrev-ref '@{u}').Code -eq 0
    if ($hasUpstream) {
        $behind = [int](Invoke-Git rev-list --count 'HEAD..@{u}').Out
        if ($behind -gt 0) {
            $p = Invoke-Git pull -q --rebase --autostash
            if ($p.Code -ne 0) {
                $null = Invoke-Git rebase --abort
                Stop-WithProblem "GitHub'daki değişikliklerle yerel değişiklikler çakışıyor. $($p.Out)"
                exit 1
            }
            Write-Log "GitHub'dan $behind yeni commit alındı ($branch)."
        }
        $ahead = [int](Invoke-Git rev-list --count '@{u}..HEAD').Out
    } else {
        $ahead = 1
    }

    # 3. GitHub'a gönder
    if ($ahead -gt 0) {
        $s = if ($hasUpstream) { Invoke-Git push -q } else { Invoke-Git push -q -u origin $branch }
        if ($s.Code -ne 0) { Write-Log "push başarısız, sonraki turda tekrar denenecek: $($s.Out)"; exit 0 }
        Write-Log "GitHub'a gönderildi ($branch)."
        if (Test-Path $desktopNote) { Remove-Item $desktopNote -ErrorAction SilentlyContinue }
    }
}
finally {
    $mutex.ReleaseMutex()
}
