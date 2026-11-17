"""Apresentação do T3, no formato do trabalho 2.

Tela 13,333 × 7,5 pol. Título 38 pt, corpo 15 pt, marcador preto,
legenda 10 pt no canto inferior esquerdo, número de página 16 pt.
Sem barra no topo. Os números vêm de relatorio/dados.py.
"""

import sys
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "relatorio"))
import dados

SAIDA = Path(__file__).resolve().parent / "apresentacao.pptx"

NAVY = RGBColor(0x0A, 0x1F, 0x44)
INK = RGBColor(0x1A, 0x1A, 0x1A)
MUTED = RGBColor(0x5C, 0x65, 0x70)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LINE = RGBColor(0xD5, 0xDB, 0xE3)


def novo():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    prs.core_properties.title = "Trabalho 3: divisão e conquista com MPI"
    prs.core_properties.author = "Bernardo Klein Heitz"
    return prs, prs.slide_layouts[6]


def texto(slide, x, y, w, h, trechos, size=15, align=PP_ALIGN.LEFT, font="Calibri"):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = box.text_frame
    frame.word_wrap = True
    frame.auto_size = None
    paragrafo = frame.paragraphs[0]
    paragrafo.alignment = align
    for pedaco, negrito in trechos:
        run = paragrafo.add_run()
        run.text = pedaco
        run.font.size = Pt(size)
        run.font.bold = negrito
        run.font.color.rgb = NAVY if negrito else INK
        run.font.name = font
    return box


def marcar(texto_bruto):
    partes = []
    for indice, pedaco in enumerate(texto_bruto.split("**")):
        if pedaco:
            partes.append((pedaco, indice % 2 == 1))
    return partes


def titulo(slide, frase):
    texto(slide, 0.38, 0.16, 11.5, 0.78, [(frase, False)], size=38)
    # o título inteiro fica em navy, não só o trecho marcado
    run = slide.shapes[-1].text_frame.paragraphs[0].runs[0]
    run.font.color.rgb = NAVY
    run.font.bold = False


def bullets(slide, itens, y0=1.45, passo=1.15):
    for indice, item in enumerate(itens):
        y = y0 + indice * passo
        ponto = slide.shapes.add_shape(
            MSO_SHAPE.OVAL, Inches(0.46), Inches(y + 0.08), Inches(0.10), Inches(0.10)
        )
        ponto.fill.solid()
        ponto.fill.fore_color.rgb = RGBColor(0, 0, 0)
        ponto.line.fill.background()
        texto(slide, 0.72, y, 12.1, 1.05, marcar(item), size=15)


def legenda(slide, frase):
    box = texto(slide, 0.38, 6.95, 11.5, 0.40, [(frase, False)], size=10)
    run = box.text_frame.paragraphs[0].runs[0]
    run.font.color.rgb = MUTED
    run.font.italic = True
    run.font.bold = False


def numerar(prs):
    for indice, slide in enumerate(prs.slides, 1):
        box = texto(slide, 12.15, 0.22, 0.85, 0.40, [(str(indice), False)], size=16, align=PP_ALIGN.RIGHT)
        run = box.text_frame.paragraphs[0].runs[0]
        run.font.color.rgb = MUTED
        run.font.bold = False


def capa(prs, layout):
    slide = prs.slides.add_slide(layout)
    texto(slide, 0.55, 1.7, 12, 0.4, [("Trabalho 3", False)], size=18)
    slide.shapes[-1].text_frame.paragraphs[0].runs[0].font.color.rgb = MUTED
    texto(slide, 0.55, 2.15, 12, 1.6, [("Ordenação por divisão e conquista", False)], size=40)
    slide.shapes[-1].text_frame.paragraphs[0].runs[0].font.color.rgb = NAVY
    texto(slide, 0.55, 4.15, 12, 0.45, [("Bernardo Klein Heitz", False)], size=20)
    texto(
        slide,
        0.55,
        4.7,
        12,
        0.4,
        [("https://github.com/bengo501/Trabalho3-Computacao-Paralela", False)],
        size=14,
    )
    slide.shapes[-1].text_frame.paragraphs[0].runs[0].font.color.rgb = MUTED
    texto(
        slide,
        0.55,
        5.15,
        12,
        0.4,
        [("atlantica03 e atlantica04, exclusivos", False)],
        size=16,
    )
    slide.shapes[-1].text_frame.paragraphs[0].runs[0].font.color.rgb = MUTED


