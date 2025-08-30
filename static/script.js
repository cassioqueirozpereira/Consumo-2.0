document.addEventListener('DOMContentLoaded', () => {
    const calcularBtn = document.getElementById('calcularBtn');
    const porcentagemInput = document.getElementById('porcentagem');
    const dropArea = document.querySelector('.border-dashed');
    const fileInput = document.getElementById('files');

    porcentagemInput.addEventListener('input', () => {
        const valor = parseFloat(porcentagemInput.value);
        if (valor >= 0 && valor <= 100) {
            calcularBtn.disabled = false;
        } else {
            calcularBtn.disabled = true;
        }
    });

    // Adiciona classes de feedback visual ao arrastar o arquivo
    dropArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropArea.classList.add('border-indigo-500', 'bg-indigo-50');
    });

    dropArea.addEventListener('dragleave', () => {
        dropArea.classList.remove('border-indigo-500', 'bg-indigo-50');
    });

    // Lida com o arquivo que foi solto
    dropArea.addEventListener('drop', (e) => {
        e.preventDefault();
        dropArea.classList.remove('border-indigo-500', 'bg-indigo-50');
        
        const files = e.dataTransfer.files;
        fileInput.files = files; // Atribui os arquivos soltos ao campo de input
        
        // Simula o evento 'change' para o campo de input para que o formulário os reconheça
        const changeEvent = new Event('change', { bubbles: true });
        fileInput.dispatchEvent(changeEvent);

        // Limpa o feedback anterior
        const parentDiv = dropArea.closest('div');
        const existingInfo = parentDiv.querySelector('.text-sm.text-gray-500');
        if (existingInfo) {
            existingInfo.remove();
        }

        // Exibe o nome dos arquivos arrastados para feedback
        if (files.length > 0) {
            const fileInfoContainer = document.createElement('div');
            fileInfoContainer.className = 'mt-2 text-sm text-gray-500';

            // Para cada arquivo, cria uma nova linha
            Array.from(files).forEach(file => {
                const fileDiv = document.createElement('div');
                fileDiv.textContent = file.name;
                fileInfoContainer.appendChild(fileDiv);
            });

            parentDiv.appendChild(fileInfoContainer);
        }
    });

    document.getElementById('uploadFormMulti').addEventListener('submit', async function(event) {
        event.preventDefault();

        const form = event.target;
        const formData = new FormData(form);

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
                    'Bege': '#C2B280', // Cor corrigida para um tom de areia mais visível
                    'Preto': '#000000',
                    'Rosa': '#FF69B4', // Cor corrigida para um tom mais forte
                    'Azul': '#0047AB',
                    'Amarelo': '#FFFF00',
                    'Brilho': '#B57EDC',
                    'Reativo': '#A9A9A9'
                };
                
                data.consumo_por_cor_lista.forEach(item => {
                    const p = document.createElement('p');
                    const massaFormatada = item.massa_g.toFixed(3);
                    const nomeExibicao = item.cor === 'Azul' ? 'Cobalto' : item.cor;
                    const corHex = coresMap[item.cor] || '#000000';
                    
                    const spanCor = document.createElement('span');
                    spanCor.style.color = corHex;
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