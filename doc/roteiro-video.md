# Roteiro: 68 GB numa placa de 16 GB

Para gravar em casa e mandar para a edição. Duas versões: **curta vertical** (9:16, ~75 s, Reels/Shorts/TikTok)
e **longa** (16:9, ~5 min, YouTube; também serve de vídeo para o post no Reddit).
Todo número abaixo vem das medições do `README.md`. Não arredonde para cima na hora de falar.

Linha mestra (abre e fecha o vídeo): **o contador de tempo**. Abre com "12 minutos para 6 segundos de fala"
(versão de 8 bits, 38 GB), fecha com o mesmo contador parando em 2 min 25 s.

Cuidado com os dois tamanhos: o gancho usa o arquivo de **68 GB (16 bits)**; o caso do dia a dia é o de **38 GB
(8 bits)**. Sempre que falar de tempo, diga de qual versão é (8 bits: 12:05 → 2:25, 4,4×; 16 bits: 17:18 → 5:02, 3,4×).

---

## 1. Versão curta (vertical, ~75 s)

Ritmo: fala direta para a câmera, cortes a cada 2-3 s com tela/gráfico por cima. Texto falado em português,
legenda queimada palavra a palavra. Gatilhos: curiosidade no gancho, ganho sem trocar de placa no meio, PC que não
trava antes do fim.

| # | Tempo | Fala (o que você diz) | Enquadramento | Na tela (edição) |
|---|---|---|---|---|
| 1 | 0-3 s | "Esse modelo de voz tem 68 gigas. Minha placa tem 16. E ele roda." | Close, rosto no terço de cima, olhando na lente | Número grande "68 GB" batendo contra "16 GB" (o 68 não cabe na caixa e transborda) |
| 2 | 3-7 s | "Aqui, na minha máquina, sem nuvem. Com Docker e o resto aberto." | Médio: você e o monitor atrás | Gravação de tela: geração rodando + gerenciador de tarefas com o resto aberto |
| 3 | 7-12 s | "É o Drama 3, da Fish Audio: um modelo de voz com 35 bilhões de parâmetros." | Close | Áudio gerado tocando com a forma de onda; selo "Built with Fish Audio" |
| 4 | 12-18 s | "Na versão de 8 bits, do jeito que vem, ele leva doze minutos para falar seis segundos. E o SSD se arrastando a 144 megas por segundo." | Close, meio sorriso de "pois é" | Contador 12:05 correndo (rótulo "8 bits · 38 GB"); gráfico do disco a 144 MB/s, linha baixa |
| 5 | 18-24 s | "O gargalo é a leitura. Ele busca um pedaço do modelo de cada vez. Fila de banco com um caixa só." | Médio, mão mostrando "um de cada vez" | Animação: 256 caixinhas (especialistas), uma acende por vez |
| 6 | 24-32 s | "Então eu fiz ele pedir tudo de uma vez, e já ler a próxima camada enquanto calcula a atual." | Close | As caixinhas acendem em bloco; seta "próxima camada" lendo em paralelo. Disco sobe para 534 MB/s |
| 7 | 32-37 s | "Quatro vírgula quatro vezes mais rápido. Sem trocar de placa." | Close, pausa curta antes do número | Barra "× o tempo real" 116 → 26,5 (encolhe com ease, número conta; quanto menor, melhor) |
| 8 | 37-44 s | "E se eu peço seis versões da mesma frase de uma vez, cada pedaço lido serve as seis. Mais um ganho de 1,8 vez." | Médio | Seis ondas de áudio saindo do mesmo bloco |
| 9 | 44-52 s | "E o PC não trava. Eu deixo uns 3 gigas da placa livres e limito a memória dele. Medi enquanto gerava: o maior engasgo do sistema foi de 7 milissegundos." | Médio, você usando o PC (rolando o navegador) | Gravação de tela com você usando outro app enquanto gera; selo "atraso máx 7 ms" |
| 10 | 52-62 s | "Escuta a versão de 8 bits e a de 16." (pausa) | Close, você ouvindo | Toca 8 bits, depois 16 bits, com rótulo e tamanho (38 GB / 68 GB) |
| 11 | 62-68 s | "Eu não consegui dizer qual é melhor, e o Whisper transcreveu as duas certo. A de 8 bits lê bem menos dados, então fico com ela." | Close | Texto: "8 bits: 2 min 25 s · 16 bits: 5 min 02 s" |
| 12 | 68-75 s | "Doze minutos viraram dois e vinte e cinco. Método, patch e como medir estão no GitHub, link na descrição. Testou em outro modelo MoE? Me conta o número." | Close, aponta para baixo | Contador da cena 4 agora para em 2:25 (linha mestra); endereço do repositório |

