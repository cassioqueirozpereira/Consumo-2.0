// /static/script.js

document.addEventListener('DOMContentLoaded', () => {
    const arquivoInput = document.getElementById('arquivoInput');
    const calcularBtn = document.getElementById('calcularBtn');
    const loadingDiv = document.getElementById('loading');
    const resultadoContainer = document.getElementById('resultadoContainer');
    const resultadosPorCorDiv = document.getElementById('resultadosPorCor');
    const consumoTotalSpan = document.getElementById('consumoTotal');

    calcularBtn.addEventListener('click', async () => {
        const arquivos = arquivoInput.files;
        if (arquivos.length === 0) {
            alert("Por favor, selecione pelo menos um arquivo.");
            return;
        }

        const formData = new FormData();
        for (const arquivo of arquivos) {
            formData.append('files[]', arquivo);
        }

        loadingDiv.classList.remove('hidden');
        resultadoContainer.classList.add('hidden');

        try {
            const response = await fetch('/upload-multi', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Erro no servidor');
            }

            const data = await response.json();
            
            resultadosPorCorDiv.innerHTML = '';
            
            data.consumo_por_cor_lista.forEach(item => {
                const p = document.createElement('p');
                const consumoFormatado = item.consumo.toFixed(3);
                p.textContent = `${item.cor}: ${consumoFormatado} g/m²`;
                resultadosPorCorDiv.appendChild(p);
            });
            
            consumoTotalSpan.textContent = data.consumo_total_gm2.toFixed(3);
            
            resultadoContainer.classList.remove('hidden');

        } catch (error) {
            alert("Ocorreu um erro: " + error.message);
        } finally {
            loadingDiv.classList.add('hidden');
        }
    });
});