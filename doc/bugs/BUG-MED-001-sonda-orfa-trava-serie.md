---
id: BUG-MED-001
aliases: [BUG-MED-001]
tipo: bug
areas: [MED]
status: resolvido
gravidade: media
criado: 2026-11-25
resolvido: 2026-11-25
commit:
teste: tests/test_run_measured.py
arquivos: [scripts/run_measured.py]
palavras: [sonda, trava, série, cli não encontrado, processo órfão]
relacionados: []
---
# Série trava para sempre quando o CLI não abre
**Sintoma:** `run_series.ps1` com um `-Cli` inexistente nunca termina.
**Causa:** `run_measured.py` inicia a sonda de atraso (outro processo) antes do `Popen` do CLI; se o `Popen`
falhava, a exceção saía sem criar o arquivo de parada, e a sonda (que herda a saída) ficava viva e prendia o pipe.
O mesmo valia para falha em `limitar()` (só matava o CLI).
**Correção:** `Popen` e `limitar()` no mesmo `try`; no erro, mata o CLI (se abriu) e encerra a sonda.
**Prova:** antes, o teste manual ficou >120 s parado com a sonda órfã; depois, `tests/test_run_measured.py` sai
com erro em ~2 s e sem arquivo de parada sobrando.
**Prevenção:** teste de regressão `test_BUG_MED_001_missing_cli_does_not_hang`.
