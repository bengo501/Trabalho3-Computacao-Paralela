"""Relatório do T3: uma página de análise e, em seguida, o código numerado.

Uma coluna. Os números saem de dados.py, o mesmo módulo dos slides.
Séries com menos de dez repetições não entram.
"""

import sys
from pathlib import Path

from fpdf import FPDF

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dados

PDF = Path(__file__).resolve().parent / "relatorio.pdf"
FONT = r"C:\Windows\Fonts\arial.ttf"
FONTB = r"C:\Windows\Fonts\arialbd.ttf"
FONTI = r"C:\Windows\Fonts\ariali.ttf"
FONTC = r"C:\Windows\Fonts\consola.ttf"
SRC = Path(__file__).resolve().parents[1] / "src"
LIMITE = 284


class Doc(FPDF):
    def __init__(self):
        super().__init__(format="A4", unit="mm")
        self.add_font("Arial", "", FONT)
        self.add_font("Arial", "B", FONTB)
        self.add_font("Arial", "I", FONTI)
        self.add_font("Consolas", "", FONTC)
        self.set_auto_page_break(False)
        self.set_margins(14, 11, 14)
        self.add_page()

    def p(self, texto, size=9, estilo="", h=3.25):
        self.set_font("Arial", estilo, size)
        self.set_x(14)
        self.multi_cell(self.epw, h, texto, align="L")
        if self.page != 1 or self.get_y() > LIMITE:
            raise SystemExit(f"a analise passou de uma pagina (y={self.get_y():.1f})")

    def secao(self, texto):
        self.ln(0.6)
        self.p(texto, 9.5, "B", 4.0)

    def tabela(self, cabecalho, linhas, larguras):
        self.set_font("Arial", "B", 7.5)
        self.set_x(14)
        for largura, texto in zip(larguras, cabecalho):
            self.cell(largura, 3.6, texto, border=1, align="C")
        self.ln(3.6)
        self.set_font("Arial", "", 7.5)
        for linha in linhas:
            self.set_x(14)
            for largura, texto in zip(larguras, linha):
                self.cell(largura, 3.5, texto, border=1, align="C")
            self.ln(3.5)
        if self.page != 1 or self.get_y() > LIMITE:
            raise SystemExit(f"tabela passou de uma pagina (y={self.get_y():.1f})")

    def legenda(self, texto):
        self.ln(0.4)
        self.p(texto, 8, "I", 3.3)


