# Runs several run_measured.py configurations in a row, each one starting with a cold OS file cache.
# Usage:
#   pwsh -File run_series.ps1 -Python python -Cli audiocpp_cli.exe -Model model.gguf -Out results `
#     -Ref voice.wav -Text "Test sentence." [-ColdFile big.bin] -Config "label|extra args;label2|extra args"
# voice.wav needs voice.txt next to it with "anything;<transcript>".
param(
    [Parameter(Mandatory)][string]$Python,
    [Parameter(Mandatory)][string]$Cli,
    [Parameter(Mandatory)][string]$Model,
    [Parameter(Mandatory)][string]$Out,
    [Parameter(Mandatory)][string]$Ref,
    [Parameter(Mandatory)][string]$Text,
    [Parameter(Mandatory)][string]$Config,
    [string]$ColdFile
)
$ErrorActionPreference = 'Stop'
$runner = Join-Path $PSScriptRoot 'run_measured.py'
foreach ($c in ($Config -split ';' | Where-Object { $_.Trim() })) {
    $label, $extra = $c.Split('|', 2)
    $a = @('-I', '-B', $runner, '--cli', $Cli, '--modelo', $Model, '--saida', $Out, '--rotulo', $label,
        '--texto', $Text, '--ref', $Ref, '--teto-ram-gb', '8', '--opcao', 'fish_drama3.codec_backend=cpu')
    if ($ColdFile) { $a += '--esfriar-arquivo', $ColdFile }
    $a += ($extra -split ' ' | Where-Object { $_ })
    & $Python @a 2>&1 | Select-Object -Last 2
    if ($LASTEXITCODE -ne 0) { throw "run '$label' failed (exit $LASTEXITCODE)" }
}
"SERIES DONE"
