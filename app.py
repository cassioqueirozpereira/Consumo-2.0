# Importa as classes e funções necessárias do framework Flask.
# Flask: A classe principal da aplicação web.
# request: Objeto que lida com dados de requisições HTTP (como arquivos e formulários).
# jsonify: Função que converte dicionários Python para respostas JSON.
# render_template: Função para renderizar arquivos HTML (neste caso, 'index.html').
import re
from flask import Flask, jsonify, request, render_template

# Inicializa a aplicação Flask. O __name__ é o nome do módulo atual.
app = Flask(__name__)

# --- Dados e Mapeamentos Constantes ---
# Estas variáveis globais armazenam dados fixos que a aplicação usa para os cálculos.

# Dicionário que mapeia o nome da cor em inglês para sua densidade em g/mL.
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

# Dicionário que traduz o nome da cor do inglês para o português.
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

# Dicionário para mapear nomes de cores com erros de digitação para os nomes corretos.
# A chave é o nome com erro (em maiúsculas), o valor é o nome correto e padronizado.
COR_MAP_ERROS = {
    "AMARELHO": "Yellow",
    "COBALT": "Blue",
    "ESMERIL": "Reactive"
}

# Dicionário que armazena o volume de tinta (em picolitros) para cada nível de "dots".
GOTAS_PL = {
    1: 12,
    2: 24,
    3: 36
}

# --- Rotas da Aplicação ---

# Define a rota principal ('/') da aplicação.
# Quando um usuário acessa a URL raiz, esta função é executada.
@app.route('/')
def home():
    # Retorna o arquivo 'index.html', que contém a interface do usuário.
    return render_template('index.html')

