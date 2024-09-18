document.addEventListener('DOMContentLoaded', () => {
    const pseudocodeEditor = document.getElementById('pseudocode');
    const interpretButton = document.getElementById('interpret');
    const loadExampleButton = document.getElementById('load-example');
    const startExecutionButton = document.getElementById('start-execution');
    const nextStepButton = document.getElementById('next-step');
    const outputDiv = document.getElementById('output');
    const variableStateDiv = document.getElementById('variable-state');

    function updateSyntaxHighlighting() {
        pseudocodeEditor.innerHTML = pseudocodeEditor.textContent;
        Prism.highlightElement(pseudocodeEditor);
    }

    updateSyntaxHighlighting();
    pseudocodeEditor.addEventListener('input', updateSyntaxHighlighting);

    interpretButton.addEventListener('click', async () => {
        const pseudocode = pseudocodeEditor.textContent;
        
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
            variableStateDiv.textContent = '';
        } catch (error) {
            outputDiv.innerHTML = `<span class="error">An error occurred: ${error.message}</span>`;
        }
    });

    loadExampleButton.addEventListener('click', async () => {
        try {
            const response = await fetch('/example');
            const data = await response.json();
            pseudocodeEditor.textContent = data.example;
            updateSyntaxHighlighting();
        } catch (error) {
            outputDiv.innerHTML = `<span class="error">Failed to load example: ${error.message}</span>`;
        }
    });

    startExecutionButton.addEventListener('click', async () => {
        const pseudocode = pseudocodeEditor.textContent;
        
        try {
            const response = await fetch('/start_execution', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ pseudocode }),
            });

            const data = await response.json();
            outputDiv.textContent = '';
            variableStateDiv.textContent = '';
            nextStepButton.disabled = false;
        } catch (error) {
            outputDiv.innerHTML = `<span class="error">An error occurred: ${error.message}</span>`;
        }
    });

    nextStepButton.addEventListener('click', async () => {
        try {
            const response = await fetch('/next_step');
            const data = await response.json();

            if (data.message === 'Execution completed') {
                outputDiv.textContent += '\nExecution completed';
                nextStepButton.disabled = true;
            } else {
                outputDiv.textContent += `\nExecuting: ${data.line}`;
                if (data.output !== null) {
                    outputDiv.textContent += `\nOutput: ${data.output}`;
                }
                updateVariableState(data.variables);
            }
        } catch (error) {
            outputDiv.innerHTML += `\n<span class="error">An error occurred: ${error.message}</span>`;
        }
    });

    function updateVariableState(variables) {
        variableStateDiv.innerHTML = '<h3>Variable State:</h3>';
        for (const [key, value] of Object.entries(variables)) {
            variableStateDiv.innerHTML += `<p>${key}: ${JSON.stringify(value)}</p>`;
        }
    }
});
