from flask import Flask, request, jsonify, render_template
import re

app = Flask(__name__)

DENSIDADES_TINTA_G_ML = {
    "Cyan": 1.29,
    "Brown": 1.32,
    "Beige": 1.27,
    "Black": 1.28,
    "Pink": 1.28,
    "Blue": 1.18,
    "Yellow": 1.32,
    "Luster": 1.10,
    "Reactive": 1.10
}

COR_MAP_PT_BR = {
    "Cyan": "Ciano",
    "Brown": "Marrom",
    "Beige": "Bege",
    "Black": "Preto",
    "Pink": "Rosa",
    "Blue": "Azul",
    "Yellow": "Amarelo",
    "Luster": "Brilho",
    "Reactive": "Reativo"
}

GOTAS_PL = {
    1: 12,
    2: 24,
    3: 36
}
INCH_PARA_M = 0.0254

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload-multi', methods=['POST'])
def upload_multi_files():
    if 'files[]' not in request.files or not request.files.getlist('files[]'):
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    arquivos = request.files.getlist('files[]')
    porcentagem_str = request.form.get('porcentagem')

    try:
        porcentagem = float(porcentagem_str)
        fator_porcentagem = porcentagem / 100.0
    except (ValueError, TypeError):
        return jsonify({"error": "Porcentagem inválida"}), 400

    max_dots_por_nivel = {}
    area_total_m2 = 0
    
    cores_na_ordem = []
    
    for arquivo in arquivos:
        try:
            conteudo_arquivo = arquivo.stream.read().decode("utf-8")
        except UnicodeDecodeError:
            return jsonify({"error": f"Erro ao ler o arquivo {arquivo.filename}. Verifique se é um arquivo de texto válido."}), 400
        
        sum_dots_por_nivel_no_arquivo = {}
        
        canais_do_arquivo = re.findall(r'\[Channel_(\d+)\].*?Color=(\w+).*?Dots_Level_1=(\d+).*?Dots_Level_2=(\d+).*?Dots_Level_3=(\d+)', conteudo_arquivo, re.DOTALL)
        
        cores_na_ordem.extend([c[1] for c in canais_do_arquivo])

        for _, cor_en, dots_l1, dots_l2, dots_l3 in canais_do_arquivo:
            dots_l1 = int(dots_l1)
            dots_l2 = int(dots_l2)
            dots_l3 = int(dots_l3)
            
            if cor_en not in sum_dots_por_nivel_no_arquivo:
                sum_dots_por_nivel_no_arquivo[cor_en] = {'l1': 0, 'l2': 0, 'l3': 0}
            
            sum_dots_por_nivel_no_arquivo[cor_en]['l1'] += dots_l1
            sum_dots_por_nivel_no_arquivo[cor_en]['l2'] += dots_l2
            sum_dots_por_nivel_no_arquivo[cor_en]['l3'] += dots_l3

        for cor_en, dots in sum_dots_por_nivel_no_arquivo.items():
            if cor_en not in max_dots_por_nivel:
                max_dots_por_nivel[cor_en] = {'l1': 0, 'l2': 0, 'l3': 0}
            
            if dots['l1'] > max_dots_por_nivel[cor_en]['l1']:
                max_dots_por_nivel[cor_en]['l1'] = dots['l1']
            if dots['l2'] > max_dots_por_nivel[cor_en]['l2']:
                max_dots_por_nivel[cor_en]['l2'] = dots['l2']
            if dots['l3'] > max_dots_por_nivel[cor_en]['l3']:
                max_dots_por_nivel[cor_en]['l3'] = dots['l3']

    consumo_por_cor_lista = []
    
    cores_unicas_na_ordem = list(dict.fromkeys(cores_na_ordem))

    for cor_en in cores_unicas_na_ordem:
        dots = max_dots_por_nivel.get(cor_en)
        if dots:
            volume_cor_pl = (dots['l1'] * GOTAS_PL[1]) + \
                            (dots['l2'] * GOTAS_PL[2]) + \
                            (dots['l3'] * GOTAS_PL[3])
            
            volume_cor_ml = volume_cor_pl * 1e-9
            densidade_cor = DENSIDADES_TINTA_G_ML.get(cor_en, 1.0)
            
            massa_cor_g = (volume_cor_ml * densidade_cor) * (1 + fator_porcentagem)
            
            cor_pt = COR_MAP_PT_BR.get(cor_en, cor_en)
            
            consumo_por_cor_lista.append({
                "cor": cor_pt,
                "massa_g": round(massa_cor_g, 5)
            })
            
    consumo_total_g = sum([item['massa_g'] for item in consumo_por_cor_lista])

    return jsonify({
        "consumo_por_cor_lista": consumo_por_cor_lista,
        "consumo_total_g": round(consumo_total_g, 5)
    }), 200

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    arquivo = request.files['file']
    porcentagem_str = request.form.get('porcentagem')

    if arquivo.filename == '':
        return jsonify({"error": "Nome do arquivo inválido"}), 400

    try:
        porcentagem = float(porcentagem_str)
        fator_porcentagem = porcentagem / 100.0
    except (ValueError, TypeError):
        return jsonify({"error": "Porcentagem inválida"}), 400

    conteudo_arquivo = arquivo.stream.read().decode("utf-8")
    
    consumo_por_cor_lista = []
    
    canais = re.findall(r'\[Channel_(\d+)\].*?Color=(\w+).*?Dots_Level_1=(\d+).*?Dots_Level_2=(\d+).*?Dots_Level_3=(\d+)', conteudo_arquivo, re.DOTALL)
    
    for _, cor_en, dots_l1, dots_l2, dots_l3 in canais:
        densidade_cor = DENSIDADES_TINTA_G_ML.get(cor_en, 1.0)
        
        dots_l1 = int(dots_l1)
        dots_l2 = int(dots_l2)
        dots_l3 = int(dots_l3)
        
        volume_cor_pl = (dots_l1 * GOTAS_PL[1]) + \
                        (dots_l2 * GOTAS_PL[2]) + \
                        (dots_l3 * GOTAS_PL[3])
        
        if volume_cor_pl > 0:
            volume_cor_ml = volume_cor_pl * 1e-9
            
            massa_cor_g = (volume_cor_ml * densidade_cor) * (1 + fator_porcentagem)
            
            cor_pt = COR_MAP_PT_BR.get(cor_en, cor_en)
            
            consumo_por_cor_lista.append({
                "cor": cor_pt,
                "massa_g": round(massa_cor_g, 5)
            })
            
    consumo_total_g = sum([item['massa_g'] for item in consumo_por_cor_lista])

    return jsonify({
        "consumo_por_cor_lista": consumo_por_cor_lista,
        "consumo_total_g": round(consumo_total_g, 5)
    }), 200