# Define a rota para o upload de múltiplos arquivos, que aceita requisições POST.
@app.route('/upload-multi', methods=['POST'])
def upload_files():
    # --- Validação Inicial ---

    # Verifica se a requisição contém a chave 'files[]' e se a lista de arquivos não está vazia.
    if 'files[]' not in request.files or not request.files.getlist('files[]'):
        # Retorna um erro JSON se nenhum arquivo for enviado.
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    # Obtém a lista de arquivos enviados e a porcentagem extra.
    arquivos = request.files.getlist('files[]')
    porcentagem_str = request.form.get('porcentagem')

    # --- Validação e Conversão da Porcentagem ---
    
    # Tenta converter a string da porcentagem para um número de ponto flutuante.
    try:
        porcentagem = float(porcentagem_str)
        # Calcula o fator de porcentagem para aplicar nos cálculos.
        fator_porcentagem = porcentagem / 100.0
    # Captura os erros se a conversão falhar (porcentagem não é um número).
    except (ValueError, TypeError):
        # Retorna um erro JSON se a porcentagem for inválida.
        return jsonify({"error": "Porcentagem inválida"}), 400

    # --- Processamento dos Arquivos ---

    # Dicionário para armazenar o valor máximo de dots por nível de cada cor em todos os arquivos.
    max_dots = {}
    # Lista para manter a ordem original das cores encontradas.
    cores_na_ordem = []

    # Loop principal que itera sobre cada arquivo na lista de uploads.
    for arquivo in arquivos:
        # Tenta ler o conteúdo do arquivo.
        try:
            # Lê o conteúdo do arquivo como bytes e decodifica para string usando UTF-8.
            conteudo_arquivo = arquivo.stream.read().decode("utf-8")
        # Captura o erro se o arquivo não puder ser decodificado.
        except UnicodeDecodeError:
            # Retorna um erro JSON informando que o arquivo é inválido.
            return jsonify({"error": f"Erro ao ler o arquivo {arquivo.filename}. Verifique se é um arquivo de texto válido."}), 400
        
        # Dicionário para somar os dots por cor em um único arquivo.
        sum_dots = {}
        
        # Expressão regular para o primeiro formato de arquivo (RIP 1).
        # Procura por "Color=", seguido do nome da cor e os três níveis de dots.
        canais_rip1 = re.findall(r'Color=(\w+).*?Dots_Level_1=(\d+).*?Dots_Level_2=(\d+).*?Dots_Level_3=(\d+)', conteudo_arquivo, re.DOTALL)

        # Expressão regular para o segundo formato de arquivo (RIP 2).
        # Procura por "tif_", seguido do nome da cor e os três números de dots.
        canais_rip2 = re.findall(r'tif_(\w+)=(\d+),(\d+),(\d+)', conteudo_arquivo)

        # --- Lógica para Selecionar o Formato Correto ---

        # Verifica se o primeiro formato foi encontrado (a lista não está vazia).
        if canais_rip1:
                # Se sim, usa os dados do primeiro formato.
                dados_arquivo = canais_rip1
        # Caso contrário, verifica se o segundo formato foi encontrado.
        elif canais_rip2:
                # Se sim, usa os dados do segundo formato.
                dados_arquivo = canais_rip2
        # Se nenhum dos formatos for encontrado.
        else:
               # Retorna um erro JSON informando que o formato do arquivo é desconhecido.
               return jsonify({"error": f"Formato de arquivo desconhecido para {arquivo.filename}"}), 400

        # --- Soma dos Dots por Arquivo ---
        
        # Loop para iterar sobre cada tupla de dados capturada pela expressão regular.
        # Desempacota a tupla em variáveis legíveis: cor_en, dots_l1, etc.
        for  cor_en, dots_l1, dots_l2, dots_l3 in dados_arquivo:
            # Tenta encontrar o nome no dicionário de erros, caso contrário, usa capitalize().
            # O capitalize(), transforma a String, deixando a primeira letra maiúscula e o restante minúscula.
            cor_en = COR_MAP_ERROS.get(cor_en, cor_en.capitalize())

            # Adiciona a cor à lista de cores na ordem.
            cores_na_ordem.append(cor_en)
            # Converte os valores de dots de string para inteiros.
            dots_l1 = int(dots_l1)
            dots_l2 = int(dots_l2)
            dots_l3 = int(dots_l3)
            
            # Se a cor ainda não estiver no dicionário de soma, a adiciona com valores iniciais de zero.
            if cor_en not in sum_dots:
                sum_dots[cor_en] = {'l1': 0, 'l2': 0, 'l3': 0}
            
            # Soma os dots do canal atual aos totais já somados para essa cor.
            sum_dots[cor_en]['l1'] += dots_l1
            sum_dots[cor_en]['l2'] += dots_l2
            sum_dots[cor_en]['l3'] += dots_l3

        # --- Encontra o Máximo de Dots entre Todos os Arquivos ---

        # Loop que itera sobre o dicionário de somas do arquivo atual.
        for cor_en, dots in sum_dots.items():
            # Se a cor ainda não estiver no dicionário de máximo, a adiciona com valores iniciais de zero.
            if cor_en not in max_dots:
                max_dots[cor_en] = {'l1': 0, 'l2': 0, 'l3': 0}
            
            # Compara os dots somados do arquivo atual com os valores máximos globais e os atualiza se forem maiores.
            if dots['l1'] > max_dots[cor_en]['l1']:
                max_dots[cor_en]['l1'] = dots['l1']
            if dots['l2'] > max_dots[cor_en]['l2']:
                max_dots[cor_en]['l2'] = dots['l2']
            if dots['l3'] > max_dots[cor_en]['l3']:
                max_dots[cor_en]['l3'] = dots['l3']

    # --- Cálculo do Consumo Final ---
    
    # Lista para armazenar o consumo final por cor.
    consumo_por_cor_lista = []
    
    # Remove cores duplicadas da lista, mantendo a ordem de primeira aparição.
    cores_unicas_na_ordem = list(dict.fromkeys(cores_na_ordem))

    # Loop para calcular o consumo de tinta para cada cor única.
    for cor_en in cores_unicas_na_ordem:
        # Obtém os valores de dots máximos para a cor.
        dots = max_dots.get(cor_en)
        # Verifica se a cor realmente existe nos dados.
        if dots:
            # Calcula o volume total de tinta em picolitros (pL).
            volume_cor_pl = (dots['l1'] * GOTAS_PL[1]) + (dots['l2'] * GOTAS_PL[2]) + (dots['l3'] * GOTAS_PL[3])
            
            # Converte o volume de picolitros para mililitros (mL).
            volume_cor_ml = volume_cor_pl * 1e-9
            # Obtém a densidade da cor do dicionário, com um valor padrão de 1.0.
            densidade_cor = DENSIDADES_TINTA_G_ML.get(cor_en, 1.0)
            
            # Calcula a massa total em gramas e aplica o fator de porcentagem.
            massa_cor_g = (volume_cor_ml * densidade_cor) * (1 + fator_porcentagem)
            
            # Traduz o nome da cor para português.
            cor_pt = COR_MAP_PT_BR.get(cor_en, cor_en)
            
            # Adiciona o resultado final à lista de consumo por cor.
            consumo_por_cor_lista.append({
                "cor": cor_pt,
                "massa_g": round(massa_cor_g, 5) # Arredonda para 5 casas decimais.
            })
            
    # Soma a massa de todas as cores para obter o consumo total em gramas.
    consumo_total_g = sum([item['massa_g'] for item in consumo_por_cor_lista])

    # --- Retorno da Resposta ---
    
    # Retorna um objeto JSON com os resultados e um status HTTP 200 (sucesso).
    return jsonify({
        "consumo_por_cor_lista": consumo_por_cor_lista,
        "consumo_total_g": round(consumo_total_g, 5) # Arredonda o total para 5 casas decimais.
    }), 200