def caixa(slide, x, y, w, h, frase):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = WHITE
    shape.line.color.rgb = NAVY
    shape.line.width = Pt(1.25)
    shape.adjustments[0] = 0.15
    frame = shape.text_frame
    frame.word_wrap = False
    frame.auto_size = None
    frame.paragraphs[0].alignment = PP_ALIGN.CENTER
    shape.text_frame.paragraphs[0].space_before = Pt(0)
    frame._txBody.bodyPr.set("anchor", "ctr")
    run = frame.paragraphs[0].add_run()
    run.text = frase
    run.font.size = Pt(16)
    run.font.bold = True
    run.font.color.rgb = NAVY
    run.font.name = "Calibri"
    return shape


def ligar(slide, x1, y1, x2, y2):
    linha = slide.shapes.add_connector(
        MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2)
    )
    linha.line.color.rgb = NAVY
    linha.line.width = Pt(1.25)


def figura(prs, layout):
    slide = prs.slides.add_slide(layout)
    titulo(slide, "A árvore do enunciado")
    nos = {
        "p0": (5.95, 1.35),
        "p1": (3.15, 2.85),
        "p2": (8.75, 2.85),
        "p3": (1.55, 4.45),
        "p4": (4.15, 4.45),
        "p5": (7.35, 4.45),
        "p6": (9.95, 4.45),
    }
    w, h = 1.45, 0.58
    for pai, filhos in (("p0", ("p1", "p2")), ("p1", ("p3", "p4")), ("p2", ("p5", "p6"))):
        px, py = nos[pai]
        for filho in filhos:
            fx, fy = nos[filho]
            ligar(slide, px + w / 2, py + h, fx + w / 2, fy)
    for nome, (x, y) in nos.items():
        caixa(slide, x, y, w, h, nome)
    for nome in ("p3", "p4", "p5", "p6"):
        x, y = nos[nome]
        rotulo = texto(slide, x, y + 0.62, w, 0.32, [("10 elementos", False)], size=12, align=PP_ALIGN.CENTER)
        rotulo.text_frame.paragraphs[0].runs[0].font.color.rgb = MUTED
    legenda(slide, "n = 40 e delta = 10. O rank r manda a esquerda para 2r+1 e a direita para 2r+2. O vetor termina em 1..n.")


def quem_divide(prs, layout):
    slide = prs.slides.add_slide(layout)
    titulo(slide, "Quem divide e quem ordena")
    bullets(
        slide,
        [
            "O processo **divide** só quando o pedaço passa de delta e os dois filhos existem.",
            "Delta = ceil(2n/(P+1)). Com P = 2^k−1, as folhas ficam do mesmo tamanho.",
            "Se o pedaço ainda é grande e o filho não existe, o processo termina a subárvore sozinho.",
            "Se o delta deixasse um rank sem mensagem, a raiz aborta. Ninguém fica preso no **MPI_Probe**.",
        ],
    )
    legenda(slide, "comum.c, divide e delta_da_arvore. A folha usa o bubble sort do sequencial.c do professor.")


