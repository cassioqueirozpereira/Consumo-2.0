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

        // Exibe o nome dos arquivos arrastados para feedback
        const fileNames = Array.from(files).map(file => file.name).join(', ');
        const fileInfoDiv = document.createElement('div');
        fileInfoDiv.className = 'mt-2 text-sm text-gray-500';
        fileInfoDiv.textContent = `Arquivos selecionados: ${fileNames}`;
        
        const parentDiv = dropArea.closest('div');
        if (parentDiv) {
            const existingInfo = parentDiv.querySelector('.text-sm.text-gray-500');
            if (existingInfo) {
                existingInfo.remove();
            }
            parentDiv.appendChild(fileInfoDiv);
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
                    'Beige': '#F5F5DC',
                    'Preto': '#000000',
                    'Rosa': '#FFC0CB',
                    'Azul': '#0047AB',
                    'Amarelo': '#FFFF00',
                    'Brilho': '#E6E6FA',
                    'Reativo': '#A9A9A9'
                };
                
                data.consumo_por_cor_lista.forEach(item => {
                    const p = document.createElement('p');
                    const massaFormatada = item.massa_g.toFixed(5);
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
                totalDiv.innerHTML = `<h2 class="text-xl font-bold mt-4">Consumo Total: ${data.consumo_total_g.toFixed(5)} g</h2>`;
                resultDiv.appendChild(totalDiv);

            } else {
                resultDiv.innerHTML = `<p class="text-red-500">Erro: ${data.error}</p>`;
            }
        } catch (error) {
            resultDiv.innerHTML = `<p class="text-red-500">Erro na requisição: ${error.message}</p>`;
        }
    });
});