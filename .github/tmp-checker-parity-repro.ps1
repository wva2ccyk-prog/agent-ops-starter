$ErrorActionPreference = 'Stop'

Write-Host '== directory target parity =='
$sandbox = Join-Path $env:RUNNER_TEMP ('starter-dir-repro-' + [guid]::NewGuid().ToString('N'))
$root = Join-Path $sandbox 'repo'
New-Item -ItemType Directory -Force -Path (Join-Path $root 'docs\DIR_TARGET') | Out-Null
Set-Content -LiteralPath (Join-Path $root 'AGENTS.md') -Value 'router' -Encoding UTF8
Set-Content -LiteralPath (Join-Path $root 'docs\RETRIEVAL_MAP.md') -Value @(
  'DIR|docs/DIR_TARGET|directory target should not be valid',
  'RETRIEVAL_MAP|docs/RETRIEVAL_MAP.md|resolver'
) -Encoding UTF8
python tools/check_docs.py --root $root
$pyCode = $LASTEXITCODE
& tools/check_docs.ps1 -Root $root
$psCode = $LASTEXITCODE
Write-Host "python_directory_code=$pyCode"
Write-Host "powershell_directory_code=$psCode"
if ($pyCode -eq 0) { throw 'Python unexpectedly accepted directory target' }
if ($psCode -ne 0) { throw 'PowerShell already rejects directory target; parity defect not reproduced' }
Write-Host 'DIRECTORY-PARITY-REPRO: PASS'

Write-Host '== malformed resolver rows =='
$sandbox2 = Join-Path $env:RUNNER_TEMP ('starter-malformed-repro-' + [guid]::NewGuid().ToString('N'))
$root2 = Join-Path $sandbox2 'repo'
New-Item -ItemType Directory -Force -Path (Join-Path $root2 'docs') | Out-Null
Set-Content -LiteralPath (Join-Path $root2 'AGENTS.md') -Value 'router' -Encoding UTF8
Set-Content -LiteralPath (Join-Path $root2 'docs\REAL.md') -Value 'real' -Encoding UTF8
Set-Content -LiteralPath (Join-Path $root2 'docs\OTHER.md') -Value 'other' -Encoding UTF8
Set-Content -LiteralPath (Join-Path $root2 'docs\RETRIEVAL_MAP.md') -Value @(
  '# Retrieval Map',
  '',
  '## Resolver Table',
  'REAL|docs/REAL.md|valid',
  'BROKEN_TOO_FEW|docs/REAL.md',
  'BROKEN_TOO_MANY|docs/OTHER.md|role|extra',
  'RETRIEVAL_MAP|docs/RETRIEVAL_MAP.md|resolver',
  '',
  '## Rules For This File'
) -Encoding UTF8
python tools/check_docs.py --root $root2
$pyMalformed = $LASTEXITCODE
& tools/check_docs.ps1 -Root $root2
$psMalformed = $LASTEXITCODE
Write-Host "python_malformed_code=$pyMalformed"
Write-Host "powershell_malformed_code=$psMalformed"
if ($pyMalformed -ne 0 -or $psMalformed -ne 0) { throw 'One checker already rejects malformed rows' }
Write-Host 'MALFORMED-ROW-REPRO: PASS'

Write-Host '== clean baseline =='
python tools/check_docs.py --self-test
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& tools/check_docs.ps1 -SelfTest
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python tools/check_docs.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& tools/check_docs.ps1
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host 'STARTER-BASELINE: PASS'
