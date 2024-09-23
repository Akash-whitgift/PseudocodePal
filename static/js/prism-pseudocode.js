Prism.languages.pseudocode = {
    'comment': {
        pattern: /#.*/,
        greedy: true
    },
    'string': {
        pattern: /"(?:\\.|[^\\"])*"/,
        greedy: true
    },
    'keyword': /\b(?:IF|THEN|ELSE|ENDIF|FOR|TO|NEXT|WHILE|DO|ENDWHILE|PROCEDURE|ENDPROCEDURE|ARRAY|OUTPUT|INPUT|DECLARE|OF|AND|OR|NOT|MOD)\b/,
    'boolean': /\b(?:TRUE|FALSE)\b/,
    'number': /\b\d+(?:\.\d+)?\b/,
    'operator': /[+\-*\/=<>≤≥≠^←]/,
    'punctuation': /[(){}\[\],]/,
    'type': {
        pattern: /\b(?:INTEGER|REAL|CHAR|STRING|BOOLEAN)\b/,
        alias: 'function'
    }
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
