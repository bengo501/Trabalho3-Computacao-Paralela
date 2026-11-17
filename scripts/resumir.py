"""mediana, minimo, maximo, dois speed-ups e a eficiencia.

le o csv da campanha. S = T1/Tp inclui o ganho do algoritmo.
Sdelta = T1_delta/Tp mede só o paralelismo. E = Sdelta/P, e na série
de 63 a 1023 o denominador são as 32 threads de hardware.
"""
import csv
import statistics
import sys
from collections import defaultdict

caminho = sys.argv[1] if len(sys.argv) > 1 else "results/runs.csv"
grupos = defaultdict(list)

with open(caminho, encoding="utf-8", newline="") as entrada:
    for linha in csv.DictReader(entrada):
        if linha["verificacao"] != "OK":
            sys.exit(f"verificacao diferente de OK: {linha}")
        chave = (
            linha["versao"],
            int(linha["n"]),
            int(linha["delta"]),
            int(linha["p"]),
            int(linha["yield"]),
        )
        grupos[chave].append(float(linha["tempo"]))


def med(xs):
    return statistics.median(xs)


def acha(versao, predicado):
    tempos = []
    for chave, xs in grupos.items():
        if chave[0] == versao and predicado(chave):
            tempos.extend(xs)
    return tempos


print("versao n delta p yield reps mediana minimo maximo")
for chave in sorted(grupos):
    xs = grupos[chave]
    print(
        f"{chave[0]} {chave[1]} {chave[2]} {chave[3]} {chave[4]} "
        f"{len(xs)} {med(xs):.4f} {min(xs):.4f} {max(xs):.4f}"
    )

t1s = acha("t1", lambda c: True)
if not t1s:
    sys.exit(0)
t1 = med(t1s)
n_ref = next(c[1] for c in grupos if c[0] == "t1")
print()
print(f"T1 mediana = {t1:.4f} s   n = {n_ref}   reps = {len(t1s)}")
print()
print("versao p yield Tp T1delta S Sdelta E ganho_algoritmo")

for chave in sorted(grupos):
    versao, n, delta, p, yield_ = chave
    if versao not in ("arvore", "balanceada"):
        continue
    tp = med(grupos[chave])
    if versao == "arvore":
        if delta == n:
            base = t1s
        else:
            base = acha("t1_delta", lambda c, d=delta: c[2] == d)
    else:
        base = acha("t1_balanceada", lambda c, pp=p: c[3] == pp)
    if not base or tp == 0:
        print(f"{versao} {p} {yield_} {tp:.4f} sem_referencia")
        continue
    t1d = med(base)
    s = t1 / tp
    sd = t1d / tp
    e = sd / (32 if p >= 63 else p)
    ganho = t1 / t1d if t1d else float("inf")
    print(
        f"{versao} {p} {yield_} {tp:.4f} {t1d:.4f} "
        f"{s:.3f} {sd:.3f} {e:.3f} {ganho:.3f}"
    )
