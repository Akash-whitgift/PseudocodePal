// Define a new mode for pseudocode
CodeMirror.defineMode("pseudocode", function() {
  return {
    startState: function() {
      return {inString: false, inComment: false};
    },
    token: function(stream, state) {
      // Handle comments
      if (state.inComment) {
        if (stream.skipTo("#")) {
          stream.next();
          state.inComment = false;
        } else {
          stream.skipToEnd();
        }
        return "comment";
      }
      if (stream.match("#")) {
        state.inComment = true;
        return "comment";
      }

      // Handle strings
      if (state.inString) {
        if (stream.skipTo('"')) {
          stream.next();
          state.inString = false;
        } else {
          stream.skipToEnd();
        }
        return "string";
      }
      if (stream.match('"')) {
        state.inString = true;
        return "string";
      }

      // Keywords
      if (stream.match(/\b(IF|THEN|ELSE|ENDIF|FOR|TO|DO|ENDFOR|WHILE|ENDWHILE|FUNCTION|ENDFUNCTION|RETURN|PRINT|ARRAY|CALL)\b/i)) {
        return "keyword";
      }

      // Operators
      if (stream.match(/[+\-*\/=<>!]=?|[()]|\[|\]/)) {
        return "operator";
      }

      // Numbers
      if (stream.match(/\d+/)) {
        return "number";
      }

      // Variables
      if (stream.match(/[a-z_]\w*/i)) {
        return "variable";
      }

      // Consume any other characters
      stream.next();
      return null;
    }
  };
});

// Set pseudocode as the default mode for CodeMirror
CodeMirror.defineMIME("text/x-pseudocode", "pseudocode");
