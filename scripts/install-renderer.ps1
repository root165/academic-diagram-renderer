[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('plantuml', 'graphviz', 'mermaid', 'drawio')]
    [string]$Renderer,
    [switch]$Plan,
    [switch]$Approved,
    [switch]$InstallScoop,
    [string]$ScoopDir = 'D:\Scoop',
    [string[]]$Package,
    [string[]]$Bucket
)

$ErrorActionPreference = 'Stop'

$defaults = @{
    plantuml = @{ Commands = @('plantuml', 'java'); SuggestedPackages = @('plantuml'); SuggestedBuckets = @('main'); Dependencies = @('Java runtime; Graphviz is recommended for broad PlantUML diagram support') }
    graphviz = @{ Commands = @('dot'); SuggestedPackages = @('graphviz'); SuggestedBuckets = @('main'); Dependencies = @() }
    mermaid = @{ Commands = @('mmdc', 'node'); SuggestedPackages = @('nodejs', 'mermaid-cli'); SuggestedBuckets = @('main'); Dependencies = @('Node.js') }
    drawio = @{ Commands = @('drawio', 'draw.io'); SuggestedPackages = @('draw.io'); SuggestedBuckets = @('extras'); Dependencies = @() }
}

$selection = $defaults[$Renderer]
$scoopCommand = Get-Command scoop -ErrorAction SilentlyContinue
$installPlan = [PSCustomObject]@{
    renderer = $Renderer
    commands_required = $selection.Commands
    commands_available = @($selection.Commands | ForEach-Object { [PSCustomObject]@{ command = $_; available = [bool](Get-Command $_ -ErrorAction SilentlyContinue) } })
    scoop_available = [bool]$scoopCommand
    scoop_root_for_new_install = $ScoopDir
    suggested_packages = if ($Package) { $Package } else { $selection.SuggestedPackages }
    suggested_buckets = if ($Bucket) { $Bucket } else { $selection.SuggestedBuckets }
    dependencies = $selection.Dependencies
    side_effects = @('Downloads software packages', 'Writes Scoop packages/shims and may add buckets', 'May create Scoop at the stated location when explicitly authorized')
    authorization_required = $true
}

if ($Plan) {
    $installPlan | ConvertTo-Json -Depth 5
    exit 0
}

if (-not $Approved) {
    throw 'Refusing to install: run with -Plan, ask the user for explicit approval, then re-run with -Approved and the approved packages/buckets.'
}

if (-not $scoopCommand) {
    if (-not $InstallScoop) {
        throw "Scoop is unavailable. The approved invocation must include -InstallScoop to bootstrap it at $ScoopDir."
    }
    $installer = Join-Path ([System.IO.Path]::GetTempPath()) 'install-scoop.ps1'
    Invoke-RestMethod -Uri 'https://get.scoop.sh' -OutFile $installer
    & $installer -ScoopDir $ScoopDir
    $scoopCommand = Get-Command scoop -ErrorAction SilentlyContinue
    if (-not $scoopCommand) {
        $candidate = Join-Path $ScoopDir 'shims\scoop.ps1'
        if (Test-Path -LiteralPath $candidate) { $scoopCommand = Get-Command $candidate }
    }
    if (-not $scoopCommand) { throw 'Scoop bootstrap completed without an available scoop command. Open a new PowerShell session and rerun discovery.' }
}

$scoop = $scoopCommand.Source
$approvedBuckets = if ($Bucket) { $Bucket } else { $selection.SuggestedBuckets }
foreach ($item in $approvedBuckets) {
    $known = & $scoop bucket list 2>$null
    if ($known -notmatch "(?m)^$([regex]::Escape($item))$") { & $scoop bucket add $item }
}

$approvedPackages = if ($Package) { $Package } else { $selection.SuggestedPackages }
foreach ($item in $approvedPackages) {
    Write-Host "Searching approved package: $item"
    & $scoop search $item
    Write-Host "Installing approved package: $item"
    & $scoop install $item
}

& "$PSScriptRoot\discover-tools.ps1"
