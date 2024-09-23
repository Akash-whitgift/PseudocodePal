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
      if (pseudocodeEditor.textContent.trim() === '') {
        pseudocodeEditor.innerHTML = '';
      } else {
        preserveCursor(pseudocodeEditor, () => {
          Prism.highlightElement(pseudocodeEditor);
        });
      }
    }
        
    let syntaxHighlightingTimeout;
    pseudocodeEditor.addEventListener('input', () => {
      clearTimeout(syntaxHighlightingTimeout);
      syntaxHighlightingTimeout = setTimeout(updateSyntaxHighlighting, 100);
    });

    function preserveCursor(element, callback) {
      const selection = window.getSelection();
      let range = null;
      let offset = 0;

      if (selection.rangeCount > 0) {
        range = selection.getRangeAt(0);
        const preCaretRange = range.cloneRange();
        preCaretRange.selectNodeContents(element);
        preCaretRange.setEnd(range.endContainer, range.endOffset);
        offset = preCaretRange.toString().length;
      }

      callback();

      if (offset > 0) {
        range = document.createRange();
        let currentOffset = 0;
        const walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT, null, false);
        let node;

        while ((node = walker.nextNode())) {
          if (currentOffset + node.length >= offset) {
            range.setStart(node, offset - currentOffset);
            range.setEnd(node, offset - currentOffset);
            break;
          }
          currentOffset += node.length;
        }

        selection.removeAllRanges();
        selection.addRange(range);
      }
    }
    
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
        preserveCursor(pseudocodeEditor, updateSyntaxHighlighting);
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
                  preserveCursor(pseudocodeEditor, updateSyntaxHighlighting);
                  outputDiv.textContent = 'Snippet loaded successfully';
                }
            }
        } catch (error) {
            outputDiv.innerHTML = `<span class="error">Failed to load snippet: ${error.message}</span>`;
        }
    });

    // Initial syntax highlighting
    updateSyntaxHighlighting();
});
