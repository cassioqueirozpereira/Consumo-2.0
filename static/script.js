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
            
            // Mapeamento de cores para códigos de cor em CSS
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
                
                // Mapeia o nome da cor de exibição para "Cobalto" se for "Azul"
                const nomeExibicao = item.cor === 'Azul' ? 'Cobalto' : item.cor;
                
                // Pega a cor do mapa usando o nome original do backend
                const corHex = coresMap[item.cor] || '#000000';
                p.style.color = corHex;

                p.textContent = `${nomeExibicao}: ${massaFormatada} g`;
                resultDiv.appendChild(p);
            });

            const totalDiv = document.createElement('div');
            totalDiv.innerHTML = `<h2 class="text-xl font-bold mt-4">Consumo Total: ${data.consumo_total_g} g</h2>`;
            resultDiv.appendChild(totalDiv);

        } else {
            resultDiv.innerHTML = `<p class="text-red-500">Erro: ${data.error}</p>`;
        }
    } catch (error) {
        resultDiv.innerHTML = `<p class="text-red-500">Erro na requisição: ${error.message}</p>`;
    }
});