def analise(pdf, ctx):
    pdf.set_font("Arial", "B", 11)
    pdf.set_xy(14, 9)
    pdf.cell(0, 4.6, "Trabalho 3: divisão e conquista com MPI", align="L")
    pdf.set_font("Arial", "", 8.5)
    pdf.set_xy(14, 13.6)
    pdf.cell(0, 3.6, "Bernardo Klein Heitz  ·  https://github.com/bengo501/Trabalho3-Computacao-Paralela", align="L")
    pdf.set_xy(14, 17.4)

    por_p = {linha["p"]: linha for linha in ctx["arvore"]}
    for p in dados.PS_ARVORE:
        if p not in por_p:
            raise SystemExit(f"a arvore original com P={p} ainda nao tem 10 repeticoes")
    p1, p3, p7, p15, p31 = (por_p[p] for p in dados.PS_ARVORE)
    prev = ctx["previsto"]
    duas = 2 * prev[31]

    pdf.secao("1. Modelagem")
    pdf.p(
        "A raiz gera o vetor decrescente, de n até 1. O rank r manda a metade esquerda para "
        "2r+1 e a direita para 2r+2. A folha ordena com o bubble sort do sequencial.c do "
        "professor. O pai intercala na volta. Com n = 40 e delta = 10, as folhas p3 a p6 "
        "ficam com dez elementos e o vetor termina em 1..n."
    )
    pdf.p(
        "O processo divide só quando o pedaço passa de delta e o filho da direita existe "
        "(comum.c:82). Delta = ceil(2n/(P+1)) (comum.c:77). Com P = 2^k−1 isso enche a árvore "
        "e as folhas ficam do mesmo tamanho. Se o delta deixasse um "
        "rank sem mensagem, a raiz aborta (arvore.c:81): ninguém fica preso no MPI_Probe."
    )
    pdf.p(
        "As duas metades saem antes de qualquer espera pelo resultado (arvore.c:132–136). "
        "O filho não sabe o tamanho: MPI_Probe no pai, MPI_Get_count e então MPI_Recv "
        "(arvore.c:105–109). A tag é 1 nos dois sentidos. O relógio é MPI_Wtime na raiz, "
        "aberto depois de gerar o vetor (arvore.c:118) e fechado com o vetor já intercalado "
        "(arvore.c:143). A inicialização fica de fora. Toda execução conta quantos v[i] "
        "diferem de i+1 e imprime verificacao=OK ou ERRO."
    )
    pdf.p(
        "A versão balanceada não usa um delta. O processo manda só a metade direita ao rank "
        "r+2^nível e fica com a esquerda (balanceada.c:56–59), no desenho de Radenski "
        "(PDPTA 2011, GPL-2.0). A folha segue sendo bubble sort. Com P potência de 2 a folha "
        "fica com n/P; com P = 31, o dobro. O envio é MPI_Isend, e o MPI_Recv só reescreve "
        "o buffer depois que o ajudante já recebeu o pedaço."
    )

    pdf.secao("2. Medição")
    pdf.p(
        "Cluster Atlântica, atlantica03 e atlantica04, sbatch --exclusive, sempre esses dois "
        "nós, srun --distribution=block. lscpu nos dois: Xeon E5520 a 2,27 GHz, 2 soquetes, "
        "4 núcleos por soquete, 2 threads. São 8 núcleos físicos e 16 lógicos por nó; nos dois "
        "nós, 16 núcleos e 32 threads. Open MPI 4.1.1. As três versões usam -O2 -std=c11. "
        "O sequencial não liga MPI; o tempo dele é clock_gettime em volta só da ordenação "
        "(sequencial.c:71–75)."
    )
    pdf.p(
        f"n = {ctx['n']}. T1, mediana de dez rodadas, é {ctx['t1_txt']} s "
        f"(mínimo {ctx['t1_min_txt']}, máximo {ctx['t1_max_txt']}), dentro de 30 a 60 s. "
        "T1delta é a mesma árvore num processo só. S = T1/Tp junta o algoritmo e o paralelismo "
        "e pode passar de P. Sdelta = T1delta/Tp é só o paralelismo. E = Sdelta/P. "
        "Nas 50 execuções da tabela 1, verificacao=OK."
    )

    larguras = [14, 24, 24, 24, 28, 20, 26, 22]
    pdf.ln(0.8)
    pdf.tabela(
        ["P", "mediana", "mínimo", "máximo", "T1delta", "S", "Sdelta", "E"],
        [
            [str(linha["p"]), linha["med"], linha["min"], linha["max"], linha["t1d"], linha["s"], linha["sd"], linha["e"]]
            for linha in ctx["arvore"]
        ],
        larguras,
    )
    pdf.legenda(
        "Tabela 1. Árvore original, tempos em segundos. Mediana, mínimo e máximo de dez "
        "repetições. S = T1/Tp, Sdelta = T1delta/Tp, E = Sdelta/P. Em P = 1, T1delta é o próprio T1."
    )

    pdf.secao("3. O que a tabela separa")
    pdf.p(
        "O bubble é quadrático e o vetor decrescente não aciona a parada antecipada. "
        f"Um bubble de n/2^k custa T1/4^k. Até P = 7 a mediana acompanha essa conta. "
        f"Em P = 3, T1delta é {dados.frac(p3['t1d_f'] / ctx['t1'])} de T1 (previsto 0,500) e Tp é "
        f"{p3['med']} s contra T1/4 = {dados.tempo(prev[3])} s. "
        f"Em P = 7, Tp é {p7['med']} s contra T1/16 = {dados.tempo(prev[7])} s."
    )
    pdf.p(
        "Só as folhas fazem o trabalho quadrático. Com P processos, (P+1)/2 ordenam e "
        "(P−1)/2 esperam e intercalam. O teto de E é o número de folhas sobre P: 2/3, 4/7, "
        f"8/15 e 16/31. P = 3 chega a {p3['e']}, que é 2/3, e P = 7 a {p7['e']}, contra 4/7 = 0,57. "
        ""
        f"Em P = 1 a árvore mede o mesmo bubble de T1: {p1['med']} s contra {ctx['t1_txt']} s. "
        f"A diferença é {dados.tempo(ctx['p1_diff'])} s, 0,07%. S e E ficam em 1,00."
    )
    pdf.p(
        "As folhas são os ranks altos. A distribuição block junta ranks consecutivos no mesmo "
        "nó, então um nó fica com os internos e o outro com as folhas, sobre 8 núcleos físicos. "
        f"Em P = 15 ainda cabe uma leva: o modelo da folha dá T1/64 = {dados.tempo(prev[15])} s "
        f"e a mediana foi {p15['med']} s. "
        f"Em P = 31 são 16 folhas para 8 núcleos, duas levas: 2·T1/256 = {dados.tempo(duas)} s, "
        f"e a mediana foi {p31['med']} s, a {dados.ms(abs(p31['tp'] - duas))} ms da conta. "
        "Nesta referência a segunda thread não encurtou a leva. "
        f"Sdelta passa de {p15['sd']} em P = 15 para {p31['sd']} em P = 31, com P dobrando, "
        f"e E cai de {p15['e']} para {p31['e']}. "
        f"O salto de S até {p31['s']} vem de T1/T1delta = {p31['ganho']}, a troca de um bubble "
        "de n por dezesseis de n/16, não de 31 núcleos em paralelo."
    )

    if ctx["balanceada"]:
        pdf.secao("4. Versão balanceada")
        escreve_balanceada(pdf, ctx)
    if ctx["over"]:
        pdf.secao("5. De 63 a 1023 processos" if ctx["balanceada"] else "4. De 63 a 1023 processos")
        escreve_over(pdf, ctx)
    faltam = [p for p in dados.PS_OVER if p not in {item["p"] for item in ctx["over"]}]
    if not ctx["balanceada"]:
        pdf.p("A série balanceada ainda não fechou as dez repetições. A tabela 2 entra sem alterar a tabela 1.")
    elif faltam:
        lista = ", ".join(str(p) for p in faltam)
        pdf.p(
            f"P = {lista} ainda não fecharam as duas políticas com dez repetições. "
            "Essas linhas entram na tabela 3 sem alterar os números acima."
        )
    extras = dados.outras()
    if len(extras) == 2:
        pdf.secao("6. Três tamanhos")
        pdf.p(texto_tres(ctx, extras))
    pdf.p(
        "Uso de IA. O código MPI, os scripts e este texto foram escritos com apoio do Cursor "
        "(Grok 4.7). As medições são do cluster. O bubble sort e a intercalação vêm do "
        "sequencial.c do professor. A árvore balanceada deriva de mpi_mergesort.c de Atanas "
        "Radenski (PDPTA 2011, GPL-2.0)."
    )