def mensagens(prs, layout):
    slide = prs.slides.add_slide(layout)
    titulo(slide, "As duas metades saem antes da espera")
    linhas = [
        "MPI_Probe(pai, tag=1)       o filho espera só o pai",
        "MPI_Get_count               o tamanho vem da mensagem",
        "MPI_Recv                    aloca e recebe o pedaço",
        "MPI_Send(esquerda)          os dois filhos recebem",
        "MPI_Send(direita)           antes de qualquer espera",
        "MPI_Recv(esquerda)",
        "MPI_Recv(direita)",
        "intercala                   o pai junta as metades já ordenadas",
    ]
    y = 1.42
    for linha in linhas:
        texto(slide, 0.7, y, 12, 0.40, [(linha, False)], size=16, font="Consolas")
        y += 0.58
    legenda(
        slide,
        "arvore.c. O Recv espera o pai (ou o filho), com tag 1. Se a mensagem não vier, o processo fica no Probe. "
        "As duas metades saem antes de qualquer espera, para os dois filhos trabalharem juntos.",
    )


def modelo_balanceado(prs, layout):
    slide = prs.slides.add_slide(layout)
    titulo(slide, "A versão balanceada muda o desenho")
    bullets(
        slide,
        [
            "Não há um delta. O processo manda a metade direita e fica com a esquerda.",
            "O ajudante é o rank **r + 2^nível**. O envio é **MPI_Isend**.",
            "Com P potência de 2, toda folha termina com n/P.",
            "Com P = 31 a última folha fica com o dobro. Por isso 31 entra na série.",
        ],
    )
    legenda(slide, "Derivada de Radenski, PDPTA 2011, GPL-2.0. A folha continua sendo bubble sort.")


def aceleracoes(prs, layout):
    slide = prs.slides.add_slide(layout)
    titulo(slide, "Duas acelerações, não uma")
    bullets(
        slide,
        [
            "**T1** é o bubble do vetor inteiro, sem MPI.",
            "**T1delta** é a mesma árvore em um processo.",
            "**S = T1/Tp** junta o algoritmo e o paralelismo, e pode passar de P.",
            "**Sdelta = T1delta/Tp** é só o paralelismo. **E = Sdelta/P**.",
        ],
    )
    legenda(
        slide,
        "S passa de P porque o bubble é quadrático: T1/T1delta é o ganho de algoritmo. "
        "E = Sdelta/P; o teto é o número de folhas sobre P, não 31 núcleos em paralelo.",
    )


def protocolo(prs, layout, ctx):
    slide = prs.slides.add_slide(layout)
    titulo(slide, "O que torna o número comparável")
    bullets(
        slide,
        [
            f"n = {ctx['n']}. T1 = {ctx['t1_txt']} s, dentro de 30 a 60 s.",
            "Dez repetições. A tabela traz mediana, mínimo e máximo.",
            "Mesmas flags **-O2**, os mesmos dois nós, **--exclusive**, distribuição **block**.",
            "Toda execução imprime **verificacao=OK**. O vetor final é exatamente 1..n.",
        ],
    )
    legenda(slide, "Xeon E5520, 8 núcleos físicos e 16 lógicos por nó. Dois nós: 16 núcleos e 32 threads.")


def pintar(celula, frase, negrito, tamanho, fundo, cor):
    celula.text = frase
    celula.margin_left = Inches(0.04)
    celula.margin_right = Inches(0.04)
    celula.vertical_anchor = MSO_ANCHOR.MIDDLE
    paragrafo = celula.text_frame.paragraphs[0]
    paragrafo.alignment = PP_ALIGN.CENTER
    run = paragrafo.runs[0]
    run.font.size = Pt(tamanho)
    run.font.bold = negrito
    run.font.color.rgb = cor
    run.font.name = "Calibri"
    if fundo is not None:
        celula.fill.solid()
        celula.fill.fore_color.rgb = fundo
    else:
        celula.fill.background()


