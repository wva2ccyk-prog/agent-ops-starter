param(
  [string]$Root,
  [switch]$AllowOrphans,
  [switch]$SelfTest
)

# Monthly integrity check for the starter kit docs. Read-only.
# Default FAIL: malformed resolver-table rows; unsafe resolver paths that escape
# docs/; missing router/map/file targets; duplicate names/paths; unresolved
# doc: tokens; and active Markdown files under docs/ absent from the resolver.
# -AllowOrphans is an explicit migration-only downgrade to WARN for orphan docs.
# Size caps: router 4KB, state docs 6KB, other active docs 10KB, optional
# always-loaded -Extra files 3KB. Oversize is an error; above 80% warns.

$ErrorActionPreference = "Stop"
$Extra = @()
for ($i = 0; $i -lt $args.Count; $i++) {
  if ($args[$i] -ne '-Extra' -or $i + 1 -ge $args.Count) {
    throw "Unexpected argument: $($args[$i]); use -Extra <file> for each extra file"
  }
  $i++
  $Extra += [string]$args[$i]
}

# History: WARN for archive/ and completed handoff files older than 30 days
# (YYYYMMDD- filename date, else mtime), and archive-file pointers in live docs.
# Report-only; removal requires ranked-list approval and a confirmed Git backup.
function Get-HistoryAgeDays([IO.FileInfo]$File, [datetime]$Now) {
  $stamp = $File.LastWriteTime
  if ($File.Name -match '^(\d{8})-') {
    $date = [datetime]::MinValue
    if ([datetime]::TryParseExact($Matches[1], 'yyyyMMdd',
        [Globalization.CultureInfo]::InvariantCulture,
        [Globalization.DateTimeStyles]::None, [ref]$date)) { $stamp = $date }
  }
  return ($Now - $stamp).TotalDays
}

