document.addEventListener('DOMContentLoaded', () => {
    // === Seleção de Elementos ===
    const calcularBtn = document.getElementById('calcularBtn');
    const porcentagemInput = document.getElementById('porcentagem');
    const dropArea = document.querySelector('.drop-area');
    const fileInput = document.getElementById('files');
    const fileListContainer = document.getElementById('fileListContainer');
    const uploadFormMulti = document.getElementById('uploadFormMulti');
    const incrementBtn = document.getElementById('incrementBtn');
    const decrementBtn = document.getElementById('decrementBtn');
    const linha = document.getElementById('linha'); 

    // === Variáveis de Estado ===
    const arquivosSelecionados = new Map();
    let fileCounter = 0;

    // === Funções de Utilidade ===

    // Função para verificar e atualizar o estado de ativação/desativação do botão "Calcular".
    const atualizarEstadoBotao = () => {
        const porcentagem = parseFloat(porcentagemInput.value.replace('%', ''));
        const hasFiles = arquivosSelecionados.size > 0;
        const porcentagemValida = !isNaN(porcentagem) && porcentagem >= 0 && porcentagem <= 100;
        // O botão só é ativado se a porcentagem for válida, houver arquivos E UMA LINHA selecionada.
        calcularBtn.disabled = !(hasFiles && porcentagemValida && linha.value !== ''); 
    };
    
    // Atualiza o estado do botão quando a linha é selecionada.
    linha.addEventListener('change', atualizarEstadoBotao);

    // Função para atualizar a mensagem de contagem de arquivos na interface.
    const atualizarContagemArquivos = () => {
        const totalArquivos = arquivosSelecionados.size;
        fileListContainer.innerHTML = '';
        if (totalArquivos > 0) {
            const mensagem = `${totalArquivos} arquivo${totalArquivos > 1 ? 's' : ''} selecionado${totalArquivos > 1 ? 's' : ''}`;
            const countDiv = document.createElement('div');
            countDiv.textContent = mensagem;
            countDiv.className = 'mt-2 text-base text-gray-500';
            fileListContainer.appendChild(countDiv);
        }
        atualizarEstadoBotao();
    };

    // Função para adicionar arquivos a partir de uma FileList.
    const adicionarArquivos = (fileList) => {
        for (const file of fileList) {
            const uniqueKey = `${file.name}-${fileCounter++}`;
            arquivosSelecionados.set(uniqueKey, file);
        }
        atualizarContagemArquivos();
    };

    // === Event Listeners para Porcentagem e Botões ===
    porcentagemInput.addEventListener('input', atualizarEstadoBotao);

    incrementBtn.addEventListener('click', () => {
        let valorNumerico = parseFloat(porcentagemInput.value.replace('%', ''));
        if (isNaN(valorNumerico)) valorNumerico = 0;
        valorNumerico = Math.min(100, valorNumerico + 5);
        porcentagemInput.value = `${valorNumerico}%`;
        atualizarEstadoBotao();
    });

    decrementBtn.addEventListener('click', () => {
        let valorNumerico = parseFloat(porcentagemInput.value.replace('%', ''));
        if (isNaN(valorNumerico)) valorNumerico = 0;
        valorNumerico = Math.max(0, valorNumerico - 5);
        porcentagemInput.value = `${valorNumerico}%`;
        atualizarEstadoBotao();
    });

    // === Event Listeners para Drag-and-Drop ===
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

    // Listener para o input de arquivo padrão.
    fileInput.addEventListener('change', (e) => {
        adicionarArquivos(e.target.files);
        fileInput.value = '';
    });

    // === Submissão do Formulário (Envio para o Backend) ===
    uploadFormMulti.addEventListener('submit', async (event) => {
        event.preventDefault();
        
        // Validação de arquivos e linha
        if (arquivosSelecionados.size === 0 || linha.value === '') {
             const resultDiv = document.getElementById('result');
             resultDiv.innerHTML = '<p class="text-red-500">Por favor, selecione uma linha e pelo menos um arquivo.</p>';
             return;
        }

        // Prepara o FormData
        const formData = new FormData();
        const arquivosParaEnviar = Array.from(arquivosSelecionados.values());
        arquivosParaEnviar.forEach(file => formData.append('files[]', file));
        
        // Anexa Porcentagem (valor limpo)
        const porcentagemValue = porcentagemInput.value.replace('%', '');
        formData.append('porcentagem', porcentagemValue);

        // Anexa o valor ATUAL da linha selecionada.
        formData.append('linha', linha.value); 

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
                
                // Mapa de cores para estilizar os resultados
                const coresMap = {
                    'Ciano': '#00AEEF',
                    'Marrom': '#964B00',
                    'Beige': '#C2B280',
                    'Preto': '#000000',
                    'Rosa': '#FF69B4',
                    'Azul': '#0047AB',
                    'Yellow': '#FFFF00',
                    'Brilho': '#B57EDC',
                    'Reativo': '#A9A9A9'
                };
                
                // Exibe os resultados por cor
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

                // Exibe o total
                const totalDiv = document.createElement('div');
                totalDiv.innerHTML = `<h2 class="text-2xl font-bold mt-4 text-purple-700">Consumo Total: ${data.consumo_total_g.toFixed(3)} g</h2>`;
                resultDiv.appendChild(totalDiv);
            } else {
                resultDiv.innerHTML = `<p class="text-red-500">Erro: ${data.error}</p>`;
            }
        } catch (error) {
            resultDiv.innerHTML = `<p class="text-red-500">Erro na requisição: ${error.message}</p>`;
        }
    });
});