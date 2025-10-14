from flask import Flask, jsonify, request, render_template # Importa classes e funções necessárias do framework Flask para criar a API e servir HTML.
import re # Importa o módulo 're' (Regular Expressions), essencial para buscar e extrair dados formatados nos arquivos RIP.

app = Flask(__name__) # Cria a instância principal da aplicação Flask, definindo-a como o servidor web.

# --- Dicionários de Densidades (g/mL) ---
# Dicionários de configuração: armazenam o valor da densidade da tinta para cada cor, específico por linha de produção.

TRIMS_DENSIDADES_TINTA_G_ML = { # Densidades (g/mL) para a linha de produção 'TRIMS'.
    "Cyan": 1.19, # Chave/Valor: Cor Ciano tem 1.19 g/mL.
    "Brown": 1.32,
    "Beige": 1.27,
    "Black": 1.28,
    "Pink": 1.28,
    "Blue": 1.17,
    "Yellow": 1.32,
    "Luster": 1.10,
    "Reactive": 1.10
}

LINHA1_2_DENSIDADES_TINTA_G_ML = { # Densidades para as linhas 'LINHA1_2'.
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

LINHA3_DENSIDADES_TINTA_G_ML = { # Densidades para a linha 'LINHA3'.
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

LINHA4_DENSIDADES_TINTA_G_ML = { # Densidades para a linha 'LINHA4' (note os valores diferentes).
    "Cyan": 1.17,
    "Brown": 1.29,
    "Beige": 1.0,
    "Black": 1.25,
    "Pink": 1.39,
    "Blue": 1.10,
    "Yellow": 1.51,
    "Luster": 1.25,
    "Reactive": 1.26
}

IAC_DENSIDADES_TINTA_G_ML = { # Densidades para a linha 'IAC' (note os valores diferentes).
    "Blue": 1.22,
    "Brown": 1.32,
    "Beige": 1.27,
    "Cyan": 1.25,
    "Pink": 1.30,
    "Black": 1.28,
    "Yellow": 1.33,
    "Luster": 1.0,
    "Reactive": 1.27
}

# --- Dicionários de Gotas (pL) ---
# Dicionários de configuração: armazenam o volume de cada gota (dot) em picolitros (pL).

# TRIMS, LINHA1_2, LINHA3 usam o mesmo mapeamento por NÍVEL (1, 2, 3)
GOTAS_POR_NIVEL_PADRAO = { # Dicionário padrão usado quando o volume da gota depende do NÍVEL (Drop Size).
    1: 12, # Nível 1 de dot tem 12 pL.
    2: 24, # Nível 2 de dot tem 24 pL.
    3: 36 # Nível 3 de dot tem 36 pL.
}

# LINHA4 e IAC usam mapeamento por COR
LINHA4_GOTAS_PL = { # Dicionário usado pela LINHA4, onde o volume da gota (pL) é fixo por COR.
    "Cyan": 24,
    "Brown": 13,
    "Beige": 12,
    "Black": 14,
    "Pink": 22,
    "Blue": 23,
    "Yellow": 20,
    "Luster": 19,
    "Reactive": 18
}

IAC_GOTAS_PL = { # Dicionário usado pela IAC, onde o volume da gota (pL) é fixo por COR.
    "Blue": 26,
    "Brown": 25,
    "Beige": 26,
    "Cyan": 28,
    "Pink": 24,
    "Black": 27,
    "Yellow": 29,
    "Luster": 0,
    "Reactive": 31
}

# --- Mapeamentos e Correção de Nomes ---

COR_MAP_PT_BR = { # Dicionário para traduzir os nomes das cores do Inglês para o Português na saída final.
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

COR_MAP_ERROS = { # Dicionário de correção para normalizar nomes de cores mal digitados ou alternativos nos arquivos de entrada.
    "BEGE": "Beige",
    "AMARELHO": "Yellow",
    "COBALT": "Blue",
    "YELOW": "Yellow",
    "COBALTO": "Blue",
    "BEJE": "Beige",
    "WHITE": "Luster",
    "SINKER": "Reactive",
    "MATT": "Luster",
    "ESMERIL": "Luster"
}

# --- MAPA UNIFICADO DE LINHAS (Configuração Central) ---
# Estrutura chave para a flexibilidade do código, centralizando todas as configurações por linha.
MAPA_LINHAS = {
    "TRIMS": { # Chave: Nome da Linha de Produção
        "densidades": TRIMS_DENSIDADES_TINTA_G_ML, # Valor: Dicionário de densidades
        "gotas": GOTAS_POR_NIVEL_PADRAO, # Valor: Dicionário de gotas
        "tipo_gotas": "nivel" # Valor: Regra de cálculo ("nivel" implica Volume = sum(Dots_L_i * pL_L_i))
    },
    "LINHA1_2": {
        "densidades": LINHA1_2_DENSIDADES_TINTA_G_ML,
        "gotas": GOTAS_POR_NIVEL_PADRAO,
        "tipo_gotas": "nivel"
    },
    "LINHA3": {
        "densidades": LINHA3_DENSIDADES_TINTA_G_ML,
        "gotas": GOTAS_POR_NIVEL_PADRAO,
        "tipo_gotas": "nivel"
    },
    "LINHA4": {
        "densidades": LINHA4_DENSIDADES_TINTA_G_ML,
        "gotas": LINHA4_GOTAS_PL,
        "tipo_gotas": "cor" # Regra de cálculo diferente ("cor" implica Volume = sum(Total_Dots * pL_Cor))
    },
    "IAC": {
        "densidades": IAC_DENSIDADES_TINTA_G_ML,
        "gotas": IAC_GOTAS_PL,
        "tipo_gotas": "cor"
    }
}

# --- Rotas da Aplicação ---
@app.route('/') # Decorador que mapeia a URL raiz ('/') para a função 'home'.
def home(): # Função que define a resposta para a rota raiz.
    """Rota inicial que renderiza a interface HTML."""
    return render_template('index.html') # Retorna o arquivo 'index.html', que é a interface do usuário.

@app.route('/upload-multi', methods=['POST']) # Decorador que mapeia a URL '/upload-multi', aceitando apenas requisições POST.
def upload_files(): # Função que executa a lógica de processamento e cálculo.
    """
    Processa o upload de múltiplos arquivos RIP, calcula o consumo de tinta em gramas.
    """
    
    # 1. Validação de Arquivo e Parâmetros
    if 'files[]' not in request.files or not request.files.getlist('files[]'): # Verifica se a lista de arquivos está vazia.
        return jsonify({"error": "Nenhum arquivo enviado"}), 400 # Retorna um erro JSON com status HTTP 400.

    arquivos = request.files.getlist('files[]') # Obtém a lista de objetos FileStorage dos arquivos enviados.
    porcentagem_str = request.form.get('porcentagem') # Obtém a string da porcentagem de segurança do formulário.
    linha = request.form.get('linha') # Obtém o nome da linha de produção selecionada.

    # 2. Seleção e Validação da Linha (Usando o MAPA_LINHAS)
    config_linha = MAPA_LINHAS.get(linha) # Busca a configuração completa da linha usando o nome fornecido.
    if not config_linha: # Verifica se a linha foi encontrada.
        return jsonify({"error": "Linha de produção inválida ou não mapeada."}), 400 # Retorna erro se a linha for desconhecida.
    
    densidades = config_linha["densidades"] # Atribui o dicionário de densidades da linha à variável local 'densidades'.
    gotas = config_linha["gotas"] # Atribui o dicionário de gotas da linha à variável local 'gotas'.
    tipo_gotas = config_linha["tipo_gotas"] # Atribui a regra de cálculo ("nivel" ou "cor").

    # 3. Validação e Conversão da Porcentagem
    try:
        # Limpa o input (remove '%', substitui ',' por '.')
        porcentagem_limpa = porcentagem_str.replace('%', '').replace(',', '.') # Normaliza a string para aceitar formatos como "5%" ou "5,0".
        porcentagem = float(porcentagem_limpa) # Converte a string limpa para um número de ponto flutuante.
        fator_porcentagem = porcentagem / 100.0 # Converte a porcentagem em um fator decimal (ex: 5 -> 0.05) para o cálculo final.
    except (ValueError, TypeError): # Captura exceções se a string não puder ser convertida em float.
        return jsonify({"error": "Porcentagem inválida. Use apenas números."}), 400 # Retorna erro de porcentagem inválida.

    # 4. Processamento dos Arquivos
    max_dots = {} # Dicionário que armazenará o *máximo* de dots por cor e nível entre todos os arquivos enviados.
    cores_na_ordem = [] # Lista usada para garantir que a ordem das cores na saída seja a ordem em que foram encontradas.

    for arquivo in arquivos: # Inicia o loop para processar cada arquivo.
        try:
            arquivo.stream.seek(0) # Reposiciona o ponteiro de leitura para o início do arquivo.
            conteudo_arquivo = arquivo.stream.read().decode("utf-8") # Lê e decodifica o conteúdo do arquivo como texto.
        except UnicodeDecodeError:
            return jsonify({"error": f"Erro ao ler o arquivo {arquivo.filename}. Verifique a codificação."}), 400 # Trata erro de codificação.
        
        sum_dots = {} # Dicionário temporário para acumular dots por cor *deste arquivo específico*.
        
        # Expressões regulares para diferentes formatos de arquivo RIP
        canais_rip1 = re.findall(r'Color=(\w+).*?Dots_Level_1=(\d+).*?Dots_Level_2=(\d+).*?Dots_Level_3=(\d+)', conteudo_arquivo, re.DOTALL) # Tenta extrair dados no Formato 1 (Color=... Dots_Level_X=...).
        canais_rip2 = re.findall(r'tif_(\w+)\s*=\s*(\d+),(\d+),(\d+)', conteudo_arquivo) # Tenta extrair dados no Formato 2 (tif_cor=d1,d2,d3).

        if canais_rip1: # Se o Formato 1 for encontrado.
            dados_arquivo = canais_rip1
        elif canais_rip2: # Se o Formato 2 for encontrado.
            dados_arquivo = canais_rip2
        else: # Se nenhum formato for reconhecido.
            return jsonify({"error": f"Formato de arquivo desconhecido para {arquivo.filename}"}), 400 # Retorna erro.

        # Acumula a contagem de dots por cor e nível (dentro deste arquivo)
        for cor_en, dots_l1, dots_l2, dots_l3 in dados_arquivo: # Itera sobre os resultados da Regex.
            cor_en = COR_MAP_ERROS.get(cor_en.upper(), cor_en.capitalize()) # Corrige e normaliza o nome da cor.
            cores_na_ordem.append(cor_en) # Registra a cor para manter a ordem.
            dots_l1 = int(dots_l1) # Converte o Nível 1 para inteiro.
            dots_l2 = int(dots_l2) # Converte o Nível 2 para inteiro.
            dots_l3 = int(dots_l3) # Converte o Nível 3 para inteiro.
            
            if cor_en not in sum_dots:
                sum_dots[cor_en] = {'l1': 0, 'l2': 0, 'l3': 0} # Inicializa a contagem se for a primeira vez.
            
            sum_dots[cor_en]['l1'] += dots_l1 # Acumula dots do Nível 1.
            sum_dots[cor_en]['l2'] += dots_l2 # Acumula dots do Nível 2.
            sum_dots[cor_en]['l3'] += dots_l3 # Acumula dots do Nível 3.

        # Determina o valor máximo de dots para cada cor/nível entre todos os arquivos (global)
        for cor_en, dots in sum_dots.items(): # Itera sobre os totais calculados no arquivo atual.
            if cor_en not in max_dots:
                max_dots[cor_en] = {'l1': 0, 'l2': 0, 'l3': 0} # Inicializa a cor no dicionário global de máximos.
            
            # Compara o total de dots do arquivo atual com o valor máximo já armazenado, atualizando se for maior.
            max_dots[cor_en]['l1'] = max(dots['l1'], max_dots[cor_en]['l1'])
            max_dots[cor_en]['l2'] = max(dots['l2'], max_dots[cor_en]['l2'])
            max_dots[cor_en]['l3'] = max(dots['l3'], max_dots[cor_en]['l3'])

    # 5. Cálculo do Consumo Final
    consumo_por_cor_lista = [] # Lista para armazenar o consumo final detalhado por cor.
    cores_unicas_na_ordem = list(dict.fromkeys(cores_na_ordem)) # Filtra cores repetidas, mantendo a ordem de primeira aparição.

    for cor_en in cores_unicas_na_ordem: # Itera sobre cada cor única a ser calculada.
        dots = max_dots.get(cor_en) # Obtém o dicionário de dots máximos (l1, l2, l3) para a cor.
        if dots:
            densidade_cor = densidades.get(cor_en) # Obtém a densidade da tinta da linha selecionada.
            
            if densidade_cor is None:
                continue # Pula a cor se a densidade não estiver mapeada (ignorando tintas desconhecidas).

            volume_cor_pl = 0 # Inicializa o volume total em picolitros.
            
            # Lógica de Volume de Tinta Consolidada (usa a regra definida em 'tipo_gotas')
            if tipo_gotas == "nivel": # Regra para linhas como TRIMS, LINHA1_2, LINHA3.
                # O volume total é a soma do produto (dots de um nível * pL específico daquele nível).
                volume_cor_pl = (dots['l1'] * gotas[1]) + \
                                (dots['l2'] * gotas[2]) + \
                                (dots['l3'] * gotas[3])
            
            elif tipo_gotas == "cor": # Regra para linhas como LINHA4, IAC.
                # O volume total é a soma total de dots (l1+l2+l3) multiplicada pelo pL fixo da cor.
                total_dots = dots['l1'] + dots['l2'] + dots['l3'] # Soma todos os dots.
                gotas_cor = gotas.get(cor_en, 0) # Obtém o volume da gota (pL) para a cor específica.
                volume_cor_pl = total_dots * gotas_cor # Volume total.
            
            # 6. Conversão e Cálculo Final (Gramas)
            volume_cor_ml = volume_cor_pl * 1e-9 # Converte picolitros (pL, 1e-12 L) para mililitros (mL, 1e-3 L) -> 1e-9.
            
            # Massa (g) = Volume (mL) * Densidade (g/mL) * Fator de Segurança (1 + fator_porcentagem)
            massa_cor_g = (volume_cor_ml * densidade_cor) * (1 + fator_porcentagem) # Aplica a fórmula de massa e o fator de segurança.
            
            cor_pt = COR_MAP_PT_BR.get(cor_en, cor_en) # Traduz a cor para o português.
            
            consumo_por_cor_lista.append({ # Adiciona o resultado formatado à lista final.
                "cor": cor_pt,
                "massa_g": round(massa_cor_g, 5) # Arredonda o consumo para 5 casas decimais.
            })
            
    consumo_total_g = sum([item['massa_g'] for item in consumo_por_cor_lista]) # Soma o consumo de todas as cores para obter o total geral.

    return jsonify({ # Retorna a resposta ao cliente no formato JSON.
        "consumo_por_cor_lista": consumo_por_cor_lista, # Consumo detalhado por cor.
        "consumo_total_g": round(consumo_total_g, 5) # Consumo total geral.
    }), 200 # Retorna o status HTTP 200 (OK).
