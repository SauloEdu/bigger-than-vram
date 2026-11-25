"""Roda uma geração do audio.cpp (TTS MoE com especialistas no disco) com prioridade baixa e teto de memória,
e mede tempo, VRAM, RAM, IO e o impacto no resto do sistema.

Uso (python com psutil e soundfile):
  python -I -B rodar.py --cli audiocpp_cli.exe --modelo m.gguf --saida pasta --rotulo nome --texto "..."
      [--ref voz.wav] [--semente 1] [--takes 1] [--cache 32] [--threads 8] [--read-threads 1]
      [--prefetch 0|1|2] [--hotmap mapa.csv] [--warm-mb 0] [--stats uso.csv] [--teto-ram-gb 8]
      [--familia fish_drama3] [--opcao chave=valor ...]
Grava <saida>/<rotulo>.wav (ou take_01..NN.wav), <rotulo>.log e uma linha JSON em <saida>/medidas.jsonl.

Técnicas aplicadas ao processo (sem administrador):
- prioridade de CPU BelowNormal, prioridade de IO "low" e prioridade de memória baixa (páginas dele saem primeiro);
- teto de memória comprometida (privada) por Job Object: estourou, o processo falha em vez de o Windows paginar.
Impacto no sistema: um processo separado, em prioridade normal, mede o atraso de um sleep de 10 ms (proxy de travada
de interface) antes (linha de base) e durante a geração; também se registram RAM disponível mínima, crescimento do
arquivo de paginação e leitura/latência média do disco do sistema.
"""
import argparse
import ctypes
import json
import os
import re
import statistics
import subprocess
import sys
import threading
import time
from ctypes import wintypes
from pathlib import Path

import psutil
import soundfile as sf

INTERVALO_S = 0.5
JITTER_SLEEP_S = 0.010
BASE_S = 15
MB = 2**20

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
ntdll = ctypes.WinDLL("ntdll")
kernel32.CreateJobObjectW.restype = wintypes.HANDLE
kernel32.OpenProcess.restype = wintypes.HANDLE
kernel32.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
kernel32.QueryInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD, ctypes.c_void_p]
kernel32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
kernel32.SetProcessWorkingSetSizeEx.argtypes = [wintypes.HANDLE, ctypes.c_size_t, ctypes.c_size_t, wintypes.DWORD]
kernel32.SetProcessInformation.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
ntdll.NtSetInformationProcess.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.ULONG]


class IoCounters(ctypes.Structure):
    _fields_ = [(n, ctypes.c_ulonglong) for n in ("r_ops", "w_ops", "o_ops", "r_bytes", "w_bytes", "o_bytes")]


class BasicLimit(ctypes.Structure):
    _fields_ = [("PerProcessUserTimeLimit", ctypes.c_longlong), ("PerJobUserTimeLimit", ctypes.c_longlong),
                ("LimitFlags", wintypes.DWORD), ("MinimumWorkingSetSize", ctypes.c_size_t),
                ("MaximumWorkingSetSize", ctypes.c_size_t), ("ActiveProcessLimit", wintypes.DWORD),
                ("Affinity", ctypes.c_size_t), ("PriorityClass", wintypes.DWORD), ("SchedulingClass", wintypes.DWORD)]


class ExtendedLimit(ctypes.Structure):
    _fields_ = [("BasicLimitInformation", BasicLimit), ("IoInfo", IoCounters),
                ("ProcessMemoryLimit", ctypes.c_size_t), ("JobMemoryLimit", ctypes.c_size_t),
                ("PeakProcessMemoryUsed", ctypes.c_size_t), ("PeakJobMemoryUsed", ctypes.c_size_t)]


QUOTA_HARDWS_MAX_ENABLE = 0x4
QUOTA_HARDWS_MIN_DISABLE = 0x2
JOB_LIMIT_PROCESS_MEMORY = 0x100
WS_MINIMO = 64 * 2**20
JOB_LIMIT_KILL_ON_CLOSE = 0x2000
JOB_EXTENDED_LIMIT_INFO = 9
PROCESS_ALL_ACCESS = 0x1FFFFF
PROCESS_IO_PRIORITY = 33
IO_PRIORITY_LOW = 1
PROCESS_MEMORY_PRIORITY = 0
MEMORY_PRIORITY_LOW = 2


