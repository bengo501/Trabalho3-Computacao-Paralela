"""Apresentação do T3 no formato do trabalho 2.

Tela 13,333 × 7,5. Título 38 pt navy, corpo 15 pt, glossário de termos
no canto inferior esquerdo, número no canto superior direito (página / total).
Figuras geradas em apresentacao/figuras/. Números de relatorio/dados.py.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "relatorio"))
import dados

ROOT = Path(__file__).resolve().parent
FIG = ROOT / "figuras"
SAIDA = ROOT / "apresentacao.pptx"

NAVY = RGBColor(0x1E, 0x3A, 0x5F)
INK = RGBColor(0x1F, 0x29, 0x37)
MUTED = RGBColor(0x4B, 0x55, 0x63)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
ROW = RGBColor(0xEE, 0xF2, 0xF7)

CHAVES = (
    "MPI_Probe", "MPI_Get_count", "MPI_Recv", "MPI_Send", "MPI_Isend",
    "MPI_Request_free", "MPI_Wtime", "MPI_ANY_SOURCE", "MPI_COMM_WORLD",
    "OMPI_MCA_mpi_yield_when_idle", "Bubble Sort", "bubble sort",
    "T1delta", "T1bal", "Sdelta", "verificacao", "delta", "folha",
    "ajudante", "intercala", "hyperthreading", "speedup", "eficiência",
    "espera ativa", "yield", "block", "exclusive", "Radenski",
)


def set_run(run, size, bold, color, name="Calibri"):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = name


def shade(cell, color):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    for old in tc_pr.findall(qn("a:solidFill")):
        tc_pr.remove(old)
    solid = etree.SubElement(tc_pr, qn("a:solidFill"))
    srgb = etree.SubElement(solid, qn("a:srgbClr"))
    srgb.set("val", f"{color[0]:02X}{color[1]:02X}{color[2]:02X}")


def blocos(text):
    itens, atual = [], []
    for ln in text.split("\n"):
        s = ln.strip()
        if s.startswith("•"):
            if atual:
                itens.append(" ".join(atual))
                atual = []
            itens.append(s.lstrip("•").strip())
        elif s == "":
            if atual:
                itens.append(" ".join(atual))
                atual = []
        else:
            atual.append(s)
    if atual:
        itens.append(" ".join(atual))
    return itens


def escrever(paragraph, text, size, bold, color, nome="Calibri"):
    padrao = re.compile("(" + "|".join(re.escape(c) for c in sorted(CHAVES, key=len, reverse=True)) + ")")
    for parte in padrao.split(text) or [text]:
        if parte == "":
            continue
        run = paragraph.add_run()
        run.text = parte
        if parte in CHAVES:
            set_run(run, size, True, NAVY, nome)
        else:
            set_run(run, size, bold, color, nome)


def add_text(slide, x, y, w, h, text, size=15, bold=False, color=INK, align=PP_ALIGN.LEFT, lista=False):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.auto_size = None
    linhas = blocos(text) if lista else text.split("\n")
    for i, line in enumerate(linhas):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(1 if lista else 2)
        p.space_before = Pt(0)
        if lista:
            p_pr = p._p.get_or_add_pPr()
            p_pr.set("marL", str(int(Inches(0.28))))
            p_pr.set("indent", str(int(Inches(-0.22))))
            bu_font = etree.SubElement(p_pr, qn("a:buFont"))
            bu_font.set("typeface", "Arial")
            bu_clr = etree.SubElement(p_pr, qn("a:buClr"))
            bu_rgb = etree.SubElement(bu_clr, qn("a:srgbClr"))
            bu_rgb.set("val", "000000")
            bu = etree.SubElement(p_pr, qn("a:buChar"))
            bu.set("char", "●")
        escrever(p, line, size, bold, color)
    return box


def chrome(slide, title, page, total):
    add_text(slide, 0.36, 0.08, 10.15, 1.15, title, 34, True, NAVY)
    add_text(slide, 10.6, 0.08, 2.4, 0.36, f"{page} / {total}", 16, False, MUTED, PP_ALIGN.RIGHT)


def legenda(slide, linhas, escuro=False):
    n = len(linhas)
    quebras = sum(1 for linha in linhas if len(linha) > 48)
    altura = 0.20 * n + 0.14 * quebras + 0.04
    y = 7.5 - 0.08 - altura
    box = slide.shapes.add_textbox(Inches(0.28), Inches(y), Inches(8.8), Inches(altura))
    tf = box.text_frame
    tf.word_wrap = True
    tf.auto_size = None
    palavra_cor = RGBColor(0xD6, 0xE4, 0xF5) if escuro else NAVY
    texto_cor = RGBColor(0xE8, 0xEE, 0xF6) if escuro else MUTED
    for i, linha in enumerate(linhas):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.space_after = Pt(0)
        p.space_before = Pt(0)
        if ":" in linha:
            palavra, resto = linha.split(":", 1)
            r1 = p.add_run()
            r1.text = palavra + ":"
            set_run(r1, 10, True, palavra_cor)
            r2 = p.add_run()
            r2.text = resto
            set_run(r2, 10, False, texto_cor)
        else:
            r = p.add_run()
            r.text = linha
            set_run(r, 10, False, texto_cor)


def codigo(slide, x, y, w, h, texto):
    caixa = slide.shapes.add_shape(1, Inches(x), Inches(y), Inches(w), Inches(h))
    caixa.fill.solid()
    caixa.fill.fore_color.rgb = RGBColor(0xF3, 0xF0, 0xE8)
    caixa.line.color.rgb = RGBColor(0xD2, 0xCB, 0xBE)
    caixa.line.width = Pt(0.75)
    tf = caixa.text_frame
    tf.word_wrap = False
    tf.auto_size = None
    tf.margin_left = Inches(0.12)
    tf.margin_top = Inches(0.08)
    for i, linha in enumerate(texto.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(0)
        run = p.add_run()
        run.text = linha if linha else " "
        set_run(run, 12, False, MUTED if linha.strip().startswith("//") else INK, "Consolas")
    return caixa


def table(slide, x, y, w, h, data, sizes=None, fonte=13):
    rows, cols = len(data), len(data[0])
    shape = slide.shapes.add_table(rows, cols, Inches(x), Inches(y), Inches(w), Inches(h))
    tbl = shape.table
    if sizes:
        for i, s in enumerate(sizes):
            tbl.columns[i].width = Inches(s)
    row_h = Inches(h / rows)
    for r, row in enumerate(data):
        tbl.rows[r].height = row_h
        for c, val in enumerate(row):
            cell = tbl.cell(r, c)
            cell.text = ""
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            run = p.add_run()
            run.text = str(val)
            if r == 0:
                set_run(run, fonte, True, WHITE)
                shade(cell, (0x1E, 0x3A, 0x5F))
            else:
                set_run(run, fonte, c == 0, INK)
                if r % 2 == 0:
                    shade(cell, (0xEE, 0xF2, 0xF7))
    return shape


def figura_arvore(path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch

    fig, ax = plt.subplots(figsize=(10.5, 4.6))
    ax.set_xlim(0, 10.5)
    ax.set_ylim(0, 4.6)
    ax.axis("off")
    fig.subplots_adjust(0, 0, 1, 1)

    def caixa(x, y, w, h, titulo, sub=None, fc="#D6E2F0"):
        ax.add_patch(
            FancyBboxPatch(
                (x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                facecolor=fc, edgecolor="#1E3A5F", linewidth=1.4,
            )
        )
        ax.text(x + w / 2, y + h * (0.62 if sub else 0.5), titulo, ha="center", va="center",
                fontsize=14, color="#1E3A5F", fontweight="bold")
        if sub:
            ax.text(x + w / 2, y + h * 0.28, sub, ha="center", va="center",
                    fontsize=11, color="#4B5563")

    nos = {
        "p0": (4.35, 3.55, "n = 40", "divide"),
        "p1": (1.85, 2.15, "n = 20", "divide"),
        "p2": (6.85, 2.15, "n = 20", "divide"),
        "p3": (0.35, 0.55, "n = 10", "Bubble Sort"),
        "p4": (2.85, 0.55, "n = 10", "Bubble Sort"),
        "p5": (5.85, 0.55, "n = 10", "Bubble Sort"),
        "p6": (8.35, 0.55, "n = 10", "Bubble Sort"),
    }
    for pai, filhos in (("p0", ("p1", "p2")), ("p1", ("p3", "p4")), ("p2", ("p5", "p6"))):
        px, py, *_ = nos[pai]
        for filho in filhos:
            fx, fy, *_ = nos[filho]
            ax.plot([px + 0.9, fx + 0.9], [py, fy + 0.85], color="#1E3A5F", lw=1.3)
    for nome, (x, y, sub1, sub2) in nos.items():
        fc = "#E7F2EA" if nome in ("p3", "p4", "p5", "p6") else "#D6E2F0"
        caixa(x, y, 1.8, 0.85, nome, f"{sub1} · {sub2}", fc)
    ax.text(5.25, 4.35, "δ = 10   ·   P = 7   ·   vetor começa em 40, 39, …, 1",
            ha="center", fontsize=13, color="#1E3A5F")
    fig.savefig(path, dpi=160)
    plt.close(fig)


def figura_balanceada(path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

    fig, ax = plt.subplots(figsize=(10.8, 4.4))
    ax.set_xlim(0, 10.8)
    ax.set_ylim(0, 4.4)
    ax.axis("off")
    fig.subplots_adjust(0, 0, 1, 1)

    def caixa(x, y, w, h, texto, fc):
        ax.add_patch(
            FancyBboxPatch(
                (x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                facecolor=fc, edgecolor="#1E3A5F", linewidth=1.4,
            )
        )
        ax.text(x + w / 2, y + h / 2, texto, ha="center", va="center",
                fontsize=13, color="#1E3A5F", fontweight="bold")

    caixa(0.4, 3.2, 3.2, 0.75, "rank r  ·  nível k", "#D6E2F0")
    caixa(4.0, 3.2, 3.0, 0.75, "fica com a esquerda", "#E7F2EA")
    caixa(7.4, 3.2, 3.0, 0.75, "manda a direita", "#FCE8D5")
    ax.add_patch(FancyArrowPatch((3.6, 3.55), (4.0, 3.55), arrowstyle="->", mutation_scale=14, color="#1E3A5F"))
    ax.add_patch(FancyArrowPatch((7.0, 3.55), (7.4, 3.55), arrowstyle="->", mutation_scale=14, color="#1E3A5F"))

    caixa(0.8, 1.7, 4.0, 0.85, "ordena a esquerda\n(recursão no mesmo rank)", "#E7F2EA")
    caixa(6.0, 1.7, 4.0, 0.85, "ajudante = r + 2^k\nMPI_Isend → Probe → ordena → Send", "#FCE8D5")
    caixa(2.4, 0.35, 6.0, 0.75, "MPI_Recv da direita ordenada  ·  intercala", "#D6E2F0")
    ax.text(5.4, 4.15, "sem delta: quem divide também conquista",
            ha="center", fontsize=13, color="#1E3A5F", fontweight="bold")
    fig.savefig(path, dpi=160)
    plt.close(fig)


def figura_mensagens(path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch

    fig, ax = plt.subplots(figsize=(10.8, 4.5))
    ax.set_xlim(0, 10.8)
    ax.set_ylim(0, 4.5)
    ax.axis("off")
    fig.subplots_adjust(0, 0, 1, 1)

    passos = [
        (0.3, 3.5, "1. MPI_Probe(pai)", "espera só o pai, tag 1"),
        (3.8, 3.5, "2. MPI_Get_count", "descobre o tamanho"),
        (7.3, 3.5, "3. MPI_Recv", "aloca e recebe"),
        (0.3, 2.0, "4. MPI_Send esq", "metade esquerda"),
        (3.8, 2.0, "5. MPI_Send dir", "metade direita"),
        (7.3, 2.0, "6. dois MPI_Recv", "só depois das duas Sends"),
        (2.4, 0.5, "7. intercala", "pai junta as metades já ordenadas"),
    ]
    for x, y, t, s in passos:
        w = 5.8 if y < 1 else 3.1
        ax.add_patch(
            FancyBboxPatch(
                (x, y), w, 0.85, boxstyle="round,pad=0.02,rounding_size=0.08",
                facecolor="#F3F0E8", edgecolor="#1E3A5F", linewidth=1.2,
            )
        )
        ax.text(x + 0.15, y + 0.52, t, ha="left", va="center", fontsize=13,
                color="#1E3A5F", fontweight="bold", family="monospace")
        ax.text(x + 0.15, y + 0.22, s, ha="left", va="center", fontsize=11, color="#4B5563")
    fig.savefig(path, dpi=160)
    plt.close(fig)


def figura_speedup(path, ctx):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ps = [linha["p"] for linha in ctx["arvore"]]
    s = [linha["s_f"] for linha in ctx["arvore"]]
    sd = [linha["sd_f"] for linha in ctx["arvore"]]
    fig, ax = plt.subplots(figsize=(6.6, 4.3))
    ax.plot(ps, ps, "k--", label="ideal S = P", zorder=1)
    ax.plot(ps, s, "o-", color="#1f77b4", label="S = T1/Tp", markersize=7, zorder=2)
    ax.plot(ps, sd, "s-", color="#ff7f0e", label="Sdelta = T1delta/Tp", markersize=6, zorder=2)
    for p, val in zip(ps, s):
        ax.annotate(
            f"{val:.1f}".replace(".", ","),
            xy=(p, val), xytext=(0, 10), textcoords="offset points",
            ha="center", fontsize=10, color="#1E3A5F", fontweight="bold",
        )
    ax.set_xlabel("processos P")
    ax.set_ylabel("aceleração")
    ax.set_xticks(ps)
    ax.set_xlim(-1, 34)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def figura_yield(path, ctx):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    ps = [item["p"] for item in ctx["over"]]
    ativa = [item["ativa"]["tp"] for item in ctx["over"]]
    cede = [item["yield"]["tp"] for item in ctx["over"]]
    x = np.arange(len(ps))
    largura = 0.38
    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    ax.bar(x - largura / 2, ativa, largura, label="espera ativa (=0)", color="#1f77b4")
    ax.bar(x + largura / 2, cede, largura, label="yield (=1)", color="#2ca02c")
    ax.set_xticks(x)
    ax.set_xticklabels([str(p) for p in ps])
    ax.set_xlabel("processos P")
    ax.set_ylabel("tempo mediano (s)")
    ax.set_yscale("log")
    ax.grid(True, axis="y", alpha=0.3)
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def figura_nos(path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch

    fig, ax = plt.subplots(figsize=(11.2, 2.5))
    ax.set_xlim(0, 11.2)
    ax.set_ylim(0, 2.5)
    ax.axis("off")
    fig.subplots_adjust(0, 0, 1, 1)

    def caixa(x, y, w, h, texto, fc):
        ax.add_patch(
            FancyBboxPatch(
                (x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.06",
                facecolor=fc, edgecolor="#1E3A5F", linewidth=1.3,
            )
        )
        ax.text(x + w / 2, y + h / 2, texto, ha="center", va="center",
                fontsize=12, color="#1E3A5F")

    ax.text(2.7, 2.2, "atlantica03", ha="center", fontsize=13, color="#1E3A5F", fontweight="bold")
    ax.text(7.5, 2.2, "atlantica04", ha="center", fontsize=13, color="#1E3A5F", fontweight="bold")
    ax.text(0.2, 1.45, "P = 15", ha="left", fontsize=12, color="#1E3A5F", fontweight="bold")
    caixa(1.2, 1.15, 3.0, 0.6, "ranks baixos\n(internos)", "#D6E2F0")
    caixa(6.0, 1.15, 3.0, 0.6, "ranks altos\n(folhas)", "#E7F2EA")
    ax.text(0.2, 0.45, "P = 31", ha="left", fontsize=12, color="#1E3A5F", fontweight="bold")
    caixa(1.2, 0.15, 3.0, 0.6, "8 núcleos\n+ HT", "#D6E2F0")
    caixa(6.0, 0.15, 3.0, 0.6, "16 folhas\nem 2 levas", "#FCE8D5")
    ax.text(9.7, 0.85, "distribuição\nblock", ha="center", fontsize=12, color="#4B5563")
    fig.savefig(path, dpi=160)
    plt.close(fig)


def por_p(serie, p):
    return next(linha for linha in serie if linha["p"] == p)


def build():
    ctx = dados.contexto()
    extras = dados.outras()
    FIG.mkdir(parents=True, exist_ok=True)

    figura_arvore(FIG / "arvore.png")
    figura_balanceada(FIG / "balanceada.png")
    figura_mensagens(FIG / "mensagens.png")
    figura_speedup(FIG / "speedup.png", ctx)
    figura_yield(FIG / "yield.png", ctx)
    figura_nos(FIG / "nos.png")

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    prs.core_properties.title = "T3 divisao e conquista com MPI"
    prs.core_properties.author = "Bernardo Klein Heitz"
    blank = prs.slide_layouts[6]
    # a capa conta como 1; o conteúdo começa em 2 / total, como no T2
    # +1 pela lâmina de contexto do problema
    total = 15 if len(extras) == 2 else 14
    page = 1

    def next_page():
        nonlocal page
        page += 1
        return page

    # 1 capa
    s = prs.slides.add_slide(blank)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = NAVY
    add_text(s, 0.7, 1.55, 12, 0.4, "Computação paralela  ·  trabalho 3", 15, False, RGBColor(0xC5, 0xD4, 0xE8))
    add_text(s, 0.7, 2.1, 12, 1.4, "Ordenação por divisão e conquista", 38, True, WHITE)
    add_text(
        s, 0.7, 3.9, 11, 1.6,
        "Bernardo Klein Heitz\n"
        "github.com/bengo501/Trabalho3-Computacao-Paralela\n"
        "atlantica03 e atlantica04, exclusivos",
        16, False, RGBColor(0xC5, 0xD4, 0xE8),
    )
    legenda(
        s,
        [
            "divisão e conquista: partir o vetor, ordenar as partes, juntar",
            "MPI: mensagens entre processos em máquinas distintas",
            "folha: processo que aplica o Bubble Sort",
        ],
        escuro=True,
    )

    # 2 contexto do problema (primeira lâmina de conteúdo)
    s = prs.slides.add_slide(blank)
    chrome(s, "O problema: ordenar um vetor grande com MPI", next_page(), total)
    add_text(
        s, 0.4, 1.35, 12.5, 5.2,
        "O objetivo deste trabalho é implementar com MPI uma ordenação por divisão e conquista, "
        "medir no Atlântica com até dois nós exclusivos e analisar duas árvores: a da figura do "
        "enunciado e uma versão balanceada. O que importa na nota é explicar o que causou os números, "
        "não apenas mostrar a tabela.\n\n"
        "Ordenamos um vetor que começa decrescente: n, n−1, …, 1. Cada folha aplica Bubble Sort, "
        "o pai intercala as metades já ordenadas e o resultado final precisa ser exatamente 1, 2, …, n. "
        "Esse vetor decrescente é o pior caso do Bubble Sort, sem parada antecipada. Assim a comparação "
        "entre as versões mede balanceamento, e não a troca de algoritmo de ordenação.\n\n"
        "Divisão e conquista entra bem aqui porque o problema parte naturalmente em duas metades. "
        "Cada metade pode ir para outro processo e, na volta, as partes ordenadas se juntam. "
        "Isso forma uma árvore binária de ranks: a raiz gera o vetor, os internos dividem e as folhas conquistam.\n\n"
        "Vamos comparar três frentes. A árvore original, em que quem dividiu espera os dois filhos. "
        "A árvore balanceada, em que o processo manda uma metade e fica com a outra. "
        "E o mesmo programa com mais processos que threads, com espera ativa e com o núcleo cedido. "
        "Duas referências sequenciais separam o ganho: T1 é o bubble do vetor inteiro; T1delta é a "
        "mesma árvore em um processo só.\n\n"
        "Em uma frase, queremos saber quanto do speedup veio do paralelismo e quanto veio do fato "
        "de o Bubble Sort ser quadrático, e como o balanceamento muda esse quadro. "
        "Nos trabalhos anteriores usávamos OpenMP no path tracer e depois MPI mestre escravo com "
        "tarefas dinâmicas. Aqui a árvore de ranks é estática: divisão e conquista, Bubble Sort "
        "nas folhas e intercalação na volta.",
        14, False, INK, lista=True,
    )
    legenda(s, [
        "objetivo: implementar, medir e explicar causas",
        "T1 (trabalho): OpenMP, path tracer",
        "T2: MPI mestre escravo; T3: MPI árvore estática",
        "balanceamento: reduzir ociosidade enquanto outros trabalham",
    ])

    # 3 árvore da figura
    s = prs.slides.add_slide(blank)
    chrome(s, "A árvore do enunciado: n = 40, delta = 10, sete processos", next_page(), total)
    s.shapes.add_picture(str(FIG / "arvore.png"), Inches(0.25), Inches(1.35), Inches(7.4))
    add_text(
        s, 7.85, 1.4, 5.1, 4.7,
        "A figura à esquerda mostra a árvore do enunciado com n = 40 e delta = 10. "
        "Cada caixa é um rank; as verdes são folhas e as setas mostram para onde vai cada metade.\n\n"
        "A raiz gera o vetor e pergunta se o pedaço ainda é grande. Se for, divide. "
        "Se não for, conquista. O rank r manda a metade esquerda ao filho 2r+1 e a direita "
        "ao filho 2r+2. A folha ordena com Bubble Sort e o pai intercala na volta.\n\n"
        "Nesta figura a árvore desce dois níveis, usa 7 processos (P = 2^k−1) e as folhas "
        "p3 a p6 ficam com dez elementos cada. O vetor termina em 1..n.\n\n"
        "Delta não se sintoniza. Com P = 2^k−1, delta = ceil(2n/(P+1)) enche a árvore e as "
        "folhas ficam do mesmo tamanho. Com k níveis há exatamente 2^k−1 processos.",
        14, False, INK, lista=True,
    )
    legenda(s, [
        "delta: limiar que decide dividir ou conquistar",
        "folha: rank que aplica o Bubble Sort",
        "intercala: junta duas metades já ordenadas",
        "P = 2^k−1: árvore cheia, folhas iguais",
    ])

    # 4 quem divide
    s = prs.slides.add_slide(blank)
    chrome(s, "Quem divide, quem conquista e o que acontece se faltar filho", next_page(), total)
    add_text(
        s, 0.4, 1.4, 12.5, 4.9,
        "A regra é simples. O processo divide só quando o pedaço passa de delta e o filho da direita "
        "existe. Se o pedaço ainda é grande e o filho não existe, ele termina a subárvore sozinho, "
        "do mesmo jeito que o sequencial faria naquele pedaço.\n\n"
        "Se o delta deixasse um rank sem mensagem, esse rank ficaria para sempre no MPI_Probe. "
        "Por isso a raiz aborta quando a árvore não ocupa todos os processos: assim evitamos deadlock.\n\n"
        "O filho não sabe o tamanho de antemão. Ele faz MPI_Probe no pai, MPI_Get_count, aloca o "
        "vetor e só então chama MPI_Recv. A tag é 1 nos dois sentidos: o filho espera o pai e, "
        "na volta, o pai espera os dois filhos.\n\n"
        "O tempo medido com MPI_Wtime na raiz abre depois de gerar o vetor e fecha com o vetor "
        "já intercalado. A inicialização fica de fora. Toda execução conta quantos v[i] diferem "
        "de i+1 e imprime verificacao=OK ou ERRO, para demonstrar equivalência em vez de só afirmá-la.\n\n"
        "O programa é SPMD: um único executável. Quem é raiz, interno ou folha sai do rank, "
        "não de programas diferentes.",
        15, False, INK, lista=True,
    )
    legenda(s, [
        "SPMD: mesmo programa, papéis pelo rank",
        "MPI_Probe: espera e lê o status sem consumir",
        "verificacao: conta v[i] ≠ i+1 em toda execução",
        "deadlock: espera permanente por mensagem",
    ])

    # 5 mensagens
    s = prs.slides.add_slide(blank)
    chrome(s, "As duas metades saem antes de qualquer espera", next_page(), total)
    s.shapes.add_picture(str(FIG / "mensagens.png"), Inches(0.25), Inches(1.35), Inches(7.5))
    codigo(
        s, 7.95, 1.4, 5.0, 3.55,
        "meio = tam / 2\n"
        "MPI_Send(esq)\n"
        "MPI_Send(dir)\n"
        "MPI_Recv(esq)\n"
        "MPI_Recv(dir)\n"
        "intercala(...)\n"
        "// arvore.c:132 a 136",
    )
    add_text(
        s, 0.4, 5.15, 12.5, 1.5,
        "A figura mostra o caminho das mensagens passo a passo: o filho descobre o tamanho com Probe, "
        "recebe o pedaço, ordena e devolve; o pai envia as duas metades antes de esperar qualquer resposta. "
        "Se o pai enviasse a esquerda, esperasse o resultado e só depois enviasse a direita, o segundo "
        "filho ficaria ocioso o tempo todo da primeira metade. Com as duas Sends antes de qualquer Recv, "
        "os dois filhos trabalham ao mesmo tempo. Se a mensagem não vier, o processo permanece no Probe ou no Recv.",
        14, False, INK, lista=True,
    )
    legenda(s, [
        "MPI_Send: envia a metade ao filho",
        "MPI_Recv: espera o pedaço ordenado de volta",
        "tag 1: rótulo da mensagem nos dois sentidos",
        "filho espera o pai; pai espera os dois filhos",
    ])

    # 6 duas acelerações
    s = prs.slides.add_slide(blank)
    chrome(s, "Duas acelerações: algoritmo e paralelismo", next_page(), total)
    add_text(
        s, 0.4, 1.4, 12.5, 4.9,
        "S passa de P porque junta dois ganhos diferentes. T1 é o Bubble Sort do vetor inteiro, sem MPI. "
        "T1delta é a mesma árvore de divisões em um só processo. S = T1/Tp. O Bubble Sort é quadrático: "
        "ordenar L pedaços de n/L custa cerca de T1/L, não T1. Isso é ganho de algoritmo, não de núcleos.\n\n"
        "Para isolar o paralelismo usamos Sdelta = T1delta/Tp. A eficiência é E = Sdelta/P "
        "(de 63 a 1023, E = Sdelta/32). O teto de E é folhas/P: 2/3, 4/7, 8/15, 16/31. "
        "Na árvore original, só as folhas fazem o trabalho quadrático; os internos esperam e intercalam. "
        "A intercalação é linear e não explica saltos grandes.\n\n"
        "Em P = 31, T1/T1delta ≈ 16,85: troca de um bubble de n por dezesseis de n/16. "
        "Por isso S ≈ 128 não significa 31 núcleos em paralelo. O E medido fica em 0,25, "
        "bem abaixo do teto 16/31 ≈ 0,52, por causa das duas levas no mesmo nó.\n\n"
        "Na versão balanceada a referência é T1bal: a mesma árvore de ajudantes num processo só.",
        15, False, INK, lista=True,
    )
    legenda(s, [
        "T1: Bubble Sort do vetor inteiro",
        "T1delta: mesma árvore, um processo",
        "S: T1/Tp, inclui o algoritmo",
        "Sdelta: T1delta/Tp, só paralelismo",
        "E: Sdelta/P (ou /32 acima de 32 threads)",
    ])

    # 7 medição
    s = prs.slides.add_slide(blank)
    chrome(s, "O que torna o número comparável", next_page(), total)
    s.shapes.add_picture(str(FIG / "nos.png"), Inches(0.3), Inches(1.35), Inches(8.6))
    add_text(
        s, 0.4, 4.05, 12.5, 2.4,
        f"A figura mostra os dois nós usados em todas as medições: atlantica03 e atlantica04. "
        f"Cada nó tem 8 núcleos físicos e 16 threads; juntos são 16 núcleos e 32 threads.\n\n"
        f"n = {ctx['n']}. T1, mediana de dez rodadas, é {ctx['t1_txt']} s "
        f"(mínimo {ctx['t1_min_txt']}, máximo {ctx['t1_max_txt']}), dentro da faixa de 30 a 60 s "
        f"pedida pelo enunciado. Jobs com exclusive, distribuição block e Open MPI 4.1.1. "
        f"As três versões compilam com O2 e std=c11.\n\n"
        "Dez repetições por configuração. Toda tabela traz mediana, mínimo e máximo. "
        "Toda execução imprime verificacao=OK. Acima de 32 processos usamos overcommit no srun.",
        14, False, INK, lista=True,
    )
    legenda(s, [
        "block: ranks consecutivos no mesmo nó",
        "exclusive: nenhum outro job no nó",
        "overcommit: acima de 32 processos no srun",
        "T1: 45,330 s nesta campanha",
    ])

    # 8 tabela + gráfico árvore
    s = prs.slides.add_slide(blank)
    chrome(s, "Árvore original: S passa de P, Sdelta mede o paralelismo", next_page(), total)
    s.shapes.add_picture(str(FIG / "speedup.png"), Inches(7.7), Inches(1.35), Inches(5.2))
    tab = [["P", "mediana", "min a max", "S", "Sdelta", "E"]]
    for linha in ctx["arvore"]:
        tab.append([
            str(linha["p"]), linha["med"],
            f"{linha['min']} a {linha['max']}",
            linha["s"], linha["sd"], linha["e"],
        ])
    table(s, 0.35, 1.4, 7.1, 2.55, tab, [0.7, 1.2, 2.0, 0.95, 1.15, 0.9], fonte=12)
    p3, p7, p15, p31 = (por_p(ctx["arvore"], p) for p in (3, 7, 15, 31))
    add_text(
        s, 0.35, 4.15, 12.5, 2.35,
        f"A tabela à esquerda é a campanha da árvore original. O gráfico à direita compara três curvas: "
        f"a reta pontilhada ideal (S = P), a azul de S = T1/Tp e a laranja de Sdelta = T1delta/Tp.\n\n"
        f"Até P = 7 a mediana acompanha T1/L², com L = (P+1)/2 folhas. "
        f"Em P = 3, Tp = {p3['med']} s e Sdelta = {p3['sd']} (E = {p3['e']} = 2/3). "
        f"Em P = 7, Tp = {p7['med']} s e Sdelta = {p7['sd']}. "
        f"Em P = 15, Sdelta = {p15['sd']}. Em P = 31, S = {p31['s']} e Sdelta = {p31['sd']}: "
        f"o salto de S vem de T1/T1delta = {p31['ganho']}, não de 31 núcleos. "
        f"E cai para {p31['e']}. A curva azul sobe muito acima da reta ideal; a laranja, não.",
        14, False, INK, lista=True,
    )
    legenda(s, [
        "tabela 1: árvore original, dez repetições",
        "L: número de folhas, (P+1)/2",
        "reta ideal: S = P (só o paralelismo perfeito)",
    ])

    # 9 folhas / HT
    s = prs.slides.add_slide(blank)
    chrome(s, "Folhas no mesmo nó e o que o hyperthreading rendeu", next_page(), total)
    prev31 = ctx["previsto"][31]
    duas = 2 * prev31
    add_text(
        s, 0.4, 1.4, 12.5, 5.0,
        "As folhas são os ranks altos. Com distribuição block, ranks consecutivos ficam no mesmo nó, "
        "então um nó concentra quase todas as folhas sobre 8 núcleos físicos.\n\n"
        f"Em P = 15 ainda cabe uma leva por núcleo. Em P = 31 são 16 folhas para 8 núcleos: duas levas. "
        f"O modelo dá 2·T1/256 = {dados.tempo(duas)} s; a mediana foi {p31['med']} s, "
        f"a {dados.ms(abs(p31['tp'] - duas))} ms da conta.\n\n"
        f"Nesta referência de 45 s, Sdelta passa de {p15['sd']} em P = 15 para {p31['sd']} em P = 31. "
        "A segunda leva no mesmo núcleo quase não encolheu. O hyperthreading ocupou a segunda thread, "
        "mas não dobrou a vazão do Bubble Sort.\n\n"
        "Nos vetores maiores (cerca de 2 min e 5 min de T1), Sdelta em P = 31 sobe para 8,92 e 9,22: "
        "a segunda thread recupera parte da leva quando o bubble é mais longo. "
        "Ainda assim não é speedup de 31 núcleos: só as folhas fazem o trabalho quadrático.",
        15, False, INK, lista=True,
    )
    legenda(s, [
        "leva: onda de folhas que cabem nos núcleos",
        "hyperthreading: segunda thread no mesmo núcleo",
        "block: ranks altos (folhas) juntos no mesmo nó",
    ])

    # 10 balanceada modelo
    s = prs.slides.add_slide(blank)
    chrome(s, "A versão balanceada: manda uma metade e fica com a outra", next_page(), total)
    s.shapes.add_picture(str(FIG / "balanceada.png"), Inches(0.25), Inches(1.3), Inches(8.3))
    add_text(
        s, 8.7, 1.35, 4.3, 4.7,
        "A figura compara a árvore original (quem divide só espera) com a balanceada "
        "(manda a direita e ordena a esquerda).\n\n"
        "Na original, quem dividiu fica parado até os dois filhos responderem. "
        "Só as folhas conquistam.\n\n"
        "Na balanceada não há delta: o processo manda a metade direita ao ajudante "
        "rank + 2^nível e ordena a esquerda. Assim o interno também conquista.\n\n"
        "A fórmula do ajudante evita colisão. No nível ℓ os ativos são 0..2^ℓ−1; "
        "o ajudante cai em 2^ℓ .. 2^(ℓ+1)−1.\n\n"
        "MPI_Isend devolve e o processo segue. MPI_Request_free solta o handle. "
        "Com P = 2^k cada um fica com n/P; com P = 31 um pedaço dobra. "
        "Derivada de Radenski (PDPTA 2011).",
        12, False, INK, lista=True,
    )
    legenda(s, [
        "ajudante: rank + 2^nível, sem colisão de ranks",
        "MPI_Isend: envio não bloqueante",
        "T1bal: mesma árvore de ajudantes, um processo",
        "Radenski: artigo e código de partida",
    ])

    # 11 balanceada números
    s = prs.slides.add_slide(blank)
    chrome(s, "Tabela balanceada: P = 2 não paraleliza", next_page(), total)
    tab = [["P", "mediana", "min a max", "S", "Sdelta", "E"]]
    for linha in ctx["balanceada"]:
        tab.append([
            str(linha["p"]), linha["med"],
            f"{linha['min']} a {linha['max']}",
            linha["s"], linha["sd"], linha["e"],
        ])
    table(s, 0.35, 1.35, 12.6, 2.7, tab, [1.0, 1.5, 3.2, 1.5, 1.7, 1.3], fonte=13)
    p2 = por_p(ctx["balanceada"], 2)
    p16 = por_p(ctx["balanceada"], 16)
    p31b = por_p(ctx["balanceada"], 31)
    p32 = por_p(ctx["balanceada"], 32)
    add_text(
        s, 0.4, 4.25, 12.5, 2.25,
        f"A tabela acima é a campanha da versão balanceada. Em P = 2, Tp = {p2['med']} s e "
        f"T1bal = {p2['t1d']} s, então Sdelta = {p2['sd']}. A esquerda é folha: sem outra chamada MPI, "
        f"o Isend não anda (Open MPI 4.1.1 sem thread de progresso) e o ajudante fica no Probe. "
        f"Isso se repete nos três tamanhos de vetor.\n\n"
        f"De P = 4 em diante outro envio destrava a mensagem. Nesta referência de 45 s, "
        f"P = 16 ({p16['med']} s) fica junto da original em P = 31 ({p31['med']} s). "
        f"P = 31 balanceada fica em {p31b['med']} s e P = 32 em {p32['med']} s: "
        f"o pedaço dobrado custa cerca de T1/256 = {dados.tempo(ctx['t1']/256)} s.",
        14, False, INK, lista=True,
    )
    legenda(s, [
        "tabela 2: versão balanceada",
        "Probe: ajudante esperando a mensagem",
        "progresso MPI: Isend só anda dentro de outra chamada MPI",
    ])

    # 12 over table
    s = prs.slides.add_slide(blank)
    chrome(s, "De 63 a 1023 processos: mais processos que threads", next_page(), total)
    tab = [["P", "T1delta", "espera ativa", "yield", "Sdelta ativa", "Sdelta yield", "E yield"]]
    for item in ctx["over"]:
        tab.append([
            str(item["p"]), item["t1d"],
            item["ativa"]["med"], item["yield"]["med"],
            item["ativa"]["sd"], item["yield"]["sd"], item["yield"]["e"],
        ])
    table(s, 0.3, 1.35, 12.7, 2.85, tab, [1.0, 1.5, 2.1, 1.7, 2.0, 2.1, 1.5], fonte=12)
    add_text(
        s, 0.4, 4.4, 12.5, 2.1,
        "A tabela compara, para cada P, o tempo com espera ativa e com yield. "
        "É o caminho para balancear sem alterar o código: rodar com mais processos que as 32 threads "
        "(de 63 a 1023) e ceder o núcleo. O escalonador do sistema passa a privilegiar as folhas.\n\n"
        "A errata da versão 2 exige OMPI_MCA_mpi_yield_when_idle=0 e =1 escritos explicitamente. "
        "Apagar a variável pode já ceder o núcleo, e as duas séries medem a mesma coisa.\n\n"
        "Aqui E = Sdelta/32. O denominador não cresce com P, porque o hardware não cresce. "
        "Mediana, mínimo e máximo das dez repetições estão na tabela 3 do relatório.",
        14, False, INK, lista=True,
    )
    legenda(s, [
        "tabela 3: série 63 a 1023",
        "espera ativa: yield=0, gira no núcleo",
        "yield: cede a CPU enquanto espera",
        "E: Sdelta/32 nestas linhas",
    ])

    # 13 yield chart
    s = prs.slides.add_slide(blank)
    chrome(s, "Espera ativa contra ceder o núcleo", next_page(), total)
    s.shapes.add_picture(str(FIG / "yield.png"), Inches(7.5), Inches(1.35), Inches(5.45))
    exemplo = max(ctx["over"], key=lambda item: item["ativa"]["tp"] / item["t1d_f"])
    add_text(
        s, 0.35, 1.4, 7.0, 4.8,
        "O gráfico à direita usa escala logarítmica no eixo vertical. "
        "As barras azuis são espera ativa (yield=0) e as laranjas são yield=1. "
        "Com a variável escrita em 0 e em 1, o yield encurtou todas as linhas e as faixas "
        "de mínimo a máximo não se cruzam.\n\n"
        f"Em P = {exemplo['p']}, o mínimo da espera ativa ({exemplo['ativa']['min']} s) ficou "
        f"acima da mediana sequencial ({exemplo['t1d']} s). Com yield, {exemplo['yield']['med']} s.\n\n"
        "Com mais processos do que os 32 threads, quem gira no núcleo tira a vez de quem ainda ordena. "
        "Ceder a CPU é o balanceamento sem alterar o código: o escalonador do sistema operacional "
        "passa a privilegiar as folhas. Em P = 1023 a diferença explode e mostra o custo da espera "
        "ativa quando a folha é minúscula e o número de processos é grande.",
        14, False, INK, lista=True,
    )
    legenda(s, [
        "escalonador: decide quem usa o núcleo",
        "folha minúscula: pouco trabalho, muito processo ocioso",
        "log: eixo vertical em escala logarítmica",
    ])

    # 14 três tamanhos (se houver)
    if len(extras) == 2:
        s = prs.slides.add_slide(blank)
        chrome(s, "O que o vetor maior muda e o que não muda", next_page(), total)
        todos = [("45 s", ctx)] + extras

        def sd(c, serie, p):
            return next(linha for linha in c[serie] if linha["p"] == p)["sd"]

        def fator(c, qual):
            item = next(i for i in c["over"] if i["p"] == 1023)
            return f"{item[qual]['tp'] / item['t1d_f']:.1f}".replace(".", ",")

        sds = ", ".join(sd(c, "arvore", 31) for _, c in todos)
        b16 = ", ".join(sd(c, "balanceada", 16) for _, c in todos)
        ativa = ", ".join(fator(c, "ativa") for _, c in todos)
        cede = ", ".join(fator(c, "yield") for _, c in todos)
        ns = ", ".join(str(c["n"]) for _, c in todos)
        add_text(
            s, 0.4, 1.4, 12.5, 5.0,
            f"Rodamos as mesmas séries com n = {ns}. A tabela oficial continua a de 45 s, "
            f"porque o enunciado pede T1 entre 30 e 60 s.\n\n"
            "P = 3 e P = 7 continuam na conta da folha nos três tamanhos: o modelo quadrático se sustenta.\n\n"
            f"Em P = 31, Sdelta fica em {sds}. A segunda thread recupera parte da leva quando o bubble "
            f"é mais longo. Em P = 16 balanceado os valores são {b16} e deixam de acompanhar esse P = 31.\n\n"
            "Em P = 2 balanceado, Sdelta = 1,00 nos três casos. O ajudante segue no Probe; "
            "não é artefato do tamanho do vetor.\n\n"
            f"Em P = 1023, a espera ativa fica {ativa} vezes a árvore sequencial; com yield, {cede}. "
            "A penalidade da espera ativa encolhe com n maior, mas não some.",
            15, False, INK, lista=True,
        )
        legenda(s, [
            "campanha oficial: n = 212064, T1 = 45,330 s",
            "médio: n = 345037, T1 ≈ 2 min",
            "longo: n = 545552, T1 ≈ 5 min",
        ])

    # 15 fechamento
    s = prs.slides.add_slide(blank)
    chrome(s, "O que levar da análise", next_page(), total)
    add_text(
        s, 0.4, 1.4, 12.5, 5.0,
        "S passa de P porque o Bubble Sort é quadrático. Sdelta e E isolam o paralelismo. "
        "O teto de E é folhas/P, por isso E em P = 31 não é speedup de 31 núcleos.\n\n"
        "Há dois caminhos de balanceamento. Sem alterar o código: mais processos que threads "
        "(de 63 a 1023) e yield=1 para ceder o núcleo. Alterando o código: Radenski manda uma "
        "metade e fica com a outra. Na referência de 45 s, P = 16 balanceado (cerca de 0,377 s) "
        "fica junto da original em P = 31 (cerca de 0,354 s).\n\n"
        "Hyperthreading em P = 31 quase não encurtou a segunda leva aos 45 s; no vetor maior, "
        "recupera parte. Em P = 2 balanceado, Sdelta = 1,00: sem outra chamada MPI, "
        "o Isend não progride e o ajudante fica no Probe.\n\n"
        "A equivalência está demonstrada: toda execução imprime verificacao=OK. Dez repetições, "
        "mesmos dois nós exclusivos, distribuição block. "
        "Código, scripts e tempos brutos estão no repositório do cabeçalho.",
        15, False, INK, lista=True,
    )
    legenda(s, [
        "tabela 1: árvore original",
        "tabela 2: balanceada",
        "tabela 3: 63 a 1023 com yield=0 e =1",
        "repositório: github.com/bengo501/Trabalho3-Computacao-Paralela",
    ])

    assert page == total, f"páginas {page} != total {total}"
    prs.save(str(SAIDA))
    print(f"{SAIDA}  slides={len(prs.slides)}  figuras={FIG}")


if __name__ == "__main__":
    build()
