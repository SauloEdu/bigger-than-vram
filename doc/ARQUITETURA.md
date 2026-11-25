---
aliases: [ARQUITETURA]
---
# Arquitetura

- **Patch** (`patches/`): modifica o audio.cpp v0.9.6 (commit base `04a37f2`). Pré-busca e mapa quente em
  `src/framework/moe_engine/expert_storage.cpp` (variáveis `AUDIOCPP_MOE_*`); lote de tomadas com estado na VRAM
  em `src/community_models/fish_drama3/` (`generator.cpp`, `session.cpp`, `state_snapshot.h`). O código-fonte
  compilado fica fora deste repositório.
- **Medição** (`scripts/run_measured.py`): lança o `audiocpp_cli` com prioridades baixas, Job Object (teto de
  commit) e teto rígido de working set; uma sonda em outro processo mede o atraso de `sleep(10 ms)`; grava uma
  linha JSON por execução em `<saida>/medidas.jsonl`. Só Windows. Flags e chaves em português.
- **Série** (`scripts/run_series.ps1`): várias configurações seguidas, com cache de arquivos frio opcional.
- **Mapa quente** (`scripts/hot_map.py`): uso por especialista → `camada;especialista;vram|ram` + cobertura.