def grade(slide, cabecalho, linhas, y, altura_linha=0.38):
    colunas = len(cabecalho)
    tabela = slide.shapes.add_table(
        len(linhas) + 1, colunas, Inches(0.4), Inches(y), Inches(12.5), Inches(altura_linha * (len(linhas) + 1))
    ).table
    tabela.columns[0].width = Inches(1.1)
    resto = Emu(int(Inches(11.4) / (colunas - 1)))
    for indice in range(1, colunas):
        tabela.columns[indice].width = resto
    for indice, nome in enumerate(cabecalho):
        pintar(tabela.cell(0, indice), nome, True, 13, NAVY, WHITE)
    for i, linha in enumerate(linhas, 1):
        fundo = RGBColor(0xF4, 0xF7, 0xFB) if i % 2 == 0 else WHITE
        for j, valor in enumerate(linha):
            pintar(tabela.cell(i, j), valor, False, 14, fundo, INK)
    return tabela


def slide_tabela(prs, layout, ctx):
    slide = prs.slides.add_slide(layout)
    titulo(slide, "Árvore original")
    grade(
        slide,
        ["P", "mediana", "mínimo", "máximo", "S", "Sdelta", "E"],
        [
            [str(linha["p"]), linha["med"], linha["min"], linha["max"], linha["s"], linha["sd"], linha["e"]]
            for linha in ctx["arvore"]
        ],
        1.55,
        0.46,
    )
    legenda(slide, f"Dez repetições, verificação OK. T1 = {ctx['t1_txt']} s. Os mesmos números estão na tabela 1 do relatório.")


def quadratico(prs, layout, ctx):
    slide = prs.slides.add_slide(layout)
    titulo(slide, "O quadrático previa estes tempos")
    por_p = {linha["p"]: linha for linha in ctx["arvore"]}
    prev = ctx["previsto"]
    bullets(
        slide,
        [
            "Bubble de m custa proporcional a m². O vetor decrescente não para antes.",
            f"P = 3: previsto T1/4 = {dados.tempo(prev[3])} s. Medido {por_p[3]['med']} s.",
            f"P = 7: previsto T1/16 = {dados.tempo(prev[7])} s. Medido {por_p[7]['med']} s.",
            f"P = 1 mede o mesmo bubble: {ctx['t1_txt']} s e {por_p[1]['med']} s. A diferença é {dados.tempo(ctx['p1_diff'])} s.",
        ],
    )
    legenda(slide, "A previsão usa só T1 e o tamanho da folha. Não foi ajustada depois da medição.")


def folhas(prs, layout, ctx):
    slide = prs.slides.add_slide(layout)
    titulo(slide, "As folhas caem no mesmo nó")
    por_p = {linha["p"]: linha for linha in ctx["arvore"]}
    duas = 2 * ctx["previsto"][31]
    bullets(
        slide,
        [
            "Só as folhas fazem o trabalho quadrático. Os internos esperam e intercalam.",
            f"O teto de E é 2/3, 4/7, 8/15 e 16/31. P = 3 mede {por_p[3]['e']} e P = 7 mede {por_p[7]['e']}.",
            "As folhas são os ranks altos. **block** junta esses ranks num nó, sobre 8 núcleos.",
            f"P = 31, duas levas: 2·T1/256 = {dados.tempo(duas)} s. A mediana foi {por_p[31]['med']} s.",
        ],
    )
    legenda(
        slide,
        "A intercalação é linear e não explica esse fator dois. A mediana ficou a "
        f"{dados.ms(abs(por_p[31]['tp'] - duas))} ms da conta.",
    )


def hyper(prs, layout, ctx):
    slide = prs.slides.add_slide(layout)
    titulo(slide, "O que o hyper-threading rendeu")
    por_p = {linha["p"]: linha for linha in ctx["arvore"]}
    bullets(
        slide,
        [
            "P = 15 cabe em um processo por núcleo físico. P = 31 ocupa a segunda thread.",
            f"Sdelta vai de {por_p[15]['sd']} para {por_p[31]['sd']}. O paralelismo quase não andou.",
            f"S vai de {por_p[15]['s']} para {por_p[31]['s']} porque o bubble ficou menor.",
            "Nesta referência de 45 s a segunda leva não encolheu. No vetor maior, a thread extra recupera parte dela.",
        ],
    )
    legenda(
        slide,
        f"E cai de {por_p[15]['e']} para {por_p[31]['e']}. O ganho de algoritmo em P = 31 é T1/T1delta = {por_p[31]['ganho']}. "
        "E não é speed-up de 31 núcleos: só as folhas fazem o trabalho quadrático.",
    )


