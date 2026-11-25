---
aliases: [VISAO]
---
# Visão

**O que é:** repositório público que documenta e entrega o método para rodar um modelo MoE
em GGUF maior que a VRAM e a RAM livre num desktop comum, sem travar o PC. Caso medido: Fish Audio Drama 3
(TTS MoE ~35B) numa RTX 5060 Ti de 16 GB.

**Para quem:** quem roda modelos locais (GitHub, Reddit r/LocalLLaMA e afins) e quer reaproveitar a técnica.

**Conteúdo:** `README.md` (inglês, público), `README.pt-BR.md`, `METHOD.md` (método genérico),
`patches/audio.cpp-v0.9.6-moe-offload.patch`, scripts de medição em `scripts/`, testes em `tests/`.

**Como testar:** `python -I -B -m unittest discover -s tests`; o CI completo (gitleaks, testes, parse do
PowerShell, patch aplica no audio.cpp v0.9.6, nada de pesos/áudio/caminho pessoal) roda no `git push` pela central
de CI local.

**Publicar:** público desde 2026-11-25, depois de o dono aprovar o README ([[PEN-PUB-001]]); mudança de texto público passa pela aprovação dele.
Nunca entram pesos, áudios gerados, caminhos pessoais ou dados pessoais ([[DEC-PUB-001]]).
