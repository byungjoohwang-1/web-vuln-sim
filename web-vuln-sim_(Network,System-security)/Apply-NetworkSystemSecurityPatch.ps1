param(
  [Parameter(Mandatory = $true)]
  [string] $ProjectRoot,
  [switch] $Apply,
  [switch] $OverwriteModule
)

$ErrorActionPreference = 'Stop'

$sourceRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$sourcePublic = Join-Path $sourceRoot 'public'
$publicRoot = Join-Path $ProjectRoot 'public'
$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$backupRoot = Join-Path $ProjectRoot ".wvs-patch-backups"
$runId = "$timestamp-$([guid]::NewGuid().ToString('N'))"
$backupDir = Join-Path $backupRoot $runId

function Assert-PathSafe {
  param([string] $Path)
  if ([string]::IsNullOrWhiteSpace($Path)) {
    throw 'Invalid path.'
  }
  if (-not (Test-Path $Path -PathType Container)) {
    throw "Path does not exist: $Path"
  }
}

function Read-TextSafe {
  param([string] $Path)
  try {
    return Get-Content -Path $Path -Raw -Encoding UTF8
  } catch {
    throw "Read failed: $Path"
  }
}

function Write-TextSafe {
  param(
    [string] $Path,
    [string] $Text,
    [string] $RelativePath
  )
  $null = New-Item -ItemType Directory -Path (Split-Path -Parent $Path) -Force
  $abs = [IO.Path]::GetFullPath((Resolve-Path -Path (Split-Path -Parent $Path)).Path)
  if (-not $abs.StartsWith([IO.Path]::GetFullPath((Resolve-Path -Path $publicRoot).Path), [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Refusing to write outside public root: $Path"
  }

  if (Test-Path -LiteralPath $Path) {
    if (-not (Test-Path -LiteralPath $backupDir)) {
      $null = New-Item -ItemType Directory -Path $backupDir -Force
    }
    $b = Join-Path $backupDir $RelativePath
    $null = New-Item -ItemType Directory -Path (Split-Path -Parent $b) -Force
    Copy-Item -LiteralPath $Path -Destination $b -Force
  }

  if (-not $Apply) {
    return
  }
  Set-Content -Path $Path -Value $Text -Encoding UTF8 -NoNewline
}

function Equal-Text {
  param([string] $A, [string] $B)
  return $A -eq $B
}

function RelPath {
  param([string] $Target, [string] $Base)
  $fullTarget = [IO.Path]::GetFullPath($Target)
  $fullBase = [IO.Path]::GetFullPath($Base)
  return $fullTarget.Substring($fullBase.Length).TrimStart('\')
}

function Log-Plan {
  param([string] $Message, [string] $Status = 'PLAN')
  Write-Host "[$Status] $Message"
}

Assert-PathSafe -Path $ProjectRoot
Assert-PathSafe -Path $sourcePublic
Assert-PathSafe -Path $publicRoot

$required = @(
  'vuln-hub.html',
  'js/soc-chrome.js',
  'data/search-index.json',
  'data/content-catalog.json'
)
foreach ($relative in $required) {
  $path = Join-Path $publicRoot $relative
  if (-not (Test-Path $path)) {
    throw "Required file missing: $relative"
  }
}

if (-not (Test-Path $sourceRoot)) {
  throw "Source root missing: $sourceRoot"
}
if (-not (Test-Path $sourcePublic)) {
  throw "Source public missing: $sourcePublic"
}

$moduleFiles = @(
  'network-system-security.html',
  'css/network-system-security.css',
  'js/network-system-security.js',
  'js/network-system-evaluator.js',
  'data/network-system-security.json',
  'data/network-system-security-data.js',
  'js/security-casebook.js',
  'data/security-casebook.js',
  'network-system-resources.html',
  'data/evidence/firewall.js',
  'data/evidence/dns.js',
  'data/evidence/authentication.js',
  'data/evidence/integrity.js',
  'data/evidence/windows.js',
  'data/evidence/backup.js'
)

$moduleData = (Read-TextSafe -Path (Join-Path $sourcePublic 'data/network-system-security.json')) | ConvertFrom-Json
if (-not $moduleData.lessons -or -not $moduleData.module) { throw 'Module JSON has no lessons or metadata.' }
$modulePage = 'network-system-security.html'
$moduleVersion = if ($moduleData.module.contentVersion) { [string]$moduleData.module.contentVersion } else { [string]$moduleData.schemaVersion }

$changes = @()

foreach ($file in $moduleFiles) {
  $source = Join-Path $sourcePublic $file
  $target = Join-Path $publicRoot $file
  if (-not (Test-Path $source)) {
    throw "Source file missing for module copy: $file"
  }
  $srcText = Read-TextSafe -Path $source
  if (Test-Path $target) {
    $dstText = Read-TextSafe -Path $target
    if (Equal-Text $srcText $dstText) {
      Log-Plan "module file already identical: $file"
      continue
    }
    if (-not $OverwriteModule) {
      throw "Target module file exists and differs. Use -OverwriteModule to apply: $file"
    }
  }
  $changes += [PSCustomObject]@{ Action='upsert'; Relative=$file; Source=$source; Target=$target; Next=$srcText; Reason='module payload' }
}

$socChrome = Join-Path $publicRoot 'js/soc-chrome.js'
$socChromeText = Read-TextSafe -Path $socChrome

$navEntry = "{ t:'네트워크 및 시스템 보안',en:'Network & Systems',u:'/network-system-security.html' }"
$navMatch = [regex]::Match($socChromeText, "var\s+NAV\s*=\s*\[(?<body>[\s\S]*?)\];")
if (-not $navMatch.Success) {
  throw 'Cannot locate NAV block in js/soc-chrome.js.'
}
$inner = $navMatch.Groups['body'].Value
if ($inner -notmatch "u\s*:\s*['""]\/network-system-security\.html['""]") {
  $trim = $inner.TrimEnd()
  $hasContent = -not [string]::IsNullOrWhiteSpace($trim)
  if ($hasContent -and -not $trim.Trim().EndsWith(',')) {
    $trim += ','
  }
  $newInner = if ($hasContent) {
    $trim + [Environment]::NewLine + "  $navEntry,"
  } else {
    "  $navEntry"
  }
  $patchedSoc = $socChromeText.Substring(0, $navMatch.Index) +
    ("var NAV = [" + [Environment]::NewLine + $newInner + [Environment]::NewLine + "];") +
    $socChromeText.Substring($navMatch.Index + $navMatch.Length)
  $changes += [PSCustomObject]@{
    Action = 'upsert'
    Relative = 'js/soc-chrome.js'
    Source = $socChrome
    Target = $socChrome
    Next = $patchedSoc
    Reason = 'add NAV menu item'
  }
} else {
  Log-Plan "NAV already contains module URL: /network-system-security.html"
}

$vulnHub = Join-Path $publicRoot 'vuln-hub.html'
$vulnHubText = Read-TextSafe -Path $vulnHub
$hubMarker = 'id="network-system-security-hub-card"'
$hubSnippet = @'

<section id="network-system-security-hub-card" class="hub-card">
  <h2>네트워크 및 시스템 보안</h2>
  <p>네트워크 경계, Linux, Windows 보안 설정 기반 학습 모듈</p>
  <a href="/network-system-security.html">학습 페이지로 이동</a>
</section>
'@

if ($vulnHubText -notmatch $hubMarker) {
  $mainMatch = [regex]::Match($vulnHubText, '<main[^>]*class="[^"]*soc-main[^"]*"[^>]*>')
  if (-not $mainMatch.Success) {
    Log-Plan 'Cannot locate main.soc-main in vuln-hub.html. Skipping hub card insert.'
  } else {
    $insertPos = $mainMatch.Index + $mainMatch.Length
    $patchedHub = $vulnHubText.Insert($insertPos, [Environment]::NewLine + $hubSnippet)
    $changes += [PSCustomObject]@{
      Action = 'upsert'
      Relative = 'vuln-hub.html'
      Source = $vulnHub
      Target = $vulnHub
      Next = $patchedHub
      Reason = 'insert hub card'
    }
  }
}

$searchPath = Join-Path $publicRoot 'data/search-index.json'
$searchJson = $null
try {
  $searchText = Read-TextSafe -Path $searchPath
  $searchJson = $searchText | ConvertFrom-Json
} catch {
  throw "Invalid JSON in search-index.json: $($_.Exception.Message)"
}
if (-not ($searchJson.PSObject.Properties.Name -contains 'pages')) {
  throw 'search-index.json does not have pages array.'
}

function Add-SearchPage {
  param($array, $entry)
  $existing = $array | Where-Object { $_.u -eq $entry.u } | Select-Object -First 1
  if ($null -eq $existing) {
    $array.Add([PSCustomObject]$entry)
    return $true
  }
  $changed = $false
  foreach ($key in @('t','g','k')) {
    $property = $existing.PSObject.Properties[$key]
    if ($null -eq $property -or $property.Value -ne $entry[$key]) {
      $existing | Add-Member -MemberType NoteProperty -Name $key -Value $entry[$key] -Force
      $changed = $true
    }
  }
  return $changed
}

$searchChanges = $false
$searchEntries = [System.Collections.Generic.List[object]]::new()
foreach ($page in $searchJson.pages) {
  $searchEntries.Add($page)
}

$searchHub = @{
  t = '네트워크 및 시스템 보안'
  u = '/network-system-security.html'
  g = 'sec'
  k = '네트워크 및 시스템 보안 방화벽 Linux Windows 원격관리'
}
if (Add-SearchPage -array $searchEntries -entry $searchHub) {
  $searchChanges = $true
}

$searchGroups = @{ network='network'; linux='linux'; windows='win' }
$deepLinks = @(
  foreach ($lesson in $moduleData.lessons) {
    @{
      t = "$($lesson.code) $($lesson.title)"
      u = "/$modulePage#$($lesson.id)"
      g = $searchGroups[$lesson.track]
      k = (@($lesson.code, $lesson.title, $lesson.goal) + @($lesson.tags)) -join ' '
    }
  }
)

foreach ($entry in $deepLinks) {
  if (Add-SearchPage -array $searchEntries -entry $entry) {
    $searchChanges = $true
  }
}

if ($searchChanges) {
  $searchJson.pages = $searchEntries.ToArray()
  $searchJson.count = $searchEntries.Count
  $patchedSearch = $searchJson | ConvertTo-Json -Depth 10
  $changes += [PSCustomObject]@{
    Action = 'upsert'
    Relative = 'data/search-index.json'
    Source = $searchPath
    Target = $searchPath
    Next = $patchedSearch
    Reason = 'upsert search index entries'
  }
}

$catalogPath = Join-Path $publicRoot 'data/content-catalog.json'
$catalogText = Read-TextSafe -Path $catalogPath
$catalog = $null
try {
  $catalog = $catalogText | ConvertFrom-Json
} catch {
  throw "Invalid JSON in content-catalog.json: $($_.Exception.Message)"
}
if (-not ($catalog.PSObject.Properties.Name -contains 'items')) {
  throw 'content-catalog.json does not have items array.'
}

$items = [System.Collections.Generic.List[object]]::new()
foreach ($item in $catalog.items) {
  $items.Add($item)
}

$catalogUpdates = @(
  @{
    id = $moduleData.module.id
    page = $modulePage
    title = $moduleData.module.title
    domains = @('network','system','linux','windows')
    skills = @()
    keywords = @('network','system','security','네트워크','Linux','Windows','보안')
    category = '네트워크/시스템 보안'
    hubGroup = $null
    level = $null
    estimatedMinutes = [int](($moduleData.lessons | Measure-Object -Property durationMin -Sum).Sum)
    learningMode = $moduleData.module.learningMode
    progressEnabled = $false
    aiEligible = $false
    validationKinds = @()
    contentVersion = $moduleVersion
    reviewStatus = 'unreviewed'
    sourceIds = @()
  }
)
foreach ($lesson in $moduleData.lessons) {
  $track = $moduleData.module.tracks | Where-Object { $_.id -eq $lesson.track } | Select-Object -First 1
  $catalogUpdates += @{
    id = $lesson.id
    page = "$modulePage#$($lesson.id)"
    title = "$($lesson.code) $($lesson.title)"
    domains = @($lesson.track)
    skills = @()
    keywords = @($lesson.code, $lesson.title) + @($lesson.tags)
    category = $track.label
    hubGroup = $null
    level = $lesson.difficulty
    estimatedMinutes = [int]$lesson.durationMin
    learningMode = $moduleData.module.learningMode
    progressEnabled = $false
    aiEligible = $false
    validationKinds = @()
    contentVersion = $moduleVersion
    reviewStatus = 'unreviewed'
    sourceIds = @()
  }
}

function Upsert-CatalogItem {
  param([System.Collections.Generic.List[object]]$arr, [hashtable]$item)
  for ($i = 0; $i -lt $arr.Count; $i++) {
    if ($arr[$i].id -eq $item.id) {
      $changed = $false
      # Preserve platform-specific progress, review and integration settings.
      foreach ($key in @('page','title','domains','keywords','category','level','estimatedMinutes','contentVersion')) {
        $property = $arr[$i].PSObject.Properties[$key]
        $before = if ($null -eq $property) { $null } else { $property.Value | ConvertTo-Json -Depth 10 -Compress }
        $after = $item[$key] | ConvertTo-Json -Depth 10 -Compress
        if ($null -eq $property -or $before -cne $after) {
          $arr[$i] | Add-Member -MemberType NoteProperty -Name $key -Value $item[$key] -Force
          $changed = $true
        }
      }
      return $changed
    }
  }
  $arr.Add([PSCustomObject]$item)
  return $true
}

$catalogChange = $false
foreach ($item in $catalogUpdates) {
  if (Upsert-CatalogItem -arr $items -item $item) {
    $catalogChange = $true
  }
}

if ($catalogChange) {
  $catalog.items = $items.ToArray()
  if ($catalog.PSObject.Properties.Name -contains 'count') {
    $catalog.count = $items.Count
  }
  $patchedCatalog = $catalog | ConvertTo-Json -Depth 10
  $changes += [PSCustomObject]@{
    Action = 'upsert'
    Relative = 'data/content-catalog.json'
    Source = $catalogPath
    Target = $catalogPath
    Next = $patchedCatalog
    Reason = 'upsert catalog records'
  }
}

if ($changes.Count -eq 0) {
  Log-Plan 'No changes detected.'
}

foreach ($item in $changes) {
  if ($item.Target -ne $item.Source) {
    $rel = RelPath -Target $item.Target -Base $publicRoot
    if ((Test-Path $item.Target) -and (Equal-Text (Read-TextSafe -Path $item.Target) $item.Next)) {
      Log-Plan "No change (identical): $rel"
      continue
    }
    Log-Plan "$($item.Action.ToUpper()) $rel :: $($item.Reason)"
    if ($Apply) {
      Write-TextSafe -Path $item.Target -Text $item.Next -RelativePath $rel
    }
  } else {
    $rel = RelPath -Target $item.Target -Base $publicRoot
    Log-Plan "$($item.Action.ToUpper()) $rel :: $($item.Reason)"
    if ($Apply) {
      Write-TextSafe -Path $item.Target -Text $item.Next -RelativePath $rel
    }
  }
}

if ($Apply) {
  Log-Plan "Apply complete. Backup root: $backupDir"
} else {
  if ($changes.Count -gt 0) {
    Log-Plan 'Plan only. Use -Apply to write files.'
  }
}