def por_p(ctx, serie, p):
    return next(linha for linha in ctx[serie] if linha["p"] == p)


def vez(x):
    return f"{x:.1f}".replace(".", ",")


def texto_tres(ctx, extras):
    todos = [("45 s", ctx)] + extras
    sds = [por_p(c, "arvore", 31)["sd"] for _, c in todos]
    ondas = [c["arvore"] and por_p(c, "arvore", 31)["tp"] / (2 * c["previsto"][31]) for _, c in todos]
    folga = [round((1 - ondas[i]) * 100) for i in (1, 2)]
    p2 = [por_p(c, "balanceada", 2)["sd"] for _, c in todos]
    b16 = [por_p(c, "balanceada", 16)["sd"] for _, c in todos]
    ns = [str(c["n"]) for _, c in todos]
    t1s = [c["t1_txt"] for _, c in todos]

    def fator(c, qual):
        item = next(i for i in c["over"] if i["p"] == 1023)
        return item[qual]["tp"] / item["t1d_f"]

    ativa = [vez(fator(c, "ativa")) for _, c in todos]
    cede = [vez(fator(c, "yield")) for _, c in todos]
    return (
        f"As mesmas séries, com n = {ns[1]} (T1 = {t1s[1]} s) e n = {ns[2]} "
        f"(T1 = {t1s[2]} s), repetem P = 3 e P = 7 na conta da folha. "
        f"Em P = 31, Sdelta sobe de {sds[0]} para {sds[1]} e {sds[2]}, "
        f"{folga[0]}% e {folga[1]}% abaixo das duas levas: a segunda thread "
        "recupera parte da leva. "
        f"O P = 16 balanceado fica em {b16[0]}, {b16[1]} e {b16[2]}, duas folhas "
        "em série, e deixa de acompanhar esse P = 31. "
        f"O P = 2 balanceado permanece em Sdelta = {p2[0]}. "
        f"Em P = 1023 a espera ativa vale {ativa[0]}, {ativa[1]} e {ativa[2]} vezes "
        f"a árvore sequencial; com o núcleo cedido, {cede[0]}, {cede[1]} e {cede[2]} vezes."
    )