function Get-HistoryWarnings([string]$CheckRoot, [object[]]$LiveFiles) {
  $now = Get-Date
  # Walk folders once, pruning Git, symlinks, caches, and each history subtree.
  $pending = [Collections.Generic.Stack[string]]::new()
  $pending.Push($CheckRoot)
  while ($pending.Count -gt 0) {
    $folder = Get-Item -LiteralPath ($pending.Pop()) -Force
    $isHistory = $folder.Name -ceq 'archive' -or
      ($folder.Name -ceq 'done' -and $folder.Parent.Name -cin @('handoffs','thread_handoffs'))
    if ($isHistory) {
      $old = @(Get-ChildItem -LiteralPath $folder.FullName -Recurse -File -Force |
        Where-Object { -not $_.LinkType -and $_.Name -ne '.DS_Store' -and (Get-HistoryAgeDays $_ $now) -gt 30 })
      if ($old.Count -gt 0) {
        $rel = $folder.FullName.Substring($CheckRoot.Length).TrimStart('\', '/') -replace '\\', '/'
        "${rel}: $($old.Count) file(s) older than 30 days; propose a ranked Diet pass (approval, backup commit, then delete)"
      }
      continue
    }
    foreach ($child in (Get-ChildItem -LiteralPath $folder.FullName -Directory -Force)) {
      if ($child.Name -notin @('.git','__pycache__') -and -not $child.LinkType) { $pending.Push($child.FullName) }
    }
  }
  foreach ($file in $LiveFiles) {
    $text = (Get-Content -LiteralPath $file.FullName -Raw) -replace '\\', '/'
    $hits = @([regex]::Matches($text, 'archive/(?:[\w.-]+/)*[\w.-]+\.\w+') |
      ForEach-Object { $_.Value } | Sort-Object -Unique)
    if ($hits.Count -gt 0) {
      $label = [IO.Path]::GetRelativePath($CheckRoot, $file.FullName) -replace '\\', '/'
      "history pointer in ${label}: $($hits -join ', ')"
    }
  }
}

function New-HistoryFixture([string]$Root, [string]$DoneRel) {
  $archive = Join-Path $Root 'archive'
  New-Item -ItemType Directory -Force -Path (Join-Path $archive 'nested'), (Join-Path $Root $DoneRel) | Out-Null
  foreach ($name in 'old.md','20260230-invalid.md','20990101-future.md') {
    $path = Join-Path $archive $name
    Set-Content -LiteralPath $path -Value 'history archive/ignored.md'
    (Get-Item -LiteralPath $path).LastWriteTime = (Get-Date).AddDays(-40)
  }
  foreach ($name in '20000101-dated.md','nested/20000101-nested.md','fresh.md') {
    Set-Content -LiteralPath (Join-Path $archive $name) -Value 'history'
  }
  Set-Content -LiteralPath (Join-Path (Join-Path $Root $DoneRel) '20000101-done.md') -Value 'completed'
  New-Item -ItemType Directory -Force -Path (Join-Path $Root '.hidden/archive') | Out-Null
  Set-Content -LiteralPath (Join-Path $Root '.hidden/archive/20000101-hidden.md') -Value 'hidden history'
  Add-Content -LiteralPath (Join-Path $Root 'docs/REAL.md') -Value 'see archive/nested/old.md'
}

function Normalize-ResolverPath([string]$Value) {
  if ([string]::IsNullOrWhiteSpace($Value)) { return $null }
  $normalized = $Value.Trim().Replace('\', '/')
  if ($normalized.StartsWith('/') -or $normalized -match '^[A-Za-z]:') { return $null }
  $parts = @($normalized.Split('/') | Where-Object { $_ -ne '' -and $_ -ne '.' })
  if ($parts.Count -lt 2 -or $parts[0] -ne 'docs' -or $parts -contains '..') { return $null }
  return ($parts -join '/')
}

function Get-SizeFinding([string]$Path, [long]$Cap) {
  $size = (Get-Item -LiteralPath $Path).Length
  $detail = "$Path ($size bytes, cap $Cap bytes)"
  if ($size -gt $Cap) {
    return [pscustomobject]@{ Severity='ERROR'; Message="oversize: $detail - split or diet" }
  }
  if ($size -gt ($Cap * 0.8)) {
    return [pscustomobject]@{ Severity='WARN'; Message="near cap: $detail" }
  }
}

function Invoke-DocsCheck([string]$CheckRoot, [bool]$PermitOrphans, [string[]]$ExtraFiles = @()) {
  $errors = @()
  $warnings = @()
  $mapPath = Join-Path (Join-Path $CheckRoot "docs") "RETRIEVAL_MAP.md"
  $routerPath = Join-Path $CheckRoot "AGENTS.md"

  if (-not (Test-Path -LiteralPath $routerPath -PathType Leaf)) { $errors += "AGENTS.md missing" }
  if (-not (Test-Path -LiteralPath $mapPath -PathType Leaf)) {
    $errors += "docs/RETRIEVAL_MAP.md missing"
    return [pscustomobject]@{ Errors=$errors; Warnings=$warnings; RowCount=0; DocCount=0 }
  }

  $rows = @()
  $inResolverTable = $false
  $sawResolverTable = $false
  $lineNo = 0
  foreach ($rawLine in (Get-Content -LiteralPath $mapPath)) {
    $lineNo++
    $line = $rawLine.Trim()
    if ($line -eq '## Resolver Table') {
      $inResolverTable = $true
      $sawResolverTable = $true
      continue
    }
    if ($inResolverTable -and $line -match '^##\s+') { break }
    if (-not $inResolverTable -or [string]::IsNullOrWhiteSpace($line)) { continue }
    if ($line -match '^([A-Z0-9_]+)\|([^|]+)\|([^|]+)$') {
      $pathValue = $Matches[2].Trim()
      $roleValue = $Matches[3].Trim()
      if (-not $pathValue -or -not $roleValue) {
        $errors += "malformed resolver row at line ${lineNo}: $line"
        continue
      }
      $rows += [pscustomobject]@{
        Name = $Matches[1]
        Path = $pathValue
        Role = $roleValue
      }
    } else {
      $errors += "malformed resolver row at line ${lineNo}: $line"
    }
  }
  if (-not $sawResolverTable) { $errors += "resolver table heading missing: ## Resolver Table" }
  if ($rows.Count -eq 0) { $errors += "no resolver rows found in RETRIEVAL_MAP.md" }

  $seenName = @{}
  $seenPath = @{}
  $statePaths = @{}
  foreach ($row in $rows) {
    $safePath = Normalize-ResolverPath $row.Path
    if (-not $safePath) {
      $errors += "unsafe resolver path (must stay under docs/): $($row.Name) -> $($row.Path)"
      $pathKey = $row.Path.Replace('\', '/')
    } else {
      $pathKey = $safePath
      $abs = Join-Path $CheckRoot ($safePath -replace '/', [IO.Path]::DirectorySeparatorChar)
      if (-not (Test-Path -LiteralPath $abs -PathType Leaf)) {
        $errors += "resolver row points to missing file: $($row.Name) -> $safePath"
      }
    }
    if ($seenName.ContainsKey($row.Name)) { $errors += "duplicate NAME: $($row.Name)" }
    else { $seenName[$row.Name] = $true }
    if ($seenPath.ContainsKey($pathKey)) { $errors += "duplicate path: $pathKey" }
    else { $seenPath[$pathKey] = $true }
    if (($row.Name -eq 'STATE' -or $row.Name -eq 'MEMORY_LEDGER') -and $safePath) {
      $statePaths[$safePath] = $true
    }
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
  if (Test-Path -LiteralPath $routerPath -PathType Leaf) { $scanFiles += Get-Item -LiteralPath $routerPath }
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

  $sizedFiles = @()
  if (Test-Path -LiteralPath $routerPath -PathType Leaf) {
    $sizedFiles += [pscustomobject]@{ Path=$routerPath; Cap=4KB }
  }
  foreach ($file in $docFiles) {
    $rel = $file.FullName.Substring($CheckRoot.Length).TrimStart('\', '/') -replace '\\', '/'
    $cap = if ($statePaths.ContainsKey($rel)) { 6KB } else { 10KB }
    $sizedFiles += [pscustomobject]@{ Path=$file.FullName; Cap=$cap }
  }
  foreach ($path in $ExtraFiles) {
    if (Test-Path -LiteralPath $path -PathType Leaf) {
      $sizedFiles += [pscustomobject]@{ Path=$path; Cap=3KB }
    } else {
      $errors += "extra file missing: $path"
    }
  }
  foreach ($entry in $sizedFiles) {
    $finding = Get-SizeFinding $entry.Path $entry.Cap
    if ($finding) {
      if ($finding.Severity -eq 'ERROR') { $errors += $finding.Message }
      else { $warnings += $finding.Message }
    }
  }

  $historyLive = @($scanFiles)
  $projects = Join-Path $CheckRoot 'projects'
  if (Test-Path -LiteralPath $projects -PathType Container) {
    foreach ($project in (Get-ChildItem -LiteralPath $projects -Directory)) {
      $historyLive += @(Get-ChildItem -LiteralPath $project.FullName -File -Filter '*.md' |
        Where-Object { $_.Name -in @('README.md','STATE.md','DECISIONS.md') })
    }
  }
  foreach ($extra in $ExtraFiles) {
    if (Test-Path -LiteralPath $extra -PathType Leaf) { $historyLive += Get-Item -LiteralPath $extra }
  }
  $warnings += @(Get-HistoryWarnings $CheckRoot $historyLive)
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
    New-Item -ItemType Directory -Force -Path (Join-Path $tmp "docs/DIR_TARGET") | Out-Null
    $outside = Join-Path $sandbox "outside.md"
    Set-Content -LiteralPath $outside -Value "outside active corpus" -Encoding UTF8
    Set-Content -LiteralPath (Join-Path $tmp "AGENTS.md") -Value "router. see doc:GHOST" -Encoding UTF8
    Set-Content -LiteralPath (Join-Path $tmp "docs/REAL.md") -Value "real doc" -Encoding UTF8
    Set-Content -LiteralPath (Join-Path $tmp "docs/ORPHAN.md") -Value "not registered" -Encoding UTF8
    [IO.File]::WriteAllText((Join-Path $tmp "docs/BIG.md"), ('x' * (10KB + 1)))
    [IO.File]::WriteAllText((Join-Path $tmp "docs/NEAR.md"), ('x' * [int](10KB * 0.9)))
    [IO.File]::WriteAllText((Join-Path $tmp "docs/STATE.md"), ('x' * (6KB + 1)))
    $extraFile = Join-Path $sandbox "EXTRA.md"
    [IO.File]::WriteAllText($extraFile, ('x' * (3KB + 1)))
    @"
# Retrieval Map

## Resolver Table
REAL|docs/REAL.md|a real row
GONE|docs/MISSING.md|points at nothing
REAL|docs/OTHER.md|duplicate name
OTHER|docs/REAL.md|duplicate path
DIRECTORY|docs/DIR_TARGET|directory is not a file target
ESCAPE|../outside.md|existing file outside repository
ABSOLUTE|$outside|existing absolute file outside repository
DRIVE|C:\absolute\outside.md|drive-root path
BROKEN_TOO_FEW|docs/REAL.md
BROKEN_TOO_MANY|docs/REAL.md|role|extra
BIG|docs/BIG.md|oversize doc
NEAR|docs/NEAR.md|near-cap doc
STATE|docs/STATE.md|oversize state doc
RETRIEVAL_MAP|docs/RETRIEVAL_MAP.md|this resolver

## Rules For This File
"@ | Set-Content -LiteralPath (Join-Path $tmp "docs/RETRIEVAL_MAP.md") -Encoding UTF8

    New-HistoryFixture $tmp 'handoffs/done'

    $strict = Invoke-DocsCheck $tmp $false @($extraFile, (Join-Path $sandbox "NOPE.md"))
    $migration = Invoke-DocsCheck $tmp $true
    $joined = (@($strict.Errors) + @($strict.Warnings)) -join " | "
    $migrationJoined = (@($migration.Errors) + @($migration.Warnings)) -join " | "
    $expectations = [ordered]@{
      'archive expiry warn' = (@($strict.Warnings | Where-Object { $_ -like 'archive: 4 file(s) older than 30 days*' }).Count -eq 1)
      'done expiry warn' = (@($strict.Warnings | Where-Object { $_ -like 'handoffs/done: 1 file(s) older*' }).Count -eq 1)
      'history pointer warn' = $joined.Contains('history pointer in docs/REAL.md: archive/nested/old.md')
      'hidden history traversed' = (@($strict.Warnings | Where-Object { $_ -like '.hidden/archive: 1 file(s) older*' }).Count -eq 1)
      'history not live' = (-not $joined.Contains('archive/ignored.md'))
      'filename date beats mtime' = ((Get-HistoryAgeDays (Get-Item (Join-Path $tmp 'archive/20000101-dated.md')) (Get-Date)) -gt 30)
      'future date beats old mtime' = ((Get-HistoryAgeDays (Get-Item (Join-Path $tmp 'archive/20990101-future.md')) (Get-Date)) -lt 0)
      'invalid date falls back' = ((Get-HistoryAgeDays (Get-Item (Join-Path $tmp 'archive/20260230-invalid.md')) (Get-Date)) -gt 30)
      '30-day boundary retained' = ((Get-HistoryAgeDays (Get-Item (Join-Path $tmp 'archive/old.md')) ((Get-Item (Join-Path $tmp 'archive/old.md')).LastWriteTime.AddDays(30))) -eq 30)
      "missing file" = $joined.Contains("missing file: GONE")
      "directory target" = $joined.Contains("missing file: DIRECTORY")
      "malformed too few" = ($joined.Contains("malformed resolver row") -and $joined.Contains("BROKEN_TOO_FEW"))
      "malformed too many" = ($joined.Contains("malformed resolver row") -and $joined.Contains("BROKEN_TOO_MANY"))
      "duplicate NAME" = $joined.Contains("duplicate NAME: REAL")
      "duplicate path" = $joined.Contains("duplicate path: docs/REAL.md")
      "unresolved doc token" = $joined.Contains("unresolved doc token doc:GHOST")
      "strict orphan error" = (@($strict.Errors | Where-Object { $_ -like '*ORPHAN.md*' }).Count -gt 0)
      "migration orphan warning" = ((@($migration.Warnings | Where-Object { $_ -like '*ORPHAN.md*' }).Count -gt 0) -and (@($migration.Errors | Where-Object { $_ -like '*ORPHAN.md*' }).Count -eq 0))
      "mode preserves other errors" = ($migrationJoined.Contains("missing file: GONE") -and $migrationJoined.Contains("BROKEN_TOO_FEW"))
      "reject parent escape" = ($joined.Contains("unsafe resolver path") -and $joined.Contains("ESCAPE -> ../outside.md"))
      "reject absolute path" = ($joined.Contains("unsafe resolver path") -and $joined.Contains("ABSOLUTE ->"))
      "reject drive-root path" = ($joined.Contains("unsafe resolver path") -and $joined.Contains("DRIVE -> C:"))
      "oversize doc error" = (@($strict.Errors | Where-Object { $_ -like '*oversize*BIG.md*' }).Count -gt 0)
      "near-cap doc warning" = (@($strict.Warnings | Where-Object { $_ -like '*near cap*NEAR.md*' }).Count -gt 0)
      "state doc cap" = (@($strict.Errors | Where-Object { $_ -like '*oversize*STATE.md*cap 6144 bytes*' }).Count -gt 0)
      "oversize extra error" = (@($strict.Errors | Where-Object { $_ -like '*oversize*EXTRA.md*' }).Count -gt 0)
      "missing extra error" = (@($strict.Errors | Where-Object { $_ -like '*extra file missing*NOPE.md*' }).Count -gt 0)
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
$result = Invoke-DocsCheck $Root ([bool]$AllowOrphans) $Extra
foreach ($item in $result.Errors) { Write-Output "ERROR: $item" }
foreach ($item in $result.Warnings) { Write-Output "WARN: $item" }
Write-Output ("rows={0} docs={1} errors={2} warnings={3}" -f $result.RowCount, $result.DocCount, $result.Errors.Count, $result.Warnings.Count)
Write-Output ("orphan_mode=" + $(if ($AllowOrphans) { "migration-warning" } else { "strict-error" }))
if ($result.Errors.Count -gt 0) { Write-Output "RESULT: FAIL"; exit 1 }
Write-Output "RESULT: PASS"
exit 0
