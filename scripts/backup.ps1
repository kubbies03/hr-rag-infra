$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent $PSScriptRoot
$BackupDir = Join-Path $RootDir "backups"
$Timestamp = Get-Date -Format "yyyy-MM-dd-HHmm"
$Archive = Join-Path $BackupDir "hr-rag-backup-$Timestamp.tar.gz"

New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null

tar -czf $Archive `
    -C $RootDir `
    data/sqlite `
    data/chroma `
    data/docs `
    monitoring `
    .env.example `
    docker-compose.yml `
    nginx/nginx.conf

Write-Output "Backup created: $Archive"
