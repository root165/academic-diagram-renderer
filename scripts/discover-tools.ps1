$ErrorActionPreference = 'Continue'
$commands = @('java', 'plantuml', 'dot', 'node', 'mmdc', 'drawio', 'draw.io')
$results = foreach ($name in $commands) {
    $command = Get-Command $name -ErrorAction SilentlyContinue
    [PSCustomObject]@{
        command = $name
        available = [bool]$command
        source = if ($command) { $command.Source } else { $null }
    }
}
$results | ConvertTo-Json -Depth 3
