param(
  [string]$Root,
  [switch]$AllowOrphans,
  [switch]$SelfTest
)

# Monthly integrity check for the starter kit docs. Read-only.
# Default FAIL: unsafe resolver paths that escape docs/, missing router/map/
# targets, duplicate names/paths, unresolved doc: tokens, and active Markdown
# files under docs/ that are absent from the resolver. -AllowOrphans is an
# explicit migration-only downgrade to WARN for orphan docs only.

$ErrorActionPreference = "Stop"

function Normalize-ResolverPath([string]$Value) {
  if ([string]::IsNullOrWhiteSpace($Value)) { return $null }
  $normalized = $Value.Trim().Replace('\', '/')
  if ($normalized.StartsWith('/') -or $normalized -match '^[A-Za-z]:') { return $null }
  $parts = @($normalized.Split('/') | Where-Object { $_ -ne '' -and $_ -ne '.' })
  if ($parts.Count -lt 2 -or $parts[0] -ne 'docs' -or $parts -contains '..') { return $null }
  return ($parts -join '/')
}

function Invoke-DocsCheck([string]$CheckRoot, [bool]$PermitOrphans) {
  $errors = @()
  $warnings = @()
  $mapPath = Join-Path (Join-Path $CheckRoot "docs") "RETRIEVAL_MAP.md"
  $routerPath = Join-Path $CheckRoot "AGENTS.md"

  if (-not (Test-Path -LiteralPath $routerPath)) { $errors += "AGENTS.md missing" }
  if (-not (Test-Path -LiteralPath $mapPath)) {
    $errors += "docs/RETRIEVAL_MAP.md missing"
    return [pscustomobject]@{ Errors=$errors; Warnings=$warnings; RowCount=0; DocCount=0 }
  }

  $rows = @()
  foreach ($line in (Get-Content -LiteralPath $mapPath)) {
    if ($line -match '^([A-Z0-9_]+)\|([^|]+)\|(.+)$') {
      $rows += [pscustomobject]@{
        Name = $Matches[1]
        Path = $Matches[2].Trim()
        Role = $Matches[3].Trim()
      }
    }
  }
  if ($rows.Count -eq 0) { $errors += "no resolver rows found in RETRIEVAL_MAP.md" }

  $seenName = @{}
  $seenPath = @{}
  foreach ($row in $rows) {
    $safePath = Normalize-ResolverPath $row.Path
    if (-not $safePath) {
      $errors += "unsafe resolver path (must stay under docs/): $($row.Name) -> $($row.Path)"
      $pathKey = $row.Path.Replace('\', '/')
    } else {
      $pathKey = $safePath
      $abs = Join-Path $CheckRoot ($safePath -replace '/', [IO.Path]::DirectorySeparatorChar)
      if (-not (Test-Path -LiteralPath $abs)) {
        $errors += "resolver row points to missing file: $($row.Name) -> $safePath"
      }
    }
    if ($seenName.ContainsKey($row.Name)) { $errors += "duplicate NAME: $($row.Name)" }
    else { $seenName[$row.Name] = $true }
    if ($seenPath.ContainsKey($pathKey)) { $errors += "duplicate path: $pathKey" }
    else { $seenPath[$pathKey] = $true }
  }

  $docsRoot = Join-Path $CheckRoot "docs"
  $docFiles = if (Test-Path -LiteralPath $docsRoot) {
    @(Get-ChildItem -LiteralPath $docsRoot -Recurse -File -Filter "*.md")
  } else { @() }

  foreach ($file in $docFiles) {
    $rel = $file.FullName.Substring($CheckRoot.Length).TrimStart('\', '/') -replace '\\', '/'
    if (-not $seenPath.ContainsKey($rel)) {
      $message = "orphan doc (not in resolver): $rel"
      if ($PermitOrphans) { $warnings += $message } else { $errors += $message }
    }
  }

  $scanFiles = @()
  if (Test-Path -LiteralPath $routerPath) { $scanFiles += Get-Item -LiteralPath $routerPath }
  $scanFiles += $docFiles
  foreach ($file in $scanFiles) {
    $text = Get-Content -LiteralPath $file.FullName -Raw
    foreach ($match in [regex]::Matches($text, 'doc:([A-Z0-9_]+)')) {
      $name = $match.Groups[1].Value
      if (-not $seenName.ContainsKey($name)) {
        $errors += "unresolved doc token doc:$name in $($file.Name)"
      }
    }
  }

  if (Test-Path -LiteralPath $routerPath) {
    $router = Get-Item -LiteralPath $routerPath
    if ($router.Length -gt 4KB) {
      $warnings += "AGENTS.md over 4KB ($([math]::Round($router.Length/1KB,1))KB) - it should route, not legislate"
    }
  }
  foreach ($file in $docFiles) {
    if ($file.Length -gt 15KB) {
      $warnings += "doc over 15KB: $($file.Name) ($([math]::Round($file.Length/1KB,1))KB) - split or diet"
    }
  }

  return [pscustomobject]@{
    Errors = $errors
    Warnings = $warnings
    RowCount = $rows.Count
    DocCount = $docFiles.Count
  }
}

function Invoke-SelfTest {
  $sandbox = Join-Path ([IO.Path]::GetTempPath()) ("agent-ops-starter-check-" + [guid]::NewGuid().ToString("N"))
  $tmp = Join-Path $sandbox "repo"
  try {
    New-Item -ItemType Directory -Force -Path (Join-Path $tmp "docs") | Out-Null
    $outside = Join-Path $sandbox "outside.md"
    Set-Content -LiteralPath $outside -Value "outside active corpus" -Encoding UTF8
    Set-Content -LiteralPath (Join-Path $tmp "AGENTS.md") -Value "router. see doc:GHOST" -Encoding UTF8
    Set-Content -LiteralPath (Join-Path $tmp "docs/REAL.md") -Value "real doc" -Encoding UTF8
    Set-Content -LiteralPath (Join-Path $tmp "docs/ORPHAN.md") -Value "not registered" -Encoding UTF8
    @"
REAL|docs/REAL.md|a real row
GONE|docs/MISSING.md|points at nothing
REAL|docs/OTHER.md|duplicate name
OTHER|docs/REAL.md|duplicate path
ESCAPE|../outside.md|existing file outside repository
ABSOLUTE|$outside|existing absolute file outside repository
DRIVE|C:\absolute\outside.md|drive-root path
RETRIEVAL_MAP|docs/RETRIEVAL_MAP.md|this resolver
"@ | Set-Content -LiteralPath (Join-Path $tmp "docs/RETRIEVAL_MAP.md") -Encoding UTF8

    $strict = Invoke-DocsCheck $tmp $false
    $migration = Invoke-DocsCheck $tmp $true
    $joined = (@($strict.Errors) + @($strict.Warnings)) -join " | "
    $migrationJoined = (@($migration.Errors) + @($migration.Warnings)) -join " | "
    $expectations = [ordered]@{
      "missing file" = $joined.Contains("missing file: GONE")
      "duplicate NAME" = $joined.Contains("duplicate NAME: REAL")
      "duplicate path" = $joined.Contains("duplicate path: docs/REAL.md")
      "unresolved doc token" = $joined.Contains("unresolved doc token doc:GHOST")
      "strict orphan error" = (@($strict.Errors | Where-Object { $_ -like '*ORPHAN.md*' }).Count -gt 0)
      "migration orphan warning" = ((@($migration.Warnings | Where-Object { $_ -like '*ORPHAN.md*' }).Count -gt 0) -and (@($migration.Errors | Where-Object { $_ -like '*ORPHAN.md*' }).Count -eq 0))
      "mode preserves other errors" = $migrationJoined.Contains("missing file: GONE")
      "reject parent escape" = ($joined.Contains("unsafe resolver path") -and $joined.Contains("ESCAPE -> ../outside.md"))
      "reject absolute path" = ($joined.Contains("unsafe resolver path") -and $joined.Contains("ABSOLUTE ->"))
      "reject drive-root path" = ($joined.Contains("unsafe resolver path") -and $joined.Contains("DRIVE -> C:"))
    }
    foreach ($entry in $expectations.GetEnumerator()) {
      Write-Host ("  [{0}] {1}" -f $(if ($entry.Value) { "OK" } else { "MISS" }), $entry.Key)
    }
    $missed = @($expectations.GetEnumerator() | Where-Object { -not $_.Value })
    Write-Host ("self_test_checks={0} missed={1}" -f $expectations.Count, $missed.Count)
    Write-Host ("SELF-TEST: " + $(if ($missed.Count -eq 0) { "PASS" } else { "FAIL" }))
    return ($missed.Count -eq 0)
  }
  finally {
    if (Test-Path -LiteralPath $sandbox) { Remove-Item -LiteralPath $sandbox -Recurse -Force }
  }
}

if ($SelfTest) {
  $selfTestPassed = Invoke-SelfTest
  exit $(if ($selfTestPassed) { 0 } else { 1 })
}
if (-not $Root) { $Root = Split-Path $PSScriptRoot -Parent }
$Root = [IO.Path]::GetFullPath($Root)
$result = Invoke-DocsCheck $Root ([bool]$AllowOrphans)
foreach ($item in $result.Errors) { Write-Output "ERROR: $item" }
foreach ($item in $result.Warnings) { Write-Output "WARN: $item" }
Write-Output ("rows={0} docs={1} errors={2} warnings={3}" -f $result.RowCount, $result.DocCount, $result.Errors.Count, $result.Warnings.Count)
Write-Output ("orphan_mode=" + $(if ($AllowOrphans) { "migration-warning" } else { "strict-error" }))
if ($result.Errors.Count -gt 0) { Write-Output "RESULT: FAIL"; exit 1 }
Write-Output "RESULT: PASS"
exit 0
