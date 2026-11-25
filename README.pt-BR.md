# moe-offload-desktop (português)

**Rodar um modelo *mixture of experts* maior que a VRAM *e* que a RAM livre num PC comum, sem travar o resto
do computador.**

Caso medido: **Drama 3** da Fish Audio, um TTS MoE de ~35B parâmetros (3B ativos por token, 40 camadas × 256
especialistas, 8 por token). O GGUF de 8 bits tem 38 GB e o de 16 bits, 68 GB. A máquina é um desktop comum,
que continua em uso durante a geração: RTX 5060 Ti de 16 GB (o modelo fica limitado a ~10,5 GB, sobrando ≥3 GB
para o resto), 31 GB de RAM com WSL/Docker e apps abertos (5–15 GB livres de fato), um SSD NVMe, Windows 11 sem
administrador.

O texto completo, com tabelas e passo a passo, está em inglês no [README.md](README.md); o método genérico em
[METHOD.md](METHOD.md).

## O problema
Nenhum dos dois arquivos cabe na VRAM nem na RAM livre. O [audio.cpp](https://github.com/0xShug0/audio.cpp) já
consegue deixar os especialistas no disco e trazê-los para um cache pequeno na GPU, mas devagar: **116× o tempo
real** em 8 bits (12 minutos para uma fala de 6 segundos) e **180×** em 16 bits. O SSD entregava ~150 MB/s,
porque cada especialista era lido por uma falha de página de cada vez.

## O que funcionou
| Técnica | Ganho medido |
|---|---|
| Pré-busca (pedir ao sistema todos os especialistas da camada de uma vez + ler a próxima camada em segundo plano) + 4 threads de cópia | **4,4×** (8 bits: 116,5 → 26,5× o tempo real); 16 bits: 180,3 → 52,4× (3,4×) |
| Lote (3 ou 6 tomadas em passo travado, estado de cada uma na VRAM) | 1,56× com 3, 1,82× com 6 (8 bits: até 15,2× o tempo real) |
| Mapa de especialistas quentes (fixos na VRAM + pré-lidos na RAM) | +4% (o roteador deste modelo espalha os pedidos) |
| Processo educado (prioridades baixas, teto de 4 GB de RAM) | custa ~4%; PC sem travada: atraso p99 de 0,7 ms, máximo 7 ms, nenhum acima de 50 ms |
| Compressão sem perda tipo DFloat11 | não se aplica (sem kernel no ggml; o original já é FP8) |

Tempo de parede para uma fala de ~6 s: 8 bits **12 min 05 s → 2 min 25 s**; 16 bits **17 min 18 s → 5 min 02 s**.
Qualidade: 8 e 16 bits foram transcritos certo pelo Whisper large-v3; com uma tomada por precisão, não dá para
afirmar que um soa melhor que o outro.

## Limites
Uma máquina, um modelo, uma frase curta, uma medida por configuração (diferença abaixo de ~5% é ruído); cache de
arquivos frio; lote só para tomadas da mesma frase; scripts de medição só no Windows. Continua lento em termos
absolutos: a graça é rodar um modelo deste tamanho numa placa de 16 GB sem largar o computador.

## Licenças
Código e textos: [Apache-2.0](LICENSE). O patch modifica o audio.cpp v0.9.6 (© 2026 ShugoAI LLC, Apache-2.0).
**Built with Fish Audio**: o Drama 3 segue a
[Fish Audio Community License v1.0](https://huggingface.co/fishaudio/drama-3/blob/main/LICENSE). Este
repositório não tem nem redistribui pesos ou áudios gerados; baixe o modelo da fonte oficial e siga a licença.