Falas do bloco 10/11: **não diga** que uma soa melhor; a medição não sustenta isso (uma tomada por precisão).

### Variações de gancho (escolha uma; grave as três se der tempo)
1. Curiosidade (a de cima): "Esse modelo de voz tem 68 gigas. Minha placa tem 16. E ele roda."
2. Ganho: "Mesma placa de 16 gigas, 4,4 vezes mais rápido. Só mudei como ele lê o disco." (vale para a versão de 8 bits)
3. PC que não trava: "Rodei um modelo de voz gigante numa placa de 16 gigas e continuei usando o PC. Maior engasgo: 7 milissegundos."

### Variações do fecho
1. (a de cima) "Doze minutos viraram dois e vinte e cinco. [...] Me conta o número."
2. "Continua lento: dois minutos e vinte e cinco para seis segundos. Mas roda numa placa de 16 gigas. O passo a passo está no GitHub."

---

## 2. Versão longa (horizontal, ~5 min)

Mesmo tom, mais tela e mais explicação. Pode ler de um teleprompter, mas olhe para a lente.

| Bloco | Tempo | O que falar (pontos, não decore) | Na tela |
|---|---|---|---|
| Gancho | 0:00-0:20 | Cenas 1-3 da curta. "Vou mostrar o que eu mudei e quanto cada coisa rendeu, com números." | Igual à curta |
| A máquina | 0:20-0:45 | RTX 5060 Ti de 16 GB, 31 GB de RAM com WSL e Docker ligados (sobram 5 a 15 GB), SSD NVMe, Windows sem administrador. "Um PC normal de quem trabalha." | Foto/b-roll do gabinete; card com a ficha |
| O problema | 0:45-1:30 | Modelo MoE: 40 camadas, 256 "especialistas" em cada, só 8 usados por vez. O programa já deixa os especialistas no disco, mas lê um de cada vez. Versão de 8 bits (38 GB): 116× o tempo real, 12 minutos para 6 segundos; a de 16 bits (68 GB): 17 minutos. SSD a 144 MB/s num NVMe que faz vários GB/s. | Animação das caixinhas; gráfico do disco baixo |
| Truque 1: pré-busca | 1:30-2:30 | Pedir ao Windows todos os especialistas da camada de uma vez; ler a próxima camada enquanto a atual calcula; 4 threads de cópia. Ganho por degrau (8 bits): 1,49× (só threads), 2,3× (pedir em bloco), 2,44× (próxima camada), 4,4× com tudo junto. Na de 16 bits: 3,4× (17:18 → 5:02). | Escada de barras subindo, um degrau por frase |
| Truque 2: lote | 2:30-3:10 | Várias tomadas da mesma frase andando juntas: cada especialista lido serve a todas. 3 tomadas: 1,56×; 6 tomadas: 1,82×. Erro que eu cometi: guardar o estado de cada tomada na RAM comeu o ganho; na placa de vídeo, funcionou. | Seis ondas saindo do mesmo bloco; card "erro: estado na RAM" riscado |
| Truque 3: mapa quente | 3:10-3:35 | Guardar na placa os especialistas mais usados. Aqui rendeu só 4%, porque esse modelo espalha muito o uso. Conto porque é útil saber o que *não* funcionou tão bem. | Mapa de calor 40×256 bem espalhado |
| PC educado | 3:35-4:10 | Prioridade baixa de CPU, disco e memória; teto de 4 GB de RAM; placa com folga. Medi com outro programa quanto o sistema atrasava: no máximo 7 ms, nunca acima de 50. Custo de ser educado: uns 4% de velocidade. | Você usando o PC durante a geração; gráfico do atraso reto |
| Prova de ouvido | 4:10-4:35 | 8 bits contra 16 bits. Os dois o Whisper transcreveu certo; não dá para afirmar que um é melhor. O de 16 lê 2,4× mais dados por segundo de áudio. | Os dois áudios com rótulo |
| Limites | 4:35-4:50 | Uma máquina, uma frase, uma medida por configuração. Continua lento: 2 min 25 s para 6 s de fala em 8 bits. A graça é rodar. | Card com os limites |
| Fecho | 4:50-5:05 | "Doze minutos viraram dois e vinte e cinco. Método, patch e como medir estão no GitHub. Testou em outro modelo MoE? Me conta o número." | Contador parando em 2:25; endereço do repositório |

