import base64
import math
import os
import random
import unicodedata

from flask import Flask, jsonify, request, send_from_directory, session

from rdkit import Chem
from rdkit.Chem import AllChem

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__, static_folder=None)


app.secret_key = "quimica-termo-chave-de-sessao-escolar"



MOLECULAS = [
    {
        "id": 1,
        "nome": "Etanol",
        "funcao": "Álcool",
        "smiles": "CCO",
        "formula": "C₂H₆O",
        "grupo_funcional": "–OH (ligado a carbono saturado)",
        "descricao": "É o álcool presente em bebidas alcoólicas e também usado como combustível.",
        "dicas": [
            "Essa função apresenta o grupo hidroxila (–OH) ligado a um carbono saturado.",
            "Essa substância é encontrada em bebidas alcoólicas.",
            "O grupo funcional característico dessa função é –OH.",
            "A função orgânica começa com a letra 'A'.",
        ],
    },
    {
        "id": 2,
        "nome": "Metanol",
        "funcao": "Álcool",
        "smiles": "CO",
        "formula": "CH₄O",
        "grupo_funcional": "–OH (ligado a carbono saturado)",
        "descricao": "É tóxico e usado como solvente industrial e em combustíveis.",
        "dicas": [
            "Essa função apresenta o grupo hidroxila (–OH) ligado a um carbono saturado.",
            "Essa substância é tóxica e muito usada como solvente industrial.",
            "O grupo funcional característico dessa função é –OH.",
            "A função orgânica começa com a letra 'A'.",
        ],
    },
    {
        "id": 3,
        "nome": "Fenol",
        "funcao": "Fenol",
        "smiles": "c1ccc(O)cc1",
        "formula": "C₆H₆O",
        "grupo_funcional": "–OH ligado diretamente ao anel aromático",
        "descricao": "Usado como antisséptico e na fabricação de resinas e plásticos.",
        "dicas": [
            "Essa função apresenta o grupo hidroxila (–OH) ligado diretamente a um anel aromático.",
            "Essa substância é usada como antisséptico e na produção de resinas.",
            "O grupo funcional característico dessa função é –OH sobre o anel benzênico.",
            "A função orgânica começa com a letra 'F'.",
        ],
    },
    {
        "id": 4,
        "nome": "Metanal (Formaldeído)",
        "funcao": "Aldeído",
        "smiles": "C=O",
        "formula": "CH₂O",
        "grupo_funcional": "–CHO (carbonila na extremidade da cadeia)",
        "descricao": "Usado como conservante (formol) e na produção de resinas.",
        "dicas": [
            "Essa função apresenta uma carbonila (C=O) ligada a hidrogênio, na extremidade da cadeia.",
            "Essa substância é a base do formol, usado como conservante.",
            "O grupo funcional característico dessa função é –CHO.",
            "A função orgânica começa com a letra 'A'.",
        ],
    },
    {
        "id": 5,
        "nome": "Etanal (Acetaldeído)",
        "funcao": "Aldeído",
        "smiles": "CC=O",
        "formula": "C₂H₄O",
        "grupo_funcional": "–CHO (carbonila na extremidade da cadeia)",
        "descricao": "É formado na fermentação e no metabolismo do etanol no corpo humano.",
        "dicas": [
            "Essa função apresenta uma carbonila (C=O) ligada a hidrogênio, na extremidade da cadeia.",
            "Essa substância é formada quando o corpo humano metaboliza o etanol.",
            "O grupo funcional característico dessa função é –CHO.",
            "A função orgânica começa com a letra 'A'.",
        ],
    },
    {
        "id": 6,
        "nome": "Propanona (Acetona)",
        "funcao": "Cetona",
        "smiles": "CC(=O)C",
        "formula": "C₃H₆O",
        "grupo_funcional": "C=O (carbonila entre dois carbonos)",
        "descricao": "É o solvente usado em removedores de esmalte.",
        "dicas": [
            "Essa função apresenta uma carbonila (C=O) ligada a dois carbonos, no interior da cadeia.",
            "Essa substância é o solvente usado em removedores de esmalte.",
            "O grupo funcional característico dessa função é C=O entre dois carbonos.",
            "A função orgânica começa com a letra 'C'.",
        ],
    },
    {
        "id": 7,
        "nome": "Butanona",
        "funcao": "Cetona",
        "smiles": "CCC(=O)C",
        "formula": "C₄H₈O",
        "grupo_funcional": "C=O (carbonila entre dois carbonos)",
        "descricao": "Usada como solvente industrial de tintas e adesivos.",
        "dicas": [
            "Essa função apresenta uma carbonila (C=O) ligada a dois carbonos, no interior da cadeia.",
            "Essa substância é usada como solvente de tintas e adesivos.",
            "O grupo funcional característico dessa função é C=O entre dois carbonos.",
            "A função orgânica começa com a letra 'C'.",
        ],
    },
    {
        "id": 8,
        "nome": "Ácido acético",
        "funcao": "Ácido carboxílico",
        "smiles": "CC(=O)O",
        "formula": "C₂H₄O₂",
        "grupo_funcional": "–COOH (carboxila)",
        "descricao": "É o componente principal do vinagre.",
        "dicas": [
            "Essa função apresenta o grupo carboxila: uma carbonila e uma hidroxila no mesmo carbono.",
            "Essa substância é o componente principal do vinagre.",
            "O grupo funcional característico dessa função é –COOH.",
            "A função orgânica começa com a letra 'Á'.",
        ],
    },
    {
        "id": 9,
        "nome": "Ácido fórmico",
        "funcao": "Ácido carboxílico",
        "smiles": "C(=O)O",
        "formula": "CH₂O₂",
        "grupo_funcional": "–COOH (carboxila)",
        "descricao": "Presente na ferroada de formigas e abelhas.",
        "dicas": [
            "Essa função apresenta o grupo carboxila: uma carbonila e uma hidroxila no mesmo carbono.",
            "Essa substância está presente na ferroada de formigas e abelhas.",
            "O grupo funcional característico dessa função é –COOH.",
            "A função orgânica começa com a letra 'Á'.",
        ],
    },
    {
        "id": 10,
        "nome": "Acetato de etila",
        "funcao": "Éster",
        "smiles": "CC(=O)OCC",
        "formula": "C₄H₈O₂",
        "grupo_funcional": "–COO– (éster)",
        "descricao": "Tem odor de frutas e é usado em removedores de esmalte e colas.",
        "dicas": [
            "Essa função é formada pela reação entre um ácido carboxílico e um álcool, com perda de água.",
            "Essa substância tem odor de frutas e aparece em removedores de esmalte.",
            "O grupo funcional característico dessa função é –COO–.",
            "A função orgânica começa com a letra 'É'.",
        ],
    },
    {
        "id": 11,
        "nome": "Éter dietílico",
        "funcao": "Éter",
        "smiles": "CCOCC",
        "formula": "C₄H₁₀O",
        "grupo_funcional": "R–O–R' (oxigênio entre dois carbonos)",
        "descricao": "Foi um dos primeiros anestésicos usados na medicina.",
        "dicas": [
            "Essa função apresenta um oxigênio ligado a dois carbonos, sem hidrogênio no oxigênio.",
            "Essa substância foi um dos primeiros anestésicos usados na medicina.",
            "O grupo funcional característico dessa função é R–O–R'.",
            "A função orgânica começa com a letra 'É'.",
        ],
    },
    {
        "id": 12,
        "nome": "Metilamina",
        "funcao": "Amina",
        "smiles": "CN",
        "formula": "CH₅N",
        "grupo_funcional": "–NH₂ (nitrogênio ligado a carbono)",
        "descricao": "Tem odor forte, semelhante ao de peixe em decomposição.",
        "dicas": [
            "Essa função é derivada da amônia, com hidrogênios substituídos por radicais orgânicos.",
            "Essa substância tem odor forte, parecido com peixe em decomposição.",
            "O grupo funcional característico dessa função envolve nitrogênio ligado a carbono.",
            "A função orgânica começa com a letra 'A'.",
        ],
    },
    {
        "id": 13,
        "nome": "Etilamina",
        "funcao": "Amina",
        "smiles": "CCN",
        "formula": "C₂H₇N",
        "grupo_funcional": "–NH₂ (nitrogênio ligado a carbono)",
        "descricao": "Usada como intermediário na síntese de fármacos e agroquímicos.",
        "dicas": [
            "Essa função é derivada da amônia, com hidrogênios substituídos por radicais orgânicos.",
            "Essa substância é usada como intermediário na síntese de fármacos.",
            "O grupo funcional característico dessa função envolve nitrogênio ligado a carbono.",
            "A função orgânica começa com a letra 'A'.",
        ],
    },
    {
        "id": 14,
        "nome": "Metano",
        "funcao": "Hidrocarboneto",
        "smiles": "C",
        "formula": "CH₄",
        "grupo_funcional": "Apenas C e H, sem heteroátomos",
        "descricao": "É o principal componente do gás natural.",
        "dicas": [
            "Essa função é formada exclusivamente por carbono e hidrogênio, sem outros elementos.",
            "Essa substância é o principal componente do gás natural.",
            "Não há grupo funcional heteroatômico; só existem carbono e hidrogênio.",
            "A função orgânica começa com a letra 'H'.",
        ],
    },
    {
        "id": 15,
        "nome": "Eteno",
        "funcao": "Hidrocarboneto",
        "smiles": "C=C",
        "formula": "C₂H₄",
        "grupo_funcional": "Apenas C e H, sem heteroátomos",
        "descricao": "É usado na fabricação do plástico polietileno e para amadurecer frutas.",
        "dicas": [
            "Essa função é formada exclusivamente por carbono e hidrogênio, sem outros elementos.",
            "Essa substância é usada para fabricar plástico e para amadurecer frutas.",
            "Não há grupo funcional heteroatômico; só existem carbono e hidrogênio.",
            "A função orgânica começa com a letra 'H'.",
        ],
    },
    {
        "id": 16,
        "nome": "Benzeno",
        "funcao": "Hidrocarboneto",
        "smiles": "c1ccccc1",
        "formula": "C₆H₆",
        "grupo_funcional": "Apenas C e H, sem heteroátomos (anel aromático)",
        "descricao": "É um anel aromático usado como solvente e matéria-prima industrial.",
        "dicas": [
            "Essa função é formada exclusivamente por carbono e hidrogênio, sem outros elementos.",
            "Essa substância forma um anel aromático usado como solvente industrial.",
            "Não há grupo funcional heteroatômico; só existem carbono e hidrogênio.",
            "A função orgânica começa com a letra 'H'.",
        ],
    },
]

