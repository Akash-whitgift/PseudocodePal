document.addEventListener('DOMContentLoaded', () => {
    const pseudocodeInput = document.getElementById('pseudocode');
    const interpretButton = document.getElementById('interpret');
    const loadExampleButton = document.getElementById('load-example');
    const outputDiv = document.getElementById('output');

    // Add a visible message to confirm JavaScript is loading
    outputDiv.textContent = "JavaScript loaded successfully!";

    // Initialize CodeMirror
    const editor = CodeMirror.fromTextArea(pseudocodeInput, {
        mode: "text/x-pseudocode",
        theme: "monokai",  // Changed theme for better visibility
        lineNumbers: true,
        indentUnit: 4,
        tabSize: 4,
        autofocus: true,
        lineWrapping: true
    });

    interpretButton.addEventListener('click', async () => {
        const pseudocode = editor.getValue();
        
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
            editor.setValue(data.example);
        } catch (error) {
            outputDiv.innerHTML = `<span class="error">Failed to load example: ${error.message}</span>`;
        }
    });
});
