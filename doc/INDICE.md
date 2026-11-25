# moe-offload-desktop — índice
Atualizado: 2026-11-25 · Stack: patch C++ para o audio.cpp v0.9.6 + scripts Python/PowerShell (Windows) ·
[[VISAO]] · [[ARQUITETURA]] · [[PROGRESSO]]

## Áreas
| Código | Área | Onde fica | Palavras-chave |
|---|---|---|---|
| MET | Método e patch | `METHOD.md`, `patches/` | pré-busca, prefetch, lote, batch, mapa quente, hotmap, especialistas, mmap |
| MED | Medição | `scripts/run_measured.py`, `scripts/run_series.ps1`, `scripts/hot_map.py`, `tests/` | x tempo real, VRAM, working set, teto, atraso, sonda, cache frio |
| PUB | Publicação e licenças | `README.md`, `README.pt-BR.md`, `LICENSE`, `NOTICE` | GitHub, Reddit, privado, público, Apache, Fish Audio, pesos |
| VID | Vídeo | `doc/roteiro-video.md` | roteiro, gravação, reels, b-roll |

## Onde fica cada coisa
- Testes: `python -I -B -m unittest discover -s tests` · CI: `.github/workflows/ci.yml` (roda na central local).
- O patch tem cabeçalho de mudança (Apache-2.0 §4) antes do primeiro `diff --git`.

## Itens
Bugs em `bugs/`, decisões em `decisoes/`, pendências em `pendencias/`. Abertas: `grep -l "status: aberta" doc/pendencias/*`.
