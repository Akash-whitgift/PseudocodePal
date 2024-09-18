document.addEventListener('DOMContentLoaded', () => {
    const pseudocodeEditor = document.getElementById('pseudocode');
    const interpretButton = document.getElementById('interpret');
    const loadExampleButton = document.getElementById('load-example');
    const startExecutionButton = document.getElementById('start-execution');
    const nextStepButton = document.getElementById('next-step');
    const saveSnippetButton = document.getElementById('save-snippet');
    const loadSnippetButton = document.getElementById('load-snippet');
    const outputDiv = document.getElementById('output');
    const variableStateDiv = document.getElementById('variable-state');

    function updateSyntaxHighlighting() {
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

    saveSnippetButton.addEventListener('click', async () => {
        const snippetName = prompt('Enter a name for this snippet:');
        if (snippetName) {
            const pseudocode = pseudocodeEditor.textContent;
            try {
                const response = await fetch('/save_snippet', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ name: snippetName, code: pseudocode }),
                });

                const data = await response.json();
                if (data.error) {
                    outputDiv.innerHTML = `<span class="error">Error: ${data.error}</span>`;
                } else {
                    outputDiv.textContent = 'Snippet saved successfully';
                }
            } catch (error) {
                outputDiv.innerHTML = `<span class="error">Failed to save snippet: ${error.message}</span>`;
            }
        }
    });

    loadSnippetButton.addEventListener('click', async () => {
        try {
            const response = await fetch('/list_snippets');
            const data = await response.json();
            const snippets = data.snippets;

            if (snippets.length === 0) {
                outputDiv.textContent = 'No snippets available';
                return;
            }

            const snippetName = prompt('Enter the name of the snippet to load:\n\nAvailable snippets:\n' + snippets.join('\n'));
            if (snippetName) {
                const loadResponse = await fetch(`/load_snippet/${snippetName}`);
                const snippetData = await loadResponse.json();

                if (snippetData.error) {
                    outputDiv.innerHTML = `<span class="error">Error: ${snippetData.error}</span>`;
                } else {
                    pseudocodeEditor.textContent = snippetData.code;
                    updateSyntaxHighlighting();
                    outputDiv.textContent = 'Snippet loaded successfully';
                }
            }
        } catch (error) {
            outputDiv.innerHTML = `<span class="error">Failed to load snippet: ${error.message}</span>`;
        }
    });

    const testConsistencyButton = document.createElement('button');
    testConsistencyButton.textContent = 'Test Consistency';
    document.querySelector('.button-container').appendChild(testConsistencyButton);

    testConsistencyButton.addEventListener('click', async () => {
        const pseudocode = pseudocodeEditor.textContent;
        
        try {
            const response = await fetch('/test_consistency', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ pseudocode }),
            });

            const data = await response.json();
            outputDiv.innerHTML = `
                <h3>Full Interpretation Result:</h3>
                <pre>${data.full_result}</pre>
                <h3>Step-by-Step Execution Result:</h3>
                <pre>${data.step_result}</pre>
            `;

            if (data.full_result === data.step_result) {
                outputDiv.innerHTML += '<p style="color: green;">Results are consistent!</p>';
            } else {
                outputDiv.innerHTML += '<p style="color: red;">Inconsistency detected!</p>';
            }
        } catch (error) {
            outputDiv.innerHTML = `<span class="error">An error occurred: ${error.message}</span>`;
        }
    });
});
