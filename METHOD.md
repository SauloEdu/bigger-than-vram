# Running a large MoE on a small GPU without freezing the PC

A generic method for running *mixture-of-experts* (MoE) models in GGUF whose weights fit neither in VRAM nor in
free RAM, reading experts from the SSD on demand, on a PC that stays in use. It was measured on a ~35B-parameter
MoE TTS (3B active per token, 40 layers × 256 experts, 8 per token) on a 16 GB GPU with only ~10 GB of free RAM,
but nothing here depends on that model: it applies to any ggml/GGUF runtime with an expert cache (audio.cpp has
one; llama.cpp has similar paths).

## The idea in one sentence

In a MoE with experts on disk, the bottleneck is **reading experts**, not computing. Each technique below attacks
one part of the reading: read fewer times (batching), read before it is needed (prefetch), read from the fastest
place (hot map per memory tier) and read fewer bytes (quantization / compression). And the process runs
"politely": low priority and a memory cap, so the rest of the PC does not feel it.

## First: measure the baseline

1. Generate a short output with the simplest configuration that works: all experts read from the GGUF via `mmap`
   into a bounded GPU cache (`moe_disk_experts=true`, `moe_expert_cache_size=N`).
2. Record: wall time / output duration (× real time), VRAM peak (nvidia-smi minus usage before starting), peak
   private RAM and working set, bytes read from disk, and how late a `sleep(10 ms)` wakes up in a normal-priority
   thread of **another process** (proxy for "did the UI stutter?"), before and during.
3. Size the cache by VRAM, not by speed: `cache_slots × bytes_per_expert × layers` + dense weights + KV + graphs
   must stay under the budget (here, total VRAM − 3 GB free).

## Technique 1: batching (several sequences together)

Inspired by FlexGen (Sheng et al., 2023): when the cost is bringing weights in, process the largest possible
batch with each weight brought in. In a MoE, each step of each layer asks for *k* experts per sequence; with N
sequences moving together, the layer asks for the **union** of the N sets, and each expert read serves every
sequence that asked for it.

Minimal implementation (no kernel rewrite): N decoding sessions sharing the weights and the expert cache,
advanced in lockstep: at step t, all N run layers 0..L before step t+1. Per-sequence state (KV cache, recurrent
state, sampler, history) stays separate **and in VRAM** (swapping it through RAM every step ate the gain).
The expert cache must hold the union: `cache_slots >= k × N` (or close, since sequences repeat many experts).

When to use: several takes (seeds) of the same input, or several different inputs at once. Compare time per
second of output with batch 1 and batch N; the gain comes from expert overlap between sequences.

## Technique 2: prefetch

Two levels, neither changes the file format:
- **Within the layer**: before copying the missing experts out of the `mmap`, ask the OS for all of them at once
  (`PrefetchVirtualMemory` on Windows, `madvise(MADV_WILLNEED)` on Linux). Instead of one page fault at a time,
  the SSD receives several large reads in parallel (deeper queue).
- **Next layer**: while layer L computes, a background thread asks the OS for the experts layer L+1 used on the
  previous step (routing changes little between steps). When layer L+1 needs them, they are already in the OS
  file cache. Stale predictions are dropped, not queued.

## Technique 3: hot map per memory tier

1. Run a generation representative of real use, recording per layer how many times each expert was requested.
2. Per layer: the most requested stay **pinned in VRAM** (never evicted while there is another victim), the next
   ones are **pre-read into RAM** (the OS file cache, within a budget) and the rest comes from SSD on demand.
3. Why RAM means the file cache and not pinned memory: clean file pages are dropped by the OS when another program
   needs memory, without writing anything to the page file. Pinned memory would compete with the user's apps.
4. Leave enough slots in the VRAM cache for non-pinned experts (here, pinned <= slots − 16).

`scripts/hot_map.py` prints the **coverage** of each tier (fraction of requests that land in it): that is the
ceiling of the gain. Concentrated distribution (few experts do most of the work) = big gain; flat = small.

## Technique 4: lossless compression (DFloat11-style)

DFloat11 compresses BF16 weights to ~70% losslessly (Huffman-codes the exponent) and decompresses on the GPU.
It only helps if the runtime has the decompression kernel; a ggml/GGUF runtime does not (official DFloat11 is
for PyTorch/CUDA). Before going there, check the source precision: if the official checkpoint is FP8 with block
scales (as here), the "16-bit" version holds no more information than the FP8; the most compact lossless format is
FP8 itself, and Q8_0 is one step away from it.

## Technique 5: polite process

- CPU priority `BelowNormal`, low I/O priority and low memory priority (its pages leave first). All as a normal
  user.
- Hard working-set cap (`SetProcessWorkingSetSizeEx`) and a commit cap through a Job Object: if exceeded, the
  process fails instead of Windows paging out the user's apps.
- Few CPU threads (performance cores only), because the bottleneck is I/O.
- Measure the impact: `sleep(10 ms)` lag (p50/p99/max), page-file growth, minimum available RAM and disk read
  latency during generation.

## Recipe for another MoE model

1. Convert the official checkpoint with the runtime's official converter; quantize experts and the rest
   separately (routers in original precision: they are small and decide what gets read).
2. Turn on disk experts and find the largest cache that respects the VRAM budget.
3. Measure the baseline (section above).
4. Turn on prefetch level 1, then 2; record each gain separately.
5. Record expert usage on a representative generation, build the hot map, run again with it.
6. Run in batches (N = 3, 6, ...) and compare time per second of output.
7. Always keep the low priorities and the memory cap; check system lag.

## Lessons that apply to any model

- **Measure the reading first.** Reading experts by page fault, one at a time, gave ~150 MB/s on an NVMe that
  does several GB/s. Asking for all blocks at once and copying in parallel was the biggest gain (4×); no "clever"
  technique makes up for serial reads.
- **Per-sequence state stays on the GPU.** The first batching version swapped KV/recurrent state through RAM every
  step and lost almost all of the gain; with copies in VRAM (~150 MB per sequence) batching gave 1.6–1.8×.
- **A RAM cap is a working-set cap, not a commit cap.** On Windows (WDDM) allocated VRAM counts as process commit;
  capping that kills loading. Mapped model pages count in the working set and stop counting as "available"; a hard
  working-set cap (here 4 GB) keeps RAM free for other programs at a ~4% speed cost. Large batches prefer a
  slightly higher cap.
- **The freeze probe must be another process.** Measuring inside the process that also calls monitoring tools
  reports stutters caused by the measurement itself.
- **Usage distribution decides the value of the hot map.** If the 16 most used experts per layer cover only ~1/3
  of requests (spread-out router), pinning them gives little; batching gives more, because it exploits overlap at
  the same instant.
- **Check what quantization really produced.** Some converters do not apply the default type to 3D tensors
  (expert banks) or to the embedding; check per-tensor types and the final size before measuring.