---

## 3. Gráficos para a edição (vão para a skill `animation` depois)

Movimento com ease (entrada `cubic-bezier(.22,1,.36,1)`), número que conta até o valor, um som curto e baixo em
cada número que aparece. Cores e fonte da marca na edição.

1. "68 GB" contra a caixa de "16 GB" (o número transborda).
2. Contador de tempo 12:05 → 2:25 (abre e fecha o vídeo).
3. Disco: 144 MB/s → 534 MB/s (medidor ou linha).
4. Caixinhas dos especialistas: uma por vez → em bloco → próxima camada em paralelo.
5. Escada de ganho (8 bits, × tempo real): 116,5 → 78,2 → 50,7 → 47,8 → 26,5 → lote 3: 17,7 → lote 6: 15,2.
6. 16 bits: 180,3 → 52,4 → lote 3: 43,2.
7. Atraso do sistema: linha reta perto de 0,7 ms, marca do máximo 7 ms, faixa "50 ms" vazia.
8. Cards: ficha da máquina; "8 bits: 38 GB · 2 min 25 s" e "16 bits: 68 GB · 5 min 02 s"; limites; repositório.

## 4. Gravação de tela e b-roll

- **Tela (OBS, 1080p ou 1440p, 30 fps):** terminal com a geração rodando; gerenciador de tarefas (aba Desempenho:
  GPU, disco, memória) ao lado; você abrindo navegador/planilha durante a geração; o `README` no GitHub rolando.
  Antes de gravar a tela, feche abas e janelas com nome de cliente, e-mail ou caminho de pasta pessoal.
- **Para a vertical:** grave a tela inteira; a edição recorta a parte que importa.
- **B-roll (celular, 4K 30 fps ou 1080p 60 fps):** gabinete/placa de vídeo de perto, LED do SSD, mão no
  mouse, monitor desfocado com o terminal, fone na cabeça ouvindo o áudio gerado. 5-8 s cada, câmera parada ou
  movimento lento e contínuo.

## 5. Como gravar em casa

- **Câmera:** celular na traseira (não a selfie), na horizontal para a longa e na vertical para a curta, na
  altura dos olhos, a ~1 m. Trave foco e exposição tocando e segurando no rosto. 30 fps.
- **Luz:** de frente ou a 45°, janela ou luminária grande e difusa (lençol branco na frente serve). Desligue a
  luz do teto (sombra no olho). Fundo um pouco mais escuro que o rosto; o monitor ligado atrás ajuda.
- **Áudio:** microfone de lapela no celular, ou o celular a meio metro da boca fora do quadro. Quarto com
  cortina, tapete ou cama (menos eco). Desligue ventilador e ar. Grave 10 s de silêncio do ambiente no começo
  (a edição usa para limpar ruído). Se o PC estiver gerando, o ventilador da placa sobe: deixe o micro longe dele.
- **Fala:** frase por frase; erre e repita a frase inteira na hora (a edição corta). Bata palma uma vez no começo
  de cada tomada (sincronia). Grave o gancho 3 vezes com energias diferentes.

## 6. O que entregar para a edição

| Arquivo | O que é |
|---|---|
| `curta_tomadas.mp4` (ou vários) | Câmera vertical, todas as tomadas, sem cortar |
| `longa_tomadas.mp4` | Câmera horizontal, todos os blocos |
| `tela_*.mp4` | Gravações de tela (geração, gerenciador de tarefas, uso do PC, GitHub) |
| `broll_*.mp4` | Imagens de apoio |
| `audio_lapela.wav` | Áudio do microfone separado, se gravou assim |
| `ambiente_silencio.wav` | Os 10 s de silêncio do quarto |
| `8bits.wav` e `16bits.wav` | Os dois áudios da comparação (mesma frase) |
| `README.md` e esta folha | Para os números e a ordem dos blocos |

Música e efeitos sonoros só licenciados (a edição escolhe).
