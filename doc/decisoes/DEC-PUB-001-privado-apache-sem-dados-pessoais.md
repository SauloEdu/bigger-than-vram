---
id: DEC-PUB-001
aliases: [DEC-PUB-001]
tipo: decisao
areas: [PUB]
status: valida
data: 2026-11-25
relacionados: ["[[PEN-PUB-001]]"]
---
# Repositório privado até aprovação, Apache-2.0, sem dados pessoais
**Contexto:** o método vai para GitHub/Reddit; o patch deriva do audio.cpp (Apache-2.0) e as medidas usam o
Drama 3 (Fish Audio Community License v1.0, que não permite redistribuir pesos).
**Decisão:** repositório nasce privado; licença Apache-2.0 (mesma do audio.cpp, sem atrito para o patch);
`NOTICE` e cabeçalho no patch dizem o que foi mudado; "Built with Fish Audio" e link para a licença oficial;
commits com o e-mail *noreply* do GitHub; nada de pesos, áudios, caminhos pessoais, nome da empresa ou frase de
teste com marca. O CI barra `.gguf/.wav/...` e caminhos de pasta de usuário (Windows, Mac e Linux) no repositório.
**Descartado:** MIT (funcionaria, mas Apache mantém a mesma regra do código de origem); publicar os scripts de
avaliação de voz (dependem de ferramentas internas).
**Consequências:** os scripts de medição saem como estão (testados), com flags em português documentadas no README.

**Atualização (2026-11-25, revisão do dono):** a ideia não é anonimato; o projeto entra no portfólio. O README
(EN e PT) ganhou a seção de autoria com nome do autor e da empresa e convite para contato. Continuam fora: pesos,
áudios, caminhos pessoais, e-mail pessoal (commits seguem com o *noreply*). O CI segue desligado no GitHub
(roda na central local), então o README não leva selo de "build passing".
