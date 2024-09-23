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
        try {
            const selection = window.getSelection();
            const range = selection.getRangeAt(0);
            const startOffset = range.startOffset;
            const endOffset = range.endOffset;

            // Save the current scroll position
            const scrollTop = pseudocodeEditor.scrollTop;

            pseudocodeEditor.removeEventListener('input', updateSyntaxHighlighting);

            const content = pseudocodeEditor.textContent;

            // Apply syntax highlighting
            Prism.highlightElement(pseudocodeEditor);

            // Restore the original content if it was changed
            if (pseudocodeEditor.textContent !== content) {
                pseudocodeEditor.textContent = content;
            }

            // Restore the cursor position
            if (pseudocodeEditor.firstChild) {
                const newRange = document.createRange();
                newRange.setStart(pseudocodeEditor.firstChild, startOffset);
                newRange.setEnd(pseudocodeEditor.firstChild, endOffset);
                selection.removeAllRanges();
                selection.addRange(newRange);
            }

            // Restore the scroll position
            pseudocodeEditor.scrollTop = scrollTop;

            pseudocodeEditor.addEventListener('input', updateSyntaxHighlighting);
        } catch (error) {
            console.error('Error in updateSyntaxHighlighting:', error);
            pseudocodeEditor.addEventListener('input', updateSyntaxHighlighting);
        }
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
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            if (data.error) {
                throw new Error(data.error);
            }
            pseudocodeEditor.textContent = data.example;
            updateSyntaxHighlighting();
            outputDiv.textContent = 'Example loaded successfully';
        } catch (error) {
            console.error('Error loading example:', error);
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

            if (data.consistency.output_match && data.consistency.variable_match && data.consistency.error_match) {
                outputDiv.innerHTML += '<p style="color: green;">Results are consistent!</p>';
            } else {
                outputDiv.innerHTML += '<p style="color: red;">Inconsistency detected!</p>';
                if (!data.consistency.output_match) {
                    outputDiv.innerHTML += '<p>Output mismatch:</p>';
                    outputDiv.innerHTML += `<pre>${data.consistency.output_diff.join('\n')}</pre>`;
                }
                if (!data.consistency.variable_match) {
                    outputDiv.innerHTML += '<p>Variable state mismatch:</p>';
                    data.consistency.variable_diffs.forEach(diff => {
                        outputDiv.innerHTML += `<p>Step ${diff.step}:</p>`;
                        for (const [var_name, values] of Object.entries(diff.differences)) {
                            outputDiv.innerHTML += `<p>${var_name}: Full: ${JSON.stringify(values.full)}, Step: ${JSON.stringify(values.step)}</p>`;
                        }
                    });
                }
                if (!data.consistency.error_match) {
                    outputDiv.innerHTML += '<p>Error mismatch:</p>';
                    outputDiv.innerHTML += `<p>Full error: ${data.consistency.full_error || 'None'}</p>`;
                    outputDiv.innerHTML += `<p>Step error: ${data.consistency.step_error || 'None'}</p>`;
                }
            }
        } catch (error) {
            outputDiv.innerHTML = `<span class="error">An error occurred: ${error.message}</span>`;
        }
    });
});