MOLECULAS_POR_ID = {m["id"]: m for m in MOLECULAS}


# ---------------------------------------------------------------------------
# 2. NORMALIZAÇÃO DE TEXTO
# ---------------------------------------------------------------------------
def normalizar(texto: str) -> str:
    
    if texto is None:
        return ""
    texto = texto.strip().lower()

   
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(ch for ch in texto if not unicodedata.combining(ch))

    texto = "".join(ch for ch in texto if ch.isalpha())
    return texto



def comparar_tentativa(tentativa_norm: str, resposta_norm: str):
    
    tamanho = len(tentativa_norm)
    resultado = ["ausente"] * tamanho

  
    contagem_resposta = {}
    for ch in resposta_norm:
        contagem_resposta[ch] = contagem_resposta.get(ch, 0) + 1

 
    for i in range(tamanho):
        if i < len(resposta_norm) and tentativa_norm[i] == resposta_norm[i]:
            resultado[i] = "correta"
            contagem_resposta[tentativa_norm[i]] -= 1


    for i in range(tamanho):
        if resultado[i] == "correta":
            continue
        ch = tentativa_norm[i]
        if contagem_resposta.get(ch, 0) > 0:
            resultado[i] = "presente"
            contagem_resposta[ch] -= 1
        else:
            resultado[i] = "ausente"

    return resultado




ORDEM_DA_LIGACAO = {
    Chem.BondType.SINGLE: 1,
    Chem.BondType.DOUBLE: 2,
    Chem.BondType.TRIPLE: 3,
}


def extrair_atomos_e_ligacoes(smiles: str):
    
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"SMILES inválido: {smiles}")

    
    Chem.Kekulize(mol, clearAromaticFlags=True)

    
    AllChem.Compute2DCoords(mol)
    conformador = mol.GetConformer()

    atomos = []
    for atomo in mol.GetAtoms():
        posicao = conformador.GetAtomPosition(atomo.GetIdx())
        atomos.append({
            "simbolo": atomo.GetSymbol(),
            "x": posicao.x,
            "y": posicao.y,
        })

    ligacoes = []
    for ligacao in mol.GetBonds():
        ligacoes.append({
            "inicio": ligacao.GetBeginAtomIdx(),
            "fim": ligacao.GetEndAtomIdx(),
            "ordem": ORDEM_DA_LIGACAO.get(ligacao.GetBondType(), 1),
        })

    return atomos, ligacoes


def construir_svg(atomos, ligacoes, tamanho_canvas=320, margem=44):
    
    xs = [a["x"] for a in atomos]
    ys = [a["y"] for a in atomos]

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    largura_mol = max(max_x - min_x, 1e-3)
    altura_mol = max(max_y - min_y, 1e-3)

    area_disponivel = tamanho_canvas - 2 * margem
    escala = area_disponivel / max(largura_mol, altura_mol)

    
    deslocamento_x = (area_disponivel - largura_mol * escala) / 2
    deslocamento_y = (area_disponivel - altura_mol * escala) / 2

    def transformar(x, y):
        
        px = margem + deslocamento_x + (x - min_x) * escala
        py = margem + deslocamento_y + (max_y - y) * escala
        return px, py

    posicoes_em_pixel = [transformar(a["x"], a["y"]) for a in atomos]

    partes_svg = []

    
    for ligacao in ligacoes:
        x1, y1 = posicoes_em_pixel[ligacao["inicio"]]
        x2, y2 = posicoes_em_pixel[ligacao["fim"]]
        partes_svg.append(_svg_ligacao(x1, y1, x2, y2, ligacao["ordem"]))

    
    for (px, py), atomo in zip(posicoes_em_pixel, atomos):
        if atomo["simbolo"] != "C":
            partes_svg.append(_svg_rotulo_atomo(px, py, atomo["simbolo"]))

    corpo = "\n  ".join(partes_svg)

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {tamanho_canvas} {tamanho_canvas}" '
        f'width="{tamanho_canvas}" height="{tamanho_canvas}">\n'
        f'  <rect width="100%" height="100%" fill="white" />\n'
        f'  {corpo}\n'
        f'</svg>'
    )