def escreve_balanceada(pdf, ctx):
    por_p = {linha["p"]: linha for linha in ctx["balanceada"]}
    larguras = [14, 24, 24, 24, 28, 20, 26, 22]
    pdf.tabela(
        ["P", "mediana", "mínimo", "máximo", "T1bal", "S", "Sdelta", "E"],
        [
            [str(linha["p"]), linha["med"], linha["min"], linha["max"], linha["t1d"], linha["s"], linha["sd"], linha["e"]]
            for linha in ctx["balanceada"]
        ],
        larguras,
    )
    pdf.legenda(
        "Tabela 2. Versão balanceada. T1bal é a mesma árvore de ajudantes num processo só. "
        "Sdelta isola o paralelismo. E = Sdelta/P."
    )
    if all(p in por_p for p in (2, 4, 8, 16, 31, 32)):
        p2, p4, p8 = por_p[2], por_p[4], por_p[8]
        p16, p31, p32 = por_p[16], por_p[31], por_p[32]
        orig = {linha["p"]: linha for linha in ctx["arvore"]}
        pdf.p(
            f"Na tabela 2, P = 2 não paraleliza: Tp = {p2['med']} s e T1bal = {p2['t1d']} s, Sdelta = {p2['sd']}. "
            "A esquerda é folha e o ajudante fica no Probe. "
            f"De P = 4 em diante outro envio destrava: {p4['med']} s "
            f"e {p8['med']} s, contra duas folhas em série "
            f"({dados.tempo(2 * ctx['t1'] / 16)} s e {dados.tempo(2 * ctx['t1'] / 64)} s). "
            f"Nesta referência, P = 16 ({p16['med']} s) fica junto da original em P = 31 ({orig[31]['med']} s). "
            f"P = 31 fica em {p31['med']} s e P = 32 em {p32['med']} s: o pedaço dobrado custa "
            f"T1/256 = {dados.tempo(ctx['t1'] / 256)} s."
        )