def limitar(pid, teto_ws, teto_commit):
    """Prende o processo num Job Object com teto de RAM (working set) e de memória comprometida, e baixa as
    prioridades de IO e memória. No Windows (WDDM) a VRAM alocada também conta como memória comprometida do
    processo, por isso o teto de commit é RAM + VRAM; o que limita a RAM de verdade é o teto de working set."""
    job = kernel32.CreateJobObjectW(None, None)
    info = ExtendedLimit()
    info.BasicLimitInformation.LimitFlags = JOB_LIMIT_PROCESS_MEMORY | JOB_LIMIT_KILL_ON_CLOSE
    info.ProcessMemoryLimit = teto_commit
    if not kernel32.SetInformationJobObject(job, JOB_EXTENDED_LIMIT_INFO, ctypes.byref(info), ctypes.sizeof(info)):
        raise OSError(ctypes.get_last_error(), "SetInformationJobObject")
    handle = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    if not kernel32.AssignProcessToJobObject(job, handle):
        raise OSError(ctypes.get_last_error(), "AssignProcessToJobObject")
    # Teto rígido de working set por processo (o limite de working set do Job exige privilégio de administrador).
    if not kernel32.SetProcessWorkingSetSizeEx(handle, ctypes.c_size_t(WS_MINIMO), ctypes.c_size_t(teto_ws),
                                               QUOTA_HARDWS_MAX_ENABLE | QUOTA_HARDWS_MIN_DISABLE):
        raise OSError(ctypes.get_last_error(), "SetProcessWorkingSetSizeEx")
    io = ctypes.c_ulong(IO_PRIORITY_LOW)
    status = ntdll.NtSetInformationProcess(handle, PROCESS_IO_PRIORITY, ctypes.byref(io), ctypes.sizeof(io))
    if status != 0:
        raise OSError(status, "NtSetInformationProcess(IoPriority)")
    mem = ctypes.c_ulong(MEMORY_PRIORITY_LOW)
    if not kernel32.SetProcessInformation(handle, PROCESS_MEMORY_PRIORITY, ctypes.byref(mem), ctypes.sizeof(mem)):
        raise OSError(ctypes.get_last_error(), "SetProcessInformation(MemoryPriority)")
    return job, handle


def pico_job(job):
    info = ExtendedLimit()
    kernel32.QueryInformationJobObject(job, JOB_EXTENDED_LIMIT_INFO, ctypes.byref(info), ctypes.sizeof(info), None)
    return info.PeakProcessMemoryUsed


def vram_mb():
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                       capture_output=True, text=True, check=True)
    return int(r.stdout.strip().splitlines()[0])


def atrasos(parar, saida):
    """Atraso (ms) de um sleep de 10 ms numa thread de prioridade normal: sobe quando o sistema engasga."""
    while not parar.is_set():
        t0 = time.perf_counter()
        time.sleep(JITTER_SLEEP_S)
        saida.append((time.perf_counter() - t0 - JITTER_SLEEP_S) * 1000)


def sonda(arquivo_parar, arquivo_saida):
    """Processo separado (prioridade normal, sem as threads de medição): mede atrasos até existir arquivo_parar."""
    valores, parar = [], threading.Event()
    th = threading.Thread(target=atrasos, args=(parar, valores))
    th.start()
    while not Path(arquivo_parar).exists():
        time.sleep(0.2)
    parar.set()
    th.join()
    Path(arquivo_saida).write_text(json.dumps(resumo_atrasos(valores)), encoding="utf-8")


def iniciar_sonda(pasta, nome):
    parar, saida = pasta / f"{nome}.parar", pasta / f"{nome}.json"
    parar.unlink(missing_ok=True)
    proc = subprocess.Popen([sys.executable, "-I", "-B", __file__, "--sonda", str(parar), str(saida)])
    return proc, parar, saida


def encerrar_sonda(sonda):
    proc, parar, saida = sonda
    parar.write_text("", encoding="utf-8")
    proc.wait()
    resultado = json.loads(saida.read_text(encoding="utf-8"))
    parar.unlink()
    saida.unlink()
    return resultado


