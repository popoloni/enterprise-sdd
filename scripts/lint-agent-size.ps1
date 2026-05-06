# lint-agent-size.ps1 — Check agent files against their declared size-tier budget.
# Usage: .\lint-agent-size.ps1 [-AgentsDir .github\agents]
#
# Exits 0 if all agents are within budget, 1 if violations are found.

param(
    [string]$AgentsDir = ".github\agents"
)

$TierBudget = @{
    compact  = 200
    standard = 400
    extended = 600
}

$Violations = 0

Write-Host "=== Agent Size Lint ==="
Write-Host "Scanning: $AgentsDir"
Write-Host ""

$header = "{0,-40} {1,6}  {2,-10} {3,6}  {4}" -f "Agent", "Lines", "Tier", "Budget", "Status"
Write-Host $header
$separator = "{0,-40} {1,6}  {2,-10} {3,6}  {4}" -f "-----", "-----", "----", "------", "------"
Write-Host $separator

$agentFiles = Get-ChildItem -Path $AgentsDir -Filter "*.agent.md" -ErrorAction SilentlyContinue

foreach ($agentFile in $agentFiles) {
    $lines = (Get-Content -Path $agentFile.FullName -Encoding UTF8).Count
    $filename = $agentFile.Name

    # Extract size-tier from YAML frontmatter
    $tier = "standard"
    $content = Get-Content -Path $agentFile.FullName -Encoding UTF8 -Raw
    if ($content -match 'size-tier:\s*(\S+)') {
        $tier = $Matches[1].Trim()
    }

    $budget = if ($TierBudget.ContainsKey($tier)) { $TierBudget[$tier] } else { 400 }

    if ($lines -gt $budget) {
        $status = "OVER"
        $Violations++
    } else {
        $status = "OK"
    }

    $row = "{0,-40} {1,6}  {2,-10} {3,6}  {4}" -f $filename, $lines, $tier, $budget, $status
    Write-Host $row
}

Write-Host ""
if ($Violations -gt 0) {
    Write-Host "$Violations agent(s) exceed their size budget." -ForegroundColor Yellow
    Write-Host "Refactor: extract tables into .instructions.md or split modes into separate agents."
    exit 1
} else {
    Write-Host "All agents within size budget." -ForegroundColor Green
    exit 0
}