def _svg_ligacao(x1, y1, x2, y2, ordem):
    """Desenha uma ligação simples, dupla ou tripla entre dois pontos."""
    dx, dy = x2 - x1, y2 - y1
    comprimento = math.hypot(dx, dy) or 1.0
    
    perp_x, perp_y = -dy / comprimento, dx / comprimento
    afastamento = 3.6

    if ordem == 1:
        deslocamentos = [0.0]
    elif ordem == 2:
        deslocamentos = [-afastamento / 2, afastamento / 2]
    else:  # tripla
        deslocamentos = [-afastamento, 0.0, afastamento]

    linhas = []
    for deslocamento in deslocamentos:
        ox, oy = perp_x * deslocamento, perp_y * deslocamento
        linhas.append(
            f'<line x1="{x1 + ox:.2f}" y1="{y1 + oy:.2f}" '
            f'x2="{x2 + ox:.2f}" y2="{y2 + oy:.2f}" '
            f'stroke="#1f2d2b" stroke-width="2.4" stroke-linecap="round" />'
        )
    return "\n  ".join(linhas)


def _svg_rotulo_atomo(x, y, simbolo):
    
    largura_fundo = 10 * len(simbolo) + 8
    return (
        f'<rect x="{x - largura_fundo / 2:.2f}" y="{y - 12:.2f}" '
        f'width="{largura_fundo:.2f}" height="24" fill="white" />\n  '
        f'<text x="{x:.2f}" y="{y + 6:.2f}" text-anchor="middle" '
        f'font-family="Arial, Helvetica, sans-serif" font-size="18" '
        f'font-weight="600" fill="#1f2d2b">{simbolo}</text>'
    )