def resumo_atrasos(valores):
    if not valores:
        return {}
    v = sorted(valores)
    return {"p50_ms": round(v[len(v) // 2], 2), "p99_ms": round(v[int(len(v) * 0.99)], 2), "max_ms": round(v[-1], 2),
            "acima_50ms": sum(x > 50 for x in v)}


def medir(proc, pico, parar):
    p = psutil.Process(proc.pid)
    p.cpu_percent()
    cpus = []
    while proc.poll() is None and not parar.is_set():
        try:
            mem = p.memory_full_info()
            pico["ws"] = max(pico["ws"], mem.rss)
            pico["privada"] = max(pico["privada"], mem.uss)
            pico["commit"] = max(pico["commit"], mem.private)
            cpus.append(p.cpu_percent() / psutil.cpu_count())
            pico["io_leitura"] = p.io_counters().read_bytes
        except psutil.Error:
            break
        pico["vram"] = max(pico["vram"], vram_mb())
        pico["ram_livre_min"] = min(pico["ram_livre_min"], psutil.virtual_memory().available)
        pico["pagefile_max"] = max(pico["pagefile_max"], psutil.swap_memory().used)
        time.sleep(INTERVALO_S)
    pico["cpu"] = statistics.mean(cpus[2:]) if len(cpus) > 2 else 0


def esfriar(arquivo, gigas):
    """Tira o modelo do cache de arquivos do Windows sem administrador: lê outro arquivo grande em sequência.
    As páginas do modelo ficaram com prioridade de memória baixa, então saem primeiro."""
    bloco = 64 * MB
    with open(arquivo, "rb", buffering=0) as f:
        for _ in range(int(gigas * 1024 * MB / bloco)):
            if not f.read(bloco):
                break


def disco():
    return psutil.disk_io_counters()


def resumo_disco(antes, depois, segundos):
    leituras = depois.read_count - antes.read_count
    return {"disco_lido_mb": round((depois.read_bytes - antes.read_bytes) / MB),
            "disco_mb_s": round((depois.read_bytes - antes.read_bytes) / MB / segundos, 1),
            "latencia_leitura_media_ms": round((depois.read_time - antes.read_time) / leituras, 2) if leituras else None}


def metricas_log(texto):
    chaves = {}
    for m in re.finditer(r"((?:disk_experts|drama3|session)\.[\w.]+)[\s=:]+([-\d.]+)\s*$", texto, re.M):
        chaves[m.group(1)] = chaves.get(m.group(1), 0) + float(m.group(2))
    return chaves


def main():
    if len(sys.argv) == 4 and sys.argv[1] == "--sonda":
        sonda(sys.argv[2], sys.argv[3])
        return
    a = argparse.ArgumentParser()
    a.add_argument("--cli", required=True)
    a.add_argument("--modelo", required=True)
    a.add_argument("--saida", required=True)
    a.add_argument("--rotulo", required=True)
    a.add_argument("--texto", required=True)
    a.add_argument("--ref")
    a.add_argument("--familia", default="fish_drama3")
    a.add_argument("--semente", default="1")
    a.add_argument("--takes", type=int, default=1)
    a.add_argument("--cache", type=int, default=32)
    a.add_argument("--threads", default="8")
    a.add_argument("--read-threads", type=int, default=1)
    a.add_argument("--prefetch", type=int, default=0)
    a.add_argument("--hotmap")
    a.add_argument("--warm-mb", type=int, default=0)
    a.add_argument("--stats")
    a.add_argument("--teto-ram-gb", type=float, default=8, help="teto de working set (RAM física do processo)")
    a.add_argument("--teto-commit-gb", type=float, default=24, help="teto de memória comprometida (RAM + VRAM no WDDM)")
    a.add_argument("--max-tokens", default="300")
    a.add_argument("--opcao", action="append", default=[])
    a.add_argument("--sem-base", action="store_true", help="pula a medição de linha de base do sistema")
    a.add_argument("--esfriar-arquivo", help="arquivo grande lido antes da geração para começar com o cache frio")
    a.add_argument("--esfriar-gb", type=float, default=14)
    arg = a.parse_args()

    pasta = Path(arg.saida)
    pasta.mkdir(parents=True, exist_ok=True)
    saida_wav = pasta / f"{arg.rotulo}.wav"
    log_arq = pasta / f"{arg.rotulo}.log"
    log_arq.unlink(missing_ok=True)   # o --log-file acrescenta
    cmd = [arg.cli, "--task", "tts", "--family", arg.familia, "--backend", "cuda", "--mode", "offline",
           "--model", arg.modelo, "--text", arg.texto, "--seed", arg.semente, "--threads", arg.threads,
           "--metrics", "--log-file", str(log_arq), "--out", str(saida_wav),
           "--session-option", "moe_disk_experts=true", "--session-option", f"moe_expert_cache_size={arg.cache}",
           "--session-option", "moe_cpu_expert_layers=0",
           "--session-option", f"moe_disk_expert_read_threads={arg.read_threads}",
           "--request-option", f"max_tokens={arg.max_tokens}"]
    if arg.ref:
        ref_txt = Path(arg.ref).with_suffix(".txt").read_text(encoding="utf-8").split(";", 1)[-1].strip()
        cmd += ["--voice-ref", arg.ref, "--request-option", f"reference_text={ref_txt}"]
    if arg.takes > 1:
        cmd += ["--request-option", f"batch_takes={arg.takes}", "--out-dir", str(pasta / arg.rotulo)]
    for o in arg.opcao:
        cmd += ["--session-option" if o.split("=", 1)[0].startswith((arg.familia + ".", "moe_")) else "--request-option", o]
    env = dict(os.environ, AUDIOCPP_MOE_PREFETCH=str(arg.prefetch), AUDIOCPP_MOE_WARM_MB=str(arg.warm_mb))
    for chave, valor in (("AUDIOCPP_MOE_HOTMAP", arg.hotmap), ("AUDIOCPP_MOE_STATS", arg.stats)):
        if valor:
            env[chave] = str(valor)

    if arg.esfriar_arquivo:
        esfriar(arg.esfriar_arquivo, arg.esfriar_gb)
    base = {}
    if not arg.sem_base:
        s = iniciar_sonda(pasta, f"{arg.rotulo}.base")
        time.sleep(BASE_S)
        base = encerrar_sonda(s)

    disco_antes = disco()
    pagefile_base = psutil.swap_memory().used
    vram_base = vram_mb()
    pico = {"ws": 0, "privada": 0, "commit": 0, "vram": 0, "io_leitura": 0, "ram_livre_min": psutil.virtual_memory().available,
            "pagefile_max": pagefile_base}
    parar = threading.Event()
    s_durante = iniciar_sonda(pasta, f"{arg.rotulo}.durante")
    t0 = time.time()
    proc = None
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8",
                                errors="replace", env=env, creationflags=subprocess.BELOW_NORMAL_PRIORITY_CLASS)
        job, _ = limitar(proc.pid, int(arg.teto_ram_gb * 2**30), int(arg.teto_commit_gb * 2**30))
    except OSError:
        # BUG-MED-001: sem isto a sonda (outro processo) ficava esperando o arquivo de parada para sempre.
        if proc:
            proc.kill()
        encerrar_sonda(s_durante)
        raise
    threads = [threading.Thread(target=medir, args=(proc, pico, parar))]
    for th in threads:
        th.start()
    saida = proc.communicate()[0]
    parede = time.time() - t0
    parar.set()
    for th in threads:
        th.join()
    durante = encerrar_sonda(s_durante)
    sistema = resumo_disco(disco_antes, disco(), parede)
    sistema["pagefile_cresceu_mb"] = round((pico["pagefile_max"] - pagefile_base) / MB)
    (pasta / f"{arg.rotulo}.saida.txt").write_text(saida, encoding="utf-8")
    log = log_arq.read_text(encoding="utf-8", errors="replace") if log_arq.exists() else ""
    wavs = sorted((pasta / arg.rotulo).glob("take_*.wav")) if arg.takes > 1 else [saida_wav]
    audio = sum(sf.info(w).duration for w in wavs if w.exists())
    linha = {
        "rotulo": arg.rotulo, "modelo": Path(arg.modelo).name, "takes": arg.takes, "cache": arg.cache,
        "read_threads": arg.read_threads, "prefetch": arg.prefetch, "hotmap": bool(arg.hotmap), "warm_mb": arg.warm_mb,
        "codigo_saida": proc.returncode, "parede_s": round(parede, 1), "audio_s": round(audio, 2),
        "x_tempo_real": round(parede / audio, 1) if audio else None,
        "vram_pico_mb": pico["vram"] - vram_base, "vram_base_mb": vram_base,
        "ram_ws_pico_mb": round(pico["ws"] / MB), "ram_privada_ws_pico_mb": round(pico["privada"] / MB),
        "commit_pico_mb": round(max(pico["commit"], pico_job(job)) / MB), "teto_ram_gb": arg.teto_ram_gb,
        "teto_commit_gb": arg.teto_commit_gb,
        "io_lido_mb": round(pico["io_leitura"] / MB), "io_mb_s": round(pico["io_leitura"] / MB / parede, 1),
        "ram_livre_min_mb": round(pico["ram_livre_min"] / MB), "cpu_medio_pct": round(pico["cpu"], 1),
        "atraso_base": base, "atraso_durante": durante,
        "sistema": sistema, "log": metricas_log(log),
    }
    with open(pasta / "medidas.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(linha, ensure_ascii=False) + "\n")
    print(json.dumps(linha, ensure_ascii=False), flush=True)
    if proc.returncode != 0:
        sys.exit(f"ERRO {proc.returncode}: {saida.strip().splitlines()[-1] if saida.strip() else ''}")


if __name__ == "__main__":
    main()
