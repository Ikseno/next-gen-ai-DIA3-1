param(
    [ValidateSet('A','B','C','D','E')]
    [string]$Batch = 'A',
    [string]$Cases = 'C01,C02,C03,C04,C05,C06,C07,C08,C09,C10,C11,C12,C13,C14,C15,C16,C17,C18,C19,C20',
    [switch]$RetryAccess,
    [switch]$ResetKey
)
$ErrorActionPreference = 'Stop'
$kitPath = Join-Path (Split-Path $PSScriptRoot -Parent) 'kit-td1'
$pythonPath = if (Test-Path (Join-Path (Split-Path $PSScriptRoot -Parent) '.venv\Scripts\python.exe')) { Join-Path (Split-Path $PSScriptRoot -Parent) '.venv\Scripts\python.exe' } else { 'python' }
$models = @{
    A = 'groq:openai/gpt-oss-120b'
    B = 'groq:openai/gpt-oss-20b'
    C = 'openrouter:cohere/north-mini-code:free'
    D = 'groq:qwen/qwen3.8-27b'
    E = 'openrouter:dots-studio/dots-3-note-preview:free'
}
$keyName = if ($Batch -in @('C','E')) { 'OPENROUTER_API_KEY' } else { 'GROQ_API_KEY' }
if ($ResetKey -or -not [Environment]::GetEnvironmentVariable($keyName, 'Process')) {
    $secretKey = Read-Host "Paste $keyName (hidden)" -AsSecureString
    $keyText = [System.Net.NetworkCredential]::new('', $secretKey).Password.Trim()
    if ($keyText -match '\s' -or ($keyName -eq 'GROQ_API_KEY' -and -not $keyText.StartsWith('gsk_')) -or ($keyName -eq 'OPENROUTER_API_KEY' -and -not $keyText.StartsWith('sk-or-'))) { throw 'Key format looks incorrect. Paste only the key, without quotes or other text.' }
    [Environment]::SetEnvironmentVariable($keyName, $keyText, 'Process')
    $keyText = $null
    $secretKey.Dispose()
}
Write-Host "Batch $Batch : $($models[$Batch])"
Write-Host 'Reference peer/instructor validation remains pending unless your group has completed it.'
Write-Host 'Check remaining free allowance. Run one batch at a time across the group.'
Write-Host 'Batches C and E belong to two different members and OpenRouter accounts.'
$retryOptions = @()
if ($RetryAccess) { $retryOptions += '--retry-access' }
& $pythonPath (Join-Path $kitPath 'skeleton-multi-llm-en.py') --run --models $models[$Batch] --cases $Cases --reference (Join-Path $PSScriptRoot 'reference-td1.csv') --state (Join-Path $PSScriptRoot "state-$Batch.jsonl") --out (Join-Path $PSScriptRoot "traces-$Batch.csv") --stop-on-access-error @retryOptions
if ($LASTEXITCODE -ne 0) { throw "Runner exited with code $LASTEXITCODE. Keep the trace and state files for diagnosis." }
