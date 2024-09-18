document.addEventListener('DOMContentLoaded', () => {
    const pseudocodeInput = document.getElementById('pseudocode');
    const interpretButton = document.getElementById('interpret');
    const loadExampleButton = document.getElementById('load-example');
    const outputDiv = document.getElementById('output');

    interpretButton.addEventListener('click', async () => {
        const pseudocode = pseudocodeInput.value;
        
        try {
            const response = await fetch('/interpret', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ pseudocode }),
            });

            const data = await response.json();

            if (data.error) {
                outputDiv.innerHTML = `<span class="error">Error: ${data.error}</span>`;
            } else {
                outputDiv.textContent = data.result;
            }
        } catch (error) {
            outputDiv.innerHTML = `<span class="error">An error occurred: ${error.message}</span>`;
        }
    });

    loadExampleButton.addEventListener('click', async () => {
        try {
            const response = await fetch('/example');
            const data = await response.json();
            pseudocodeInput.value = data.example;
        } catch (error) {
            outputDiv.innerHTML = `<span class="error">Failed to load example: ${error.message}</span>`;
        }
    });
});
