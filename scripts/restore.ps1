param(
    [Parameter(Mandatory = $true)]
    [string]$Archive
)

$ErrorActionPreference = "Stop"

$ResolvedArchive = (Resolve-Path -LiteralPath $Archive).Path
$RootDir = Split-Path -Parent $PSScriptRoot

New-Item -ItemType Directory -Path (Join-Path $RootDir "data/sqlite") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $RootDir "data/chroma") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $RootDir "data/docs") -Force | Out-Null

tar -xzf $ResolvedArchive -C $RootDir

Write-Output "Restore completed from: $ResolvedArchive"
