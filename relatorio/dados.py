"""Números da campanha. Relatório e slides leem daqui para não divergir."""

import csv
import statistics
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
CSV = RAIZ / "results" / "runs.csv"

PS_ARVORE = (1, 3, 7, 15, 31)
PS_BALANCEADA = (2, 4, 8, 16, 32, 31)
PS_OVER = (63, 127, 255, 511, 1023)


def tempo(x):
    return f"{x:.3f}".replace(".", ",")


def razao(x):
    return f"{x:.2f}".replace(".", ",")


def frac(x):
    return f"{x:.3f}".replace(".", ",")


def ms(x):
    return f"{x * 1000:.1f}".replace(".", ",")


def ler(caminho=CSV):
    grupos = {}
    with caminho.open(encoding="utf-8", newline="") as arquivo:
        for linha in csv.DictReader(arquivo):
            if linha["verificacao"] != "OK":
                raise SystemExit(f"execucao com verificacao diferente de OK: {linha}")
            chave = (
                linha["versao"],
                int(linha["p"]),
                int(linha["delta"]),
                int(linha["yield"]),
            )
            grupos.setdefault(chave, []).append(float(linha["tempo"]))
            grupos.setdefault("_n", set()).add(int(linha["n"]))
    return grupos


def fechar(grupos, versao, p, yield_=0, delta=None):
    candidatos = [
        chave
        for chave in grupos
        if chave != "_n"
        and chave[0] == versao
        and chave[1] == p
        and chave[3] == yield_
        and (delta is None or chave[2] == delta)
    ]
    if len(candidatos) != 1:
        return None
    tempos = grupos[candidatos[0]]
    if len(tempos) != 10:
        return None
    return {
        "med": statistics.median(tempos),
        "min": min(tempos),
        "max": max(tempos),
        "delta": candidatos[0][2],
    }


def linha_speedup(p, tp, t1, t1d, divisor):
    s = t1 / tp["med"]
    sd = t1d / tp["med"]
    return {
        "p": p,
        "med": tempo(tp["med"]),
        "min": tempo(tp["min"]),
        "max": tempo(tp["max"]),
        "t1d": tempo(t1d),
        "s": razao(s),
        "sd": razao(sd),
        "e": razao(sd / divisor),
        "ganho": razao(t1 / t1d),
        "tp": tp["med"],
        "tp_min": tp["min"],
        "tp_max": tp["max"],
        "t1d_f": t1d,
        "s_f": s,
        "sd_f": sd,
        "e_f": sd / divisor,
        "ganho_f": t1 / t1d,
        "delta": tp["delta"],
    }


def contexto(caminho=CSV):
    if not caminho.exists():
        raise SystemExit(f"nao achei {caminho}")
    grupos = ler(caminho)
    ns = grupos.pop("_n")
    if len(ns) != 1:
        raise SystemExit(f"o csv mistura valores de n: {sorted(ns)}")
    n = ns.pop()
    t1 = fechar(grupos, "t1", 1)
    if t1 is None:
        raise SystemExit("T1 ainda nao tem 10 repeticoes com verificacao OK")

    arvore = []
    for p in PS_ARVORE:
        tp = fechar(grupos, "arvore", p)
        if tp is None:
            continue
        if p == 1:
            t1d = t1["med"]
        else:
            ref = fechar(grupos, "t1_delta", p, delta=tp["delta"])
            if ref is None:
                continue
            t1d = ref["med"]
        arvore.append(linha_speedup(p, tp, t1["med"], t1d, p))

    balanceada = []
    for p in PS_BALANCEADA:
        tp = fechar(grupos, "balanceada", p)
        ref = fechar(grupos, "t1_balanceada", p)
        if tp is None or ref is None:
            continue
        balanceada.append(linha_speedup(p, tp, t1["med"], ref["med"], p))

    over = []
    for p in PS_OVER:
        ref = fechar(grupos, "t1_delta", p)
        ativa = fechar(grupos, "arvore", p, yield_=0)
        cede = fechar(grupos, "arvore", p, yield_=1)
        if ref is None or ativa is None or cede is None:
            continue
        over.append(
            {
                "p": p,
                "t1d": tempo(ref["med"]),
                "t1d_f": ref["med"],
                "ativa": linha_speedup(p, ativa, t1["med"], ref["med"], 32),
                "yield": linha_speedup(p, cede, t1["med"], ref["med"], 32),
            }
        )

    folhas = {p: (p + 1) // 2 for p in PS_ARVORE}
    previsto = {p: t1["med"] / (folhas[p] ** 2) for p in PS_ARVORE}
    return {
        "n": n,
        "t1": t1["med"],
        "t1_min": t1["min"],
        "t1_max": t1["max"],
        "t1_txt": tempo(t1["med"]),
        "t1_min_txt": tempo(t1["min"]),
        "t1_max_txt": tempo(t1["max"]),
        "arvore": arvore,
        "balanceada": balanceada,
        "over": over,
        "previsto": previsto,
        "p1_diff": abs(t1["med"] - arvore[0]["tp"]) if arvore and arvore[0]["p"] == 1 else None,
    }


def outras(caminho=CSV):
    """Campanhas mais longas, se os csv já existirem."""
    raiz = caminho.parent
    achadas = []
    for nome, pasta in (("2 min", "medio"), ("5 min", "longo")):
        arquivo = raiz / pasta / "runs.csv"
        if arquivo.exists():
            achadas.append((nome, contexto(arquivo)))
    return achadas


if __name__ == "__main__":
    ctx = contexto()
    print("n", ctx["n"], "T1", ctx["t1_txt"])
    for linha in ctx["arvore"]:
        prev = ctx["previsto"][linha["p"]]
        print(
            "arvore",
            linha["p"],
            linha["med"],
            "Sd",
            linha["sd"],
            "E",
            linha["e"],
            "ganho",
            linha["ganho"],
            "previsto",
            tempo(prev),
            "diff_ms",
            ms(linha["tp"] - prev),
        )
    print("balanceada", len(ctx["balanceada"]), "over", len(ctx["over"]))
