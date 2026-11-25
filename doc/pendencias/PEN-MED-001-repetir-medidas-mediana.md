---
id: PEN-MED-001
aliases: [PEN-MED-001]
tipo: pendencia
areas: [MED]
status: aberta
prioridade: media
criado: 2026-11-25
origem: revisão do repositório pelo dono
---
Hoje cada configuração tem uma rodada só. Rodar a referência, a configuração completa (pré-busca + 4 threads +
teto de 4 GB) e o lote de 6 tomadas **três vezes cada**, em 8 bits, com cache frio, e mostrar a mediana no README
(EN e PT). Custo estimado: cerca de 1 hora de máquina (`scripts/run_series.ps1`).
Bloqueio: a GPU estava em uso por outra sessão gerando áudio; só rodar com a placa livre.
Pronto quando: as três rodadas de cada configuração estão no `medidas.jsonl`, o README mostra a mediana e a nota
"uma rodada por configuração" sai dos limites.
