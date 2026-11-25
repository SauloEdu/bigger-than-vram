<div align="center">

# bigger-than-vram

**Rodar um modelo *mixture of experts* maior que a VRAM *e* que a RAM livre num PC comum,<br>
sem travar o resto do computador.**

[![Licença: Apache-2.0](https://img.shields.io/badge/licen%C3%A7a-Apache--2.0-blue)](LICENSE)
[![Runtime: audio.cpp v0.9.6](https://img.shields.io/badge/runtime-audio.cpp%20v0.9.6-orange)](https://github.com/0xShug0/audio.cpp)
[![Modelo: Fish Audio Drama 3](https://img.shields.io/badge/modelo-Fish%20Audio%20Drama%203-purple)](https://huggingface.co/fishaudio/drama-3)
[![Testado em: Windows 11 + CUDA](https://img.shields.io/badge/testado%20em-Windows%2011%20%2B%20CUDA-0078D6)](#máquina-de-teste)
[![Sem administrador](https://img.shields.io/badge/administrador-n%C3%A3o%20precisa-brightgreen)](#o-que-funcionou)
[![Sem pesos no repositório](https://img.shields.io/badge/pesos-n%C3%A3o%20inclu%C3%ADdos-lightgrey)](#licenças)

[![Ganho: 4,4x uma tomada](https://img.shields.io/badge/ganho-4%2C4%C3%97%20uma%20tomada-success)](#o-que-funcionou)
[![Ganho: 7,7x em 6 tomadas da mesma frase](https://img.shields.io/badge/ganho-7%2C7%C3%97%206%20tomadas%20da%20mesma%20frase-success)](#o-que-funcionou)
[![Disco: 144 para 534 MB/s](https://img.shields.io/badge/disco-144%20%E2%86%92%20534%20MB%2Fs-informational)](#o-que-funcionou)
[![Atraso p99 abaixo de 0,7 ms](https://img.shields.io/badge/atraso%20do%20PC%20p99-%3C0%2C7%20ms-brightgreen)](#o-que-funcionou)

[English (texto completo)](README.md) · [Método](METHOD.md) · [Patch](patches/) · [Scripts](scripts/)

</div>

---

## Em resumo

Um TTS MoE de **68 GB** (16 bits) e **38 GB** (8 bits) rodando numa placa de **16 GB**, com o computador em uso
normal durante a geração.

| | Antes | Depois | Ganho |
|---|:---:|:---:|:---:|
| **8 bits** (38 GB) · fala de 6,2 s, tempo de parede | 12 min 05 s | **2 min 45 s**¹ | **4,4× mais rápido** |
| **16 bits** (68 GB) · fala de 5,8 s, tempo de parede | 17 min 18 s | **5 min 02 s** | **3,4× mais rápido** |
| **8 bits**, 6 tomadas da *mesma* frase de uma vez² | 116,5× o tempo real | **15,2× o tempo real** | **7,7× mais rápido** |
| Pior atraso do sistema durante a geração, em todas as rodadas relatadas³ | — | **7 ms** no máximo, nenhum acima de 50 ms | PC continua usável |

<sub>¹ Mesma série e mesmas condições da referência. Melhor rodada: **2 min 25 s** (build final, 23,2× o tempo
real), uma medida só, então a diferença mistura o build final e a variação entre rodadas.<br>
² O lote gera várias tomadas (sementes diferentes) de uma frase só, e todas terminam juntas. Para frases
diferentes, como um roteiro de narração, o ganho é o de uma tomada: 4,4× em 8 bits e 3,4× em 16 bits.<br>
³ Uma rodada anterior da referência em 8 bits, sem o método, foi substituída pela referência relatada e não entra
nos resultados. Ela chegou a 399 ms de atraso máximo.</sub>

> [!NOTE]
> Todo número vem de uma rodada registrada (uma linha JSON por rodada), com o cache de arquivos do sistema frio.
> Uma máquina, um modelo, uma medida por configuração: veja os [limites](#limites).

## O problema

Caso medido: **Drama 3** da Fish Audio, um TTS MoE de ~35B parâmetros (3B ativos por token, 40 camadas × 256
especialistas, 8 por token).

<a id="máquina-de-teste"></a>

| Máquina de teste | |
|---|---|
| 🎮 GPU | RTX 5060 Ti de 16 GB (o modelo fica limitado a ~10,5 GB, sobrando ≥3 GB para o resto) |
| 🧠 RAM | 31 GB, com WSL/Docker e apps abertos (5–15 GB livres de fato) |
| 💾 Disco | um SSD NVMe |
| 🪟 Sistema | Windows 11, sem administrador |

Nenhum dos dois arquivos cabe na VRAM nem na RAM livre. O [audio.cpp](https://github.com/0xShug0/audio.cpp) já
consegue deixar os especialistas no disco e trazê-los para um cache pequeno na GPU, mas devagar: **116× o tempo
real** em 8 bits (12 minutos para uma fala de 6 segundos) e **180×** em 16 bits. O SSD entregava ~150 MB/s,
porque cada especialista era lido por uma falha de página de cada vez.

> Com os especialistas no disco, o gargalo é **ler especialistas**, não fazer conta.

```mermaid
flowchart LR
    SSD["💾 SSD NVMe<br/>modelo inteiro, 38/68 GB"] -->|pré-busca| RAM["🧠 cache de arquivos<br/>especialistas pré-lidos"]
    RAM -->|4 threads| VRAM["🎮 cache na GPU<br/>quentes, ~10,5 GB"]
    VRAM --> GPU["⚡ N tomadas<br/>dividem cada leitura"]
```

## O que funcionou

| # | Técnica | Ganho medido | O que faz |
|:-:|---|:---:|---|
| 1 | **Pré-busca** | **4,4×** em 8 bits · **3,4×** em 16 bits | Pede ao sistema todos os especialistas da camada de uma vez e lê a próxima camada em segundo plano; com 4 threads de cópia, o disco foi de 144 para 534 MB/s |
| 2 | **Lote** | **1,56×** (3 tomadas) · **1,82×** (6) | Várias tomadas da mesma frase, em passo travado, dividem cada leitura; o estado de cada uma fica na VRAM. 8 bits chega a 15,2× o tempo real |
| 3 | **Mapa de especialistas quentes** | +4% | Fixa os mais usados na VRAM e pré-lê os seguintes na RAM (o roteador deste modelo espalha os pedidos) |
| 4 | **Processo educado** | custa ~4% | Prioridades baixas e teto de 4 GB de RAM; atraso p99 de 0,7 ms, máximo 7 ms, nenhum acima de 50 ms |
| 5 | Compressão sem perda tipo DFloat11 | não se aplica | Sem kernel no ggml; o original já é FP8 |

Qualidade: 8 e 16 bits foram transcritos certo pelo Whisper large-v3; com uma tomada por precisão, não dá para
afirmar que um soa melhor que o outro.

📘 Tabelas completas e o passo a passo para reproduzir estão no [README em inglês](README.md); o método genérico,
para qualquer MoE em GGUF, no [METHOD.md](METHOD.md).

## Limites

- Uma máquina, um modelo, uma frase curta, **uma medida por configuração** (diferença abaixo de ~5% é ruído).
- Cache de arquivos frio; gerações seguidas são mais rápidas.
- Lote só para tomadas da mesma frase. Frases diferentes num lote precisariam de um prefill por frase; não
  implementado.
- Scripts de medição só no Windows.
- Continua lento em termos absolutos: a graça é rodar um modelo deste tamanho numa placa de 16 GB sem largar o
  computador.

## Trabalhos relacionados

Nenhuma ideia daqui é nova sozinha. O repositório é uma combinação testada, com números, a máquina e como
repetir.

- **llama.cpp `--override-tensor`** (`-ot`): deixa tensores escolhidos, em geral os especialistas, na RAM e
  calcula na CPU. Funciona quando os especialistas cabem na RAM; aqui nem na RAM livre cabem, então ficam no SSD e
  são calculados na GPU depois de lidos para um cache na VRAM.
- **[KTransformers](https://github.com/kvcache-ai/ktransformers)**: inferência híbrida CPU/GPU para LLMs MoE
  grandes, com os especialistas na CPU. Pressupõe muita RAM.
- **[PowerInfer](https://arxiv.org/abs/2312.12456)** (Song et al., 2023): neurônios mais ativados na GPU e o resto
  na CPU. O mapa de especialistas quentes é a mesma ideia no nível do especialista inteiro.
- **[LLM in a Flash](https://arxiv.org/abs/2312.11514)** (Alizadeh et al., Apple, 2023): lê pesos do
  armazenamento sob demanda, para aparelhos com pouca memória. É o mais parecido com este trabalho.
- **FlexGen** (Sheng et al., 2023): a ideia do lote.

O que muda aqui: um patch pequeno no [audio.cpp](https://github.com/0xShug0/audio.cpp) em vez de um motor novo,
um modelo de voz, um processo que mantém o PC usável (com o atraso medido) e sem precisar de administrador.

## Autor

Feito por **[Saulo Eduardo](https://github.com/SauloEdu)**, Beexbe Tecnologia e Inovação.
Se você roda modelos grandes em máquina comum ou quer ajuda num projeto assim, abra uma
[issue](https://github.com/SauloEdu/bigger-than-vram/issues) ou fale comigo no [LinkedIn](https://www.linkedin.com/in/sauloeduardo-beexbe).

## Licenças

- Código e textos: [Apache-2.0](LICENSE). O patch modifica o audio.cpp v0.9.6 (© 2026 ShugoAI LLC, Apache-2.0).
- **Built with Fish Audio**: o Drama 3 segue a
  [Fish Audio Community License v1.0](https://huggingface.co/fishaudio/drama-3/blob/main/LICENSE).
- Este repositório não tem nem redistribui pesos ou áudios gerados; baixe o modelo da fonte oficial e siga a
  licença.