def escreve_over(pdf, ctx):
    larguras = [16, 26, 32, 32, 26, 28, 22]
    pdf.tabela(
        ["P", "T1delta", "espera ativa", "yield", "Sdelta ativa", "Sdelta yield", "E yield"],
        [
            [
                str(item["p"]),
                item["t1d"],
                f"{item['ativa']['med']} ({item['ativa']['min']}–{item['ativa']['max']})",
                f"{item['yield']['med']} ({item['yield']['min']}–{item['yield']['max']})",
                item["ativa"]["sd"],
                item["yield"]["sd"],
                item["yield"]["e"],
            ]
            for item in ctx["over"]
        ],
        larguras,
    )
    pdf.legenda(
        "Tabela 3. Acima de 32 processos, srun -O nos mesmos dois nós. E = Sdelta/32. "
        "Entre parênteses, mínimo e máximo."
    )
    encurtou, alongou, empatou = [], [], []
    for item in ctx["over"]:
        ativa, cede = item["ativa"], item["yield"]
        cruza = ativa["tp_max"] >= cede["tp_min"] and cede["tp_max"] >= ativa["tp_min"]
        if cruza or abs(cede["tp"] - ativa["tp"]) <= 0.1 * ativa["tp"]:
            empatou.append(str(item["p"]))
        elif cede["tp"] < ativa["tp"]:
            encurtou.append(str(item["p"]))
        else:
            alongou.append(str(item["p"]))
    partes = []
    if encurtou:
        partes.append(
            "Na tabela 3 a variável está escrita em 0 e em 1. Ceder a CPU encurtou P = "
            + ", ".join(encurtou)
            + ". O 0 ficou na faixa da série em que a variável era apagada."
        )
    if alongou:
        partes.append("Ceder a CPU alongou P = " + ", ".join(alongou) + ". A espera ativa não era o atraso dessas linhas.")
    if empatou:
        partes.append(
            "Em P = " + ", ".join(empatou) + " as duas políticas não se separam da variação das dez repetições."
        )
    piores = [item for item in ctx["over"] if item["ativa"]["tp_min"] > item["t1d_f"]]
    if piores:
        exemplo = max(piores, key=lambda item: item["ativa"]["tp"] / item["t1d_f"])
        partes.append(
            f"Em P = {exemplo['p']}, o mínimo da espera ativa ({exemplo['ativa']['min']} s) ficou "
            f"acima da mediana sequencial ({exemplo['t1d']} s). Com yield, {exemplo['yield']['med']} s: "
            "os processos a mais, girando nos 32 threads, tiram a CPU de quem ainda ordena."
        )
    pdf.p(" ".join(partes))


def codigo(pdf):
    pdf.set_auto_page_break(True, margin=12)
    arquivos = [
        ("arvore.c", "Versão original"),
        ("balanceada.c", "Versão balanceada"),
        ("sequencial.c", "Referências sequenciais"),
        ("comum.c", "Ordenação, delta e numeração dos ranks"),
        ("comum.h", "Contratos compartilhados"),
    ]
    for nome, titulo in arquivos:
        linhas = (SRC / nome).read_text(encoding="utf-8").splitlines()
        pdf.add_page()
        pdf.set_font("Arial", "B", 11)
        pdf.set_x(14)
        pdf.cell(0, 6, f"{nome}  ·  {titulo}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)
        for numero, linha in enumerate(linhas, 1):
            texto = f"{numero:4d}  {linha.rstrip()}"
            pdf.set_font("Consolas", "", 7.5)
            if pdf.get_string_width(texto) > pdf.epw:
                pdf.set_font("Consolas", "", 6)
            pdf.set_x(14)
            pdf.cell(0, 3.25, texto, new_x="LMARGIN", new_y="NEXT")


def main():
    ctx = dados.contexto()
    pdf = Doc()
    analise(pdf, ctx)
    fim = pdf.get_y()
    codigo(pdf)
    pdf.output(str(PDF))
    print(f"{PDF}  paginas={pdf.page}  analise_y={fim:.1f}")


if __name__ == "__main__":
    main()
