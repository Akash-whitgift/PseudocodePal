Prism.languages.pseudocode = {
    'comment': {
        pattern: /#.*/,
        greedy: true
    },
    'string': {
        pattern: /"(?:\\.|[^\\"])*"/,
        greedy: true
    },
    'keyword': /\b(?:IF|THEN|ELSE|ENDIF|FOR|FROM|TO|DO|ENDFOR|WHILE|ENDWHILE|FUNCTION|ENDFUNCTION|ARRAY|PRINT|CALL)\b/,
    'boolean': /\b(?:TRUE|FALSE)\b/,
    'number': /\b\d+(?:\.\d+)?\b/,
    'operator': /[+\-*\/=<>]=?|[!&|^~]|\b(?:AND|OR|NOT)\b/,
    'punctuation': /[(){}\[\],]/
};

Prism.languages.pseudocode['string'].inside = {
    'interpolation': {
        pattern: /\{(?:[^{}]|\{(?:[^{}]|\{[^}]*\})*\})*\}/,
        inside: {
            'interpolation-punctuation': {
                pattern: /^\{|\}$/,
                alias: 'punctuation'
            },
            rest: Prism.languages.pseudocode
        }
    }
};