def gerar_imagem_molecula(smiles: str) -> str:
    
    atomos, ligacoes = extrair_atomos_e_ligacoes(smiles)
    svg = construir_svg(atomos, ligacoes)

    svg_base64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    return f"data:image/svg+xml;base64,{svg_base64}"



@app.route("/")
def pagina_inicial():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/style.css")
def arquivo_css():
    return send_from_directory(BASE_DIR, "style.css")


@app.route("/script.js")
def arquivo_js():
    return send_from_directory(BASE_DIR, "script.js")



@app.route("/api/nova_molecula")
def api_nova_molecula():
    
    ultima_id = session.get("ultima_molecula_id")

    candidatas = MOLECULAS
    if ultima_id is not None and len(MOLECULAS) > 1:
        candidatas = [m for m in MOLECULAS if m["id"] != ultima_id]

    molecula = random.choice(candidatas)

    session["molecula_atual_id"] = molecula["id"]
    session["ultima_molecula_id"] = molecula["id"]
    session["dicas_usadas"] = 0

    imagem = gerar_imagem_molecula(molecula["smiles"])

    return jsonify({
        "imagem": imagem,
        "total_dicas": len(molecula["dicas"]),
    })


@app.route("/api/tentativa", methods=["POST"])
def api_tentativa():
    
    dados = request.get_json(silent=True) or {}
    tentativa_bruta = dados.get("tentativa", "")

    molecula_id = session.get("molecula_atual_id")
    if molecula_id is None or molecula_id not in MOLECULAS_POR_ID:
        return jsonify({"erro": "Nenhuma molécula ativa. Sorteie uma nova molécula."}), 400

    molecula = MOLECULAS_POR_ID[molecula_id]

    tentativa_norm = normalizar(tentativa_bruta)
    resposta_norm = normalizar(molecula["funcao"])

    if tentativa_norm == "":
        return jsonify({"erro": "Digite uma resposta antes de enviar."}), 400

    diff = comparar_tentativa(tentativa_norm, resposta_norm)
    acertou = tentativa_norm == resposta_norm

    resposta_json = {
        "tentativa_normalizada": tentativa_norm,
        "diff": diff,
        "acertou": acertou,
    }

    if acertou:
        resposta_json["info"] = {
            "nome": molecula["nome"],
            "funcao": molecula["funcao"],
            "formula": molecula["formula"],
            "grupo_funcional": molecula["grupo_funcional"],
            "descricao": molecula["descricao"],
        }

    return jsonify(resposta_json)


@app.route("/api/dica")
def api_dica():
    
    molecula_id = session.get("molecula_atual_id")
    if molecula_id is None or molecula_id not in MOLECULAS_POR_ID:
        return jsonify({"erro": "Nenhuma molécula ativa. Sorteie uma nova molécula."}), 400

    molecula = MOLECULAS_POR_ID[molecula_id]
    dicas_usadas = session.get("dicas_usadas", 0)

    if dicas_usadas >= len(molecula["dicas"]):
        return jsonify({
            "dica": None,
            "dicas_usadas": dicas_usadas,
            "total_dicas": len(molecula["dicas"]),
            "mensagem": "Você já usou todas as dicas disponíveis para essa molécula.",
        })

    dica_texto = molecula["dicas"][dicas_usadas]
    session["dicas_usadas"] = dicas_usadas + 1

    return jsonify({
        "dica": dica_texto,
        "dicas_usadas": dicas_usadas + 1,
        "total_dicas": len(molecula["dicas"]),
    })


if __name__ == "__main__":
    
    app.run(debug=True, port=5000)