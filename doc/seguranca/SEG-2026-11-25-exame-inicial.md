# Exame de segurança inicial (2026-11-25, modo rápido)
Veredito: **libera com correções** (aplicadas no mesmo commit).
- Corrigido: o filtro de caminhos pessoais do CI abortava (`git grep` com barra invertida no fim, código 128) e
  passava sempre. Agora cobre pastas de usuário no Windows, Mac e Linux e falha se o `git grep` der erro. A etapa
  do patch também confere que a tag v0.9.6 do audio.cpp ainda aponta para `04a37f2`.
- Sem segredos (gitleaks), sem dados pessoais nos arquivos nem nos metadados de commit (e-mail *noreply*).
- Licenças ok: Apache-2.0 + NOTICE + cabeçalho de mudança no patch; "Built with Fish Audio"; nenhum peso ou áudio.
- Descartados: entradas do patch e dos scripts vêm de variáveis de ambiente e argumentos locais do próprio usuário
  (sem `shell=True`, sem `Invoke-Expression`); a etapa de CI só roda `git apply --check`, não compila o clone.
- Observação: `psutil` e `soundfile` não estão declarados em manifesto, então não entram no osv-scanner.
