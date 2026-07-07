param()

# Monthly integrity check for the starter kit docs. Read-only.
# PASS/FAIL on: resolver rows resolve, no duplicate names/paths,
# no orphan docs, size budgets. Run: powershell -ExecutionPolicy Bypass -File tools\check_docs.ps1

$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
$mapPath = Join-Path $root "docs\RETRIEVAL_MAP.md"

$errors = @()
$warnings = @()

if (-not (Test-Path -LiteralPath $mapPath)) {
    Write-Output "RESULT: FAIL (docs\RETRIEVAL_MAP.md missing)"
    exit 1
}

# Parse resolver rows: NAME|path|role
$rows = @()
foreach ($line in (Get-Content -LiteralPath $mapPath)) {
    if ($line -match '^([A-Z0-9_]+)\|([^|]+)\|(.+)$') {
        $rows += [pscustomobject]@{ Name = $Matches[1]; Path = $Matches[2].Trim(); Role = $Matches[3].Trim() }
    }
}
if ($rows.Count -eq 0) { $errors += "no resolver rows found in RETRIEVAL_MAP.md" }

# Rows must resolve; names and paths must be unique
$seenName = @{}; $seenPath = @{}
foreach ($r in $rows) {
    $abs = Join-Path $root ($r.Path -replace '/', '\')
    if (-not (Test-Path -LiteralPath $abs)) { $errors += "resolver row points to missing file: $($r.Name) -> $($r.Path)" }
    if ($seenName.ContainsKey($r.Name)) { $errors += "duplicate NAME: $($r.Name)" } else { $seenName[$r.Name] = $true }
    if ($seenPath.ContainsKey($r.Path)) { $errors += "duplicate path: $($r.Path)" } else { $seenPath[$r.Path] = $true }
}

# Orphans: every md under docs\ must have a resolver row
$docFiles = Get-ChildItem -LiteralPath (Join-Path $root "docs") -Recurse -File -Filter "*.md"
foreach ($f in $docFiles) {
    $rel = $f.FullName.Substring($root.Length).TrimStart('\') -replace '\\', '/'
    if (-not $seenPath.ContainsKey($rel)) { $warnings += "orphan doc (not in resolver): $rel" }
}

# doc: tokens used anywhere must resolve
$scanFiles = @(Get-Item (Join-Path $root "AGENTS.md")) + $docFiles
foreach ($f in $scanFiles) {
    $text = Get-Content -LiteralPath $f.FullName -Raw
    foreach ($m in [regex]::Matches($text, 'doc:([A-Z0-9_]+)')) {
        $n = $m.Groups[1].Value
        if (-not $seenName.ContainsKey($n)) { $errors += "unresolved doc token doc:$n in $($f.Name)" }
    }
}

# Size budgets: router <= 4KB, each doc <= 15KB
$router = Get-Item (Join-Path $root "AGENTS.md")
if ($router.Length -gt 4KB) { $warnings += "AGENTS.md over 4KB ($([math]::Round($router.Length/1KB,1))KB) - it should route, not legislate" }
foreach ($f in $docFiles) {
    if ($f.Length -gt 15KB) { $warnings += "doc over 15KB: $($f.Name) ($([math]::Round($f.Length/1KB,1))KB) - split or diet" }
}

foreach ($e in $errors) { Write-Output "ERROR: $e" }
foreach ($w in $warnings) { Write-Output "WARN: $w" }
Write-Output ("rows={0} docs={1} errors={2} warnings={3}" -f $rows.Count, $docFiles.Count, $errors.Count, $warnings.Count)

if ($errors.Count -gt 0) { Write-Output "RESULT: FAIL"; exit 1 }
Write-Output "RESULT: PASS"