def slide_balanceada(prs, layout, ctx):
    slide = prs.slides.add_slide(layout)
    titulo(slide, "Versão balanceada")
    grade(
        slide,
        ["P", "mediana", "mínimo", "máximo", "S", "Sdelta", "E"],
        [
            [str(linha["p"]), linha["med"], linha["min"], linha["max"], linha["s"], linha["sd"], linha["e"]]
            for linha in ctx["balanceada"]
        ],
        1.45,
        0.42,
    )
    por_p = {linha["p"]: linha for linha in ctx["balanceada"]}
    if 31 in por_p and 32 in por_p:
        frase = (
            f"Tabela 2 do relatório. P = 31 ficou em {por_p[31]['med']} s e P = 32 em {por_p[32]['med']} s. "
            "Em 31, um pedaço tem o dobro de elementos."
        )
    else:
        frase = "Tabela 2 do relatório. T1bal é a mesma árvore de ajudantes num processo só."
    legenda(slide, frase)


def causa_balanceada(prs, layout, ctx):
    slide = prs.slides.add_slide(layout)
    titulo(slide, "Por que P = 2 não acelerou")
    por_p = {linha["p"]: linha for linha in ctx["balanceada"]}
    orig = {linha["p"]: linha for linha in ctx["arvore"]}
    bullets(
        slide,
        [
            f"P = 2: Tp = {por_p[2]['med']} s e T1bal = {por_p[2]['t1d']} s. Sdelta = {por_p[2]['sd']}.",
            "A esquerda é folha. Sem outra chamada MPI, o **MPI_Isend** não anda e o ajudante fica no **Probe**.",
            f"De P = 4 em diante outro envio destrava a mensagem. P = 4 mediu {por_p[4]['med']} s, duas folhas em série.",
            f"Nesta referência de 45 s, P = 16 ({por_p[16]['med']} s) fica junto da original em P = 31 ({orig[31]['med']} s). O desenho novo não subiu o paralelismo.",
        ],
        passo=1.05,
    )
    legenda(
        slide,
        f"P = 32 chega a {por_p[32]['med']} s porque a folha cai para n/32. "
        f"P = 31 fica em {por_p[31]['med']} s: um pedaço tem o dobro de elementos.",
    )


def causa_over(prs, layout, ctx):
    slide = prs.slides.add_slide(layout)
    titulo(slide, "Espera ativa contra yield")
    piores = [item for item in ctx["over"] if item["ativa"]["tp_min"] > item["t1d_f"]]
    cruzam = [
        item for item in ctx["over"]
        if not (
            item["ativa"]["tp_max"] < item["yield"]["tp_min"]
            or item["yield"]["tp_max"] < item["ativa"]["tp_min"]
        )
    ]
    if cruzam:
        abertura = "Em P = " + ", ".join(str(item["p"]) for item in cruzam) + " as faixas mínimo–máximo se encontram."
    else:
        abertura = "Com a variável escrita em 0 e em 1, yield encurtou todas as linhas. O 0 repetiu a faixa da série anterior."
    itens = [abertura]
    if piores:
        exemplo = max(piores, key=lambda item: item["ativa"]["tp"] / item["t1d_f"])
        itens.append(
            f"Em P = {exemplo['p']}, o mínimo da espera ativa ({exemplo['ativa']['min']} s) perde da mediana sequencial ({exemplo['t1d']} s)."
        )
    itens.append("Com mais processos do que os 32 threads, quem gira no núcleo tira a vez de quem ainda ordena.")
    itens.append("E = Sdelta/32. O denominador não cresce com P, porque o hardware não cresce.")
    bullets(slide, itens, passo=1.05)
    legenda(
        slide,
        "Tabela 1 é a árvore original, tabela 2 a balanceada e tabela 3 estes P. "
        "Mediana, mínimo e máximo estão nas três. Mesmos dois nós, srun -O.",
    )


