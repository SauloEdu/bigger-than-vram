"""Transforma o uso de especialistas (AUDIOCPP_MOE_STATS) num mapa quente por camada.
Uso: python -I -B mapa_quente.py <uso.csv> <mapa.csv> <n_vram_por_camada> <n_ram_por_camada>
Os n_vram mais pedidos de cada camada ficam fixos na VRAM; os n_ram seguintes são pré-lidos para a RAM
(cache de arquivos do sistema); o resto é lido do SSD sob demanda. Imprime a cobertura: a fração dos pedidos
que cai em cada nível, que é o teto de acertos que o mapa pode dar."""
import csv
import sys
from collections import defaultdict


def main():
    origem, destino, n_vram, n_ram = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    por_camada = defaultdict(list)
    with open(origem, encoding="utf-8") as f:
        for linha in csv.DictReader(f, delimiter=";"):
            por_camada[int(linha["group"])].append((int(linha["requests"]), int(linha["expert"])))
    total = vram = ram = 0
    with open(destino, "w", encoding="utf-8") as f:
        f.write("# camada;especialista;nivel\n")
        for camada in sorted(por_camada):
            ordem = sorted(por_camada[camada], reverse=True)
            total += sum(p for p, _ in ordem)
            for i, (pedidos, especialista) in enumerate(ordem[:n_vram + n_ram]):
                nivel = "vram" if i < n_vram else "ram"
                vram += pedidos if nivel == "vram" else 0
                ram += pedidos if nivel == "ram" else 0
                f.write(f"{camada};{especialista};{nivel}\n")
    print(f"camadas={len(por_camada)} pedidos={total} cobertura_vram={vram / total:.1%} "
          f"cobertura_ram={ram / total:.1%} resto_ssd={(total - vram - ram) / total:.1%}")


if __name__ == "__main__":
    main()
