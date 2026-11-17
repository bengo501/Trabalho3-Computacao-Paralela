"""escolhe n para o bubble sort do vetor inteiro ficar entre 30 e 60 s.

le linhas 'n tempo'. imprime o n escolhido.
sai com 0 quando a escolha já foi medida.
sai com 2 quando o n impresso ainda precisa ser medido.
"""
import math
import sys

amostras = []
for linha in open(sys.argv[1], encoding="utf-8"):
    linha = linha.strip()
    if not linha or linha.startswith("#"):
        continue
    n, tempo = linha.split()
    amostras.append((int(n), float(tempo)))

if not amostras:
    sys.exit(1)

dentro = [(n, t) for n, t in amostras if 30.0 <= t <= 60.0]
if dentro:
    n, t = min(dentro, key=lambda nt: abs(nt[1] - 45.0))
    print(n)
    print(f"medido {t:.3f} s", file=sys.stderr)
    sys.exit(0)

n, t = min(amostras, key=lambda nt: abs(math.log(nt[1] / 45.0)))
if t <= 0:
    sys.exit(1)
estimado = max(1, int(round(n * math.sqrt(45.0 / t))))
print(estimado)
if any(s[0] == estimado for s in amostras):
    print(f"fora da faixa, melhor medido n={n} tempo={t:.3f}", file=sys.stderr)
    sys.exit(0)
print(f"estimado a partir de n={n} tempo={t:.3f}", file=sys.stderr)
sys.exit(2)