def slide_over(prs, layout, ctx):
    slide = prs.slides.add_slide(layout)
    titulo(slide, "De 63 a 1023 processos")
    grade(
        slide,
        ["P", "espera ativa", "yield", "Sdelta ativa", "Sdelta yield", "E yield"],
        [
            [
                str(item["p"]),
                item["ativa"]["med"],
                item["yield"]["med"],
                item["ativa"]["sd"],
                item["yield"]["sd"],
                item["yield"]["e"],
            ]
            for item in ctx["over"]
        ],
        1.5,
        0.46,
    )
    legenda(slide, "Tabela 3. mpi_yield_when_idle=0 e =1, os dois escritos. E = Sdelta/32. Dez repetições.")


def falta(prs, layout, faltam):
    slide = prs.slides.add_slide(layout)
    titulo(slide, "O que esta versão ainda não fecha")
    lista = ", ".join(str(p) for p in faltam)
    bullets(
        slide,
        [
            f"P = {lista} ainda não fecharam as duas políticas com dez repetições.",
            "Acima de 32 processos, E = Sdelta/32. São os mesmos 32 threads de hardware.",
            "Nada desta página é um resultado. É o que ainda falta medir.",
        ],
        passo=1.2,
    )
    legenda(slide, "Quando o CSV fechar, esta página sai e a tabela ganha essas linhas.")


def tres_tamanhos(prs, layout, ctx, extras):
    slide = prs.slides.add_slide(layout)
    titulo(slide, "O que o vetor maior muda")
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
    bullets(
        slide,
        [
            "P = 3 e P = 7 continuam na conta da folha nos três tamanhos.",
            f"P = 31: Sdelta {sds}. A segunda thread recupera parte da leva. P = 16 balanceado fica em {b16} e deixa de acompanhar.",
            "P = 2 balanceado: Sdelta = 1,00 nos três. O ajudante segue no **Probe**.",
            f"P = 1023: espera ativa {ativa} vezes o sequencial; com yield, {cede}.",
        ],
        passo=1.05,
    )
    ns = ", ".join(str(c["n"]) for _, c in todos)
    legenda(slide, f"n = {ns}. A tabela oficial continua a primeira, com T1 entre 30 e 60 s.")


def main():
    ctx = dados.contexto()
    prs, layout = novo()
    capa(prs, layout)
    figura(prs, layout)
    quem_divide(prs, layout)
    mensagens(prs, layout)
    modelo_balanceado(prs, layout)
    aceleracoes(prs, layout)
    protocolo(prs, layout, ctx)
    slide_tabela(prs, layout, ctx)
    quadratico(prs, layout, ctx)
    folhas(prs, layout, ctx)
    hyper(prs, layout, ctx)
    if len(ctx["balanceada"]) == len(dados.PS_BALANCEADA):
        slide_balanceada(prs, layout, ctx)
        causa_balanceada(prs, layout, ctx)
    if ctx["over"]:
        slide_over(prs, layout, ctx)
        causa_over(prs, layout, ctx)
    faltam = [p for p in dados.PS_OVER if p not in {item["p"] for item in ctx["over"]}]
    if faltam:
        falta(prs, layout, faltam)
    extras = dados.outras()
    if len(extras) == 2:
        tres_tamanhos(prs, layout, ctx, extras)
    numerar(prs)
    prs.save(str(SAIDA))
    print(f"{SAIDA}  slides={len(prs.slides)}")


if __name__ == "__main__":
    main()
