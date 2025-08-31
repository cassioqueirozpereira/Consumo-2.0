document.addEventListener('DOMContentLoaded', () => {
    const calcularBtn = document.getElementById('calcularBtn');
    const porcentagemInput = document.getElementById('porcentagem');
    const dropArea = document.querySelector('.border-dashed');
    const fileInput = document.getElementById('files');
    const fileListContainer = document.getElementById('fileListContainer');
    const uploadFormMulti = document.getElementById('uploadFormMulti');

    const incrementBtn = document.getElementById('incrementBtn');
    const decrementBtn = document.getElementById('decrementBtn');

    const arquivosSelecionados = new Map();

    const atualizarContagemArquivos = () => {
        const totalArquivos = arquivosSelecionados.size;
        fileListContainer.innerHTML = '';
        if (totalArquivos > 0) {
            const mensagem = `${totalArquivos} arquivo${totalArquivos > 1 ? 's' : ''}`;
            const countDiv = document.createElement('div');
            countDiv.textContent = mensagem;
            countDiv.className = 'mt-2 text-sm text-gray-500';
            fileListContainer.appendChild(countDiv);
            calcularBtn.disabled = false;
        } else {
            calcularBtn.disabled = true;
        }
    };

    const adicionarArquivos = (fileList) => {
        for (const file of fileList) {
            arquivosSelecionados.set(file.name, file);
        }
        atualizarContagemArquivos();
    };

    porcentagemInput.addEventListener('input', () => {
        const valorNumerico = parseFloat(porcentagemInput.value.replace('%', ''));
        calcularBtn.disabled = !(valorNumerico >= 0 && valorNumerico <= 100);
        if (arquivosSelecionados.size === 0) {
            calcularBtn.disabled = true;
        }
    });

    incrementBtn.addEventListener('click', () => {
        let valorNumerico = parseFloat(porcentagemInput.value.replace('%', ''));
        if (isNaN(valorNumerico)) valorNumerico = 0;
        valorNumerico = Math.min(100, valorNumerico + 5);
        porcentagemInput.value = `${valorNumerico}%`;
    });

    decrementBtn.addEventListener('click', () => {
        let valorNumerico = parseFloat(porcentagemInput.value.replace('%', ''));
        if (isNaN(valorNumerico)) valorNumerico = 0;
        valorNumerico = Math.max(0, valorNumerico - 5);
        porcentagemInput.value = `${valorNumerico}%`;
    });

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

    fileInput.addEventListener('change', (e) => {
        adicionarArquivos(e.target.files);
        fileInput.value = '';
    });

    uploadFormMulti.addEventListener('submit', async (event) => {
        event.preventDefault();

        if (arquivosSelecionados.size === 0) {
            const resultDiv = document.getElementById('result');
            resultDiv.innerHTML = '<p class="text-red-500">Por favor, selecione pelo menos um arquivo.</p>';
            return;
        }

        const formData = new FormData();

        const arquivosParaEnviar = Array.from(arquivosSelecionados.values());
        arquivosParaEnviar.forEach(file => formData.append('files[]', file));
        
        const porcentagemValue = porcentagemInput.value.replace('%', '');
        formData.append('porcentagem', porcentagemValue);

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