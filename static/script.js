document.addEventListener('DOMContentLoaded', () => {
    const calcularBtn = document.getElementById('calcularBtn');
    const porcentagemInput = document.getElementById('porcentagem');
    const dropArea = document.querySelector('.border-dashed');
    const fileInput = document.getElementById('files');
    const fileListContainer = document.getElementById('fileListContainer');
    
    // Use um Map para armazenar os arquivos, usando o nome do arquivo como chave
    const arquivosSelecionados = new Map();

    // Função para atualizar a contagem de arquivos e exibi-la
    const atualizarContagemArquivos = () => {
        const totalArquivos = arquivosSelecionados.size;
        fileListContainer.innerHTML = ''; // Limpa o conteúdo anterior
        if (totalArquivos > 0) {
            const mensagem = `${totalArquivos} arquivo${totalArquivos > 1 ? 's' : ''}`;
            const countDiv = document.createElement('div');
            countDiv.textContent = mensagem;
            countDiv.className = 'mt-2 text-xl text-gray-500';
            fileListContainer.appendChild(countDiv);
        }
    };

    // Função para adicionar arquivos a partir de uma lista, verificando duplicatas
    const adicionarArquivos = (fileList) => {
        for (const file of fileList) {
            // Adiciona o arquivo ao Map, usando seu nome como a chave.
            // Se o nome já existir, ele será substituído.
            arquivosSelecionados.set(file.name, file);
        }
        atualizarContagemArquivos();
    };

    porcentagemInput.addEventListener('input', () => {
        calcularBtn.disabled = !(parseFloat(porcentagemInput.value) >= 0 && parseFloat(porcentagemInput.value) <= 100);
    });

    // Eventos de Drag and Drop
    dropArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropArea.classList.add('border-indigo-500', 'bg-indigo-50');
    });

    dropArea.addEventListener('dragleave', () => {
        dropArea.classList.remove('border-indigo-500', 'bg-indigo-50');
    });

    dropArea.addEventListener('drop', (e) => {
        e.preventDefault();
        dropArea.classList.remove('border-indigo-500', 'bg-indigo-50');
        adicionarArquivos(e.dataTransfer.files);
    });

    // Evento de seleção por clique
    fileInput.addEventListener('change', (e) => {
        adicionarArquivos(e.target.files);
        fileInput.value = '';
    });

    document.getElementById('uploadFormMulti').addEventListener('submit', async (event) => {
        event.preventDefault();
        const formData = new FormData();

        // Converte os valores do Map para um array para enviar
        const arquivosParaEnviar = Array.from(arquivosSelecionados.values());
        arquivosParaEnviar.forEach(file => formData.append('files[]', file));
        
        formData.append('porcentagem', porcentagemInput.value);

        const resultDiv = document.getElementById('result');
        resultDiv.innerHTML = '<p class="text-gray-500">Calculando...</p>';

        try {
            const response = await fetch('/upload-multi', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();

            if (response.ok) {
                resultDiv.innerHTML = '';
                const coresMap = {
                    'Ciano': '#00AEEF',
                    'Marrom': '#964B00',
                    'Bege': '#C2B280',
                    'Preto': '#000000',
                    'Rosa': '#FF69B4',
                    'Azul': '#0047AB',
                    'Amarelo': '#FFFF00',
                    'Brilho': '#B57EDC',
                    'Reativo': '#A9A9A9'
                };
                
                data.consumo_por_cor_lista.forEach(item => {
                    const p = document.createElement('p');
                    const massaFormatada = item.massa_g.toFixed(3);
                    const nomeExibicao = item.cor === 'Azul' ? 'Cobalto' : item.cor;
                    const spanCor = document.createElement('span');
                    spanCor.style.color = coresMap[item.cor] || '#000000';
                    spanCor.textContent = nomeExibicao;
                    p.appendChild(spanCor);
                    p.append(`: ${massaFormatada} g`);
                    resultDiv.appendChild(p);
                });

                const totalDiv = document.createElement('div');
                totalDiv.innerHTML = `<h2 class="text-3xl font-bold mt-4 text-purple-700">Consumo Total: ${data.consumo_total_g.toFixed(3)} g</h2>`;
                resultDiv.appendChild(totalDiv);
            } else {
                resultDiv.innerHTML = `<p class="text-red-500">Erro: ${data.error}</p>`;
            }
        } catch (error) {
            resultDiv.innerHTML = `<p class="text-red-500">Erro na requisição: ${error.message}</p>`;
        }
    });
});