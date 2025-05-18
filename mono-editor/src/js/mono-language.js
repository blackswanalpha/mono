// Mono language definition for Monaco Editor

// Initialize Mono language when Monaco is ready
function initMonoLanguage() {
  console.log('Attempting to initialize Mono language...');

  // Check if Monaco is available
  if (typeof monaco === 'undefined' || !monaco.languages) {
    console.log('Monaco Editor is not loaded yet or languages API not available');

    // Set up a one-time event listener for monaco-ready
    const onMonacoReady = () => {
      console.log('Monaco ready event received, initializing Mono language');
      window.removeEventListener('monaco-ready', onMonacoReady);
      // Wait a short time to ensure Monaco is fully initialized
      setTimeout(initMonoLanguage, 100);
    };

    window.addEventListener('monaco-ready', onMonacoReady);

    // Also register with the Monaco loader if available
    if (window.monacoLoader) {
      console.log('Registering with Monaco loader');
      window.monacoLoader.onLoad(() => {
        console.log('Monaco loader callback triggered');
        // Wait a short time to ensure Monaco is fully initialized
        setTimeout(initMonoLanguage, 100);
      });
    }

    return;
  }

  // Double-check that monaco.languages is available
  if (!monaco.languages) {
    console.error('Monaco languages API is not available');
    return;
  }

  console.log('Initializing Mono language for Monaco Editor');

  try {
    // Check if already initialized
    if (window.monoLanguageInitialized) {
      console.log('Mono language already initialized, skipping');
      return;
    }

    // Register the Mono language
    monaco.languages.register({ id: 'mono' });

// Define the Mono language tokens and rules
monaco.languages.setMonarchTokensProvider('mono', {
  // Set defaultToken to invalid to see what you do not tokenize yet
  defaultToken: 'invalid',

  keywords: [
    'component', 'function', 'var', 'state', 'props', 'return',
    'if', 'else', 'for', 'while', 'new', 'this', 'import', 'export',
    'true', 'false', 'null', 'undefined', 'print', 'emit', 'on',
    'registerService', 'getService', 'provideContext', 'consumeContext'
  ],

  typeKeywords: [
    'int', 'float', 'string', 'bool', 'void', 'any'
  ],

  operators: [
    '=', '>', '<', '!', '~', '?', ':', '==', '<=', '>=', '!=',
    '&&', '||', '++', '--', '+', '-', '*', '/', '&', '|', '^', '%',
    '<<', '>>', '>>>', '+=', '-=', '*=', '/=', '&=', '|=', '^=',
    '%=', '<<=', '>>=', '>>>='
  ],

  // we include these common regular expressions
  symbols: /[=><!~?:&|+\-*\/\^%]+/,

  // C# style strings
  escapes: /\\(?:[abfnrtv\\"']|x[0-9A-Fa-f]{1,4}|u[0-9A-Fa-f]{4}|U[0-9A-Fa-f]{8})/,

  // The main tokenizer for our languages
  tokenizer: {
    root: [
      // identifiers and keywords
      [/[a-z_$][\w$]*/, {
        cases: {
          '@typeKeywords': 'keyword.type',
          '@keywords': 'keyword',
          '@default': 'identifier'
        }
      }],
      [/[A-Z][\w\$]*/, 'type.identifier'],  // to show class names nicely

      // whitespace
      { include: '@whitespace' },

      // delimiters and operators
      [/[{}()\[\]]/, '@brackets'],
      [/[<>](?!@symbols)/, '@brackets'],
      [/@symbols/, {
        cases: {
          '@operators': 'operator',
          '@default': ''
        }
      }],

      // @ annotations.
      [/@\s*[a-zA-Z_\$][\w\$]*/, 'annotation'],

      // numbers
      [/\d*\.\d+([eE][\-+]?\d+)?/, 'number.float'],
      [/0[xX][0-9a-fA-F]+/, 'number.hex'],
      [/\d+/, 'number'],

      // delimiter: after number because of .\d floats
      [/[;,.]/, 'delimiter'],

      // strings
      [/"([^"\\]|\\.)*$/, 'string.invalid'],  // non-terminated string
      [/'([^'\\]|\\.)*$/, 'string.invalid'],  // non-terminated string
      [/"/, 'string', '@string_double'],
      [/'/, 'string', '@string_single'],
    ],

    whitespace: [
      [/[ \t\r\n]+/, 'white'],
      [/\/\/.*$/, 'comment'],
      [/\/\*/, 'comment', '@comment'],
    ],

    comment: [
      [/[^\/*]+/, 'comment'],
      [/\/\*/, 'comment', '@push'],    // nested comment
      ["\\*/", 'comment', '@pop'],
      [/[\/*]/, 'comment']
    ],

    string_double: [
      [/[^\\"]+/, 'string'],
      [/@escapes/, 'string.escape'],
      [/\\./, 'string.escape.invalid'],
      [/"/, 'string', '@pop']
    ],

    string_single: [
      [/[^\\']+/, 'string'],
      [/@escapes/, 'string.escape'],
      [/\\./, 'string.escape.invalid'],
      [/'/, 'string', '@pop']
    ],
  },
});

// Define the Mono language configuration
monaco.languages.setLanguageConfiguration('mono', {
  comments: {
    lineComment: '//',
    blockComment: ['/*', '*/']
  },
  brackets: [
    ['{', '}'],
    ['[', ']'],
    ['(', ')']
  ],
  autoClosingPairs: [
    { open: '{', close: '}' },
    { open: '[', close: ']' },
    { open: '(', close: ')' },
    { open: '"', close: '"' },
    { open: "'", close: "'" }
  ],
  surroundingPairs: [
    { open: '{', close: '}' },
    { open: '[', close: ']' },
    { open: '(', close: ')' },
    { open: '"', close: '"' },
    { open: "'", close: "'" }
  ],
  folding: {
    markers: {
      start: new RegExp('^\\s*//\\s*#?region\\b'),
      end: new RegExp('^\\s*//\\s*#?endregion\\b')
    }
  },
  wordPattern: /(-?\d*\.\d\w*)|([^\`\~\!\@\#\%\^\&\*\(\)\-\=\+\[\{\]\}\\\|\;\:\'\"\,\.\<\>\/\?\s]+)/g
});

// Define the Mono language completion provider
monaco.languages.registerCompletionItemProvider('mono', {
  provideCompletionItems: function(model, position) {
    const word = model.getWordUntilPosition(position);
    const range = {
      startLineNumber: position.lineNumber,
      endLineNumber: position.lineNumber,
      startColumn: word.startColumn,
      endColumn: word.endColumn
    };

    // Define completion items
    const suggestions = [
      // Keywords
      ...['component', 'function', 'var', 'state', 'props', 'return',
        'if', 'else', 'for', 'while', 'new', 'this', 'import', 'export',
        'true', 'false', 'null', 'undefined', 'print', 'emit', 'on',
        'registerService', 'getService', 'provideContext', 'consumeContext'
      ].map(keyword => ({
        label: keyword,
        kind: monaco.languages.CompletionItemKind.Keyword,
        insertText: keyword,
        range: range
      })),

      // Types
      ...['int', 'float', 'string', 'bool', 'void', 'any'].map(type => ({
        label: type,
        kind: monaco.languages.CompletionItemKind.TypeParameter,
        insertText: type,
        range: range
      })),

      // Snippets
      {
        label: 'component',
        kind: monaco.languages.CompletionItemKind.Snippet,
        insertText: [
          'component ${1:ComponentName} {',
          '\tstate {',
          '\t\t${2:property}: ${3:type} = ${4:value};',
          '\t}',
          '',
          '\tfunction ${5:methodName}() {',
          '\t\t${0}',
          '\t}',
          '}'
        ].join('\n'),
        insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
        documentation: 'Component definition',
        range: range
      },
      {
        label: 'function',
        kind: monaco.languages.CompletionItemKind.Snippet,
        insertText: [
          'function ${1:name}(${2:params}) {',
          '\t${0}',
          '}'
        ].join('\n'),
        insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
        documentation: 'Function definition',
        range: range
      },
      {
        label: 'if',
        kind: monaco.languages.CompletionItemKind.Snippet,
        insertText: [
          'if (${1:condition}) {',
          '\t${0}',
          '}'
        ].join('\n'),
        insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
        documentation: 'If statement',
        range: range
      },
      {
        label: 'ifelse',
        kind: monaco.languages.CompletionItemKind.Snippet,
        insertText: [
          'if (${1:condition}) {',
          '\t${2}',
          '} else {',
          '\t${0}',
          '}'
        ].join('\n'),
        insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
        documentation: 'If-else statement',
        range: range
      },
      {
        label: 'for',
        kind: monaco.languages.CompletionItemKind.Snippet,
        insertText: [
          'for (var ${1:i} = 0; ${1:i} < ${2:count}; ${1:i}++) {',
          '\t${0}',
          '}'
        ].join('\n'),
        insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
        documentation: 'For loop',
        range: range
      },
      {
        label: 'while',
        kind: monaco.languages.CompletionItemKind.Snippet,
        insertText: [
          'while (${1:condition}) {',
          '\t${0}',
          '}'
        ].join('\n'),
        insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
        documentation: 'While loop',
        range: range
      }
    ];

    return { suggestions: suggestions };
  }
});

// Define the Mono language hover provider
monaco.languages.registerHoverProvider('mono', {
  provideHover: function(model, position) {
    const word = model.getWordAtPosition(position);
    if (!word) return null;

    const keywords = {
      'component': 'Defines a reusable UI component with its own state and behavior.',
      'function': 'Defines a function that can be called to perform actions.',
      'var': 'Declares a variable with local scope.',
      'state': 'Defines internal mutable data for a component.',
      'props': 'Defines immutable input data passed from parent components.',
      'return': 'Returns a value from a function.',
      'if': 'Conditional statement that executes code if the condition is true.',
      'else': 'Executes code if the condition in the if statement is false.',
      'for': 'Loop that iterates over a range of values.',
      'while': 'Loop that executes as long as a condition is true.',
      'new': 'Creates a new instance of a component or object.',
      'this': 'Refers to the current component instance.',
      'import': 'Imports components or functions from other files.',
      'export': 'Makes components or functions available to other files.',
      'print': 'Outputs text to the console.',
      'emit': 'Emits an event that can be handled by parent components.',
      'on': 'Registers an event handler for a specific event.'
    };

    const types = {
      'int': 'Integer numeric type',
      'float': 'Floating-point numeric type',
      'string': 'Text string type',
      'bool': 'Boolean type (true or false)',
      'void': 'Represents no value (used for functions that don\'t return a value)',
      'any': 'Dynamic type that can hold any value'
    };

    let contents = '';
    if (keywords[word.word]) {
      contents = keywords[word.word];
    } else if (types[word.word]) {
      contents = types[word.word];
    }

    if (contents) {
      return {
        range: new monaco.Range(
          position.lineNumber,
          word.startColumn,
          position.lineNumber,
          word.endColumn
        ),
        contents: [
          { value: `**${word.word}**` },
          { value: contents }
        ]
      };
    }

    return null;
  }
});

    // Set the initialization flag
    window.monoLanguageInitialized = true;
    console.log('Mono language initialization completed successfully');
  } catch (error) {
    console.error('Error initializing Mono language:', error);
  }
} // End of initMonoLanguage function

// Call the initialization function
document.addEventListener('DOMContentLoaded', function() {
  console.log('DOM content loaded, setting up Mono language initialization');

  // Set a timeout to ensure other scripts have loaded
  setTimeout(() => {
    console.log('Attempting initial Mono language initialization');
    initMonoLanguage();

    // Set up a global variable to track initialization status
    window.monoLanguageInitialized = false;

    // Set up a function to check if Monaco is loaded periodically
    const checkMonaco = () => {
      if (window.monoLanguageInitialized) {
        console.log('Mono language already initialized, stopping checks');
        return;
      }

      if (typeof monaco !== 'undefined' && monaco.languages) {
        console.log('Monaco detected during periodic check, initializing Mono language');
        initMonoLanguage();
      } else {
        console.log('Monaco not detected during periodic check, will try again');
        setTimeout(checkMonaco, 1000);
      }
    };

    // Start periodic checks
    setTimeout(checkMonaco, 1000);
  }, 500);

  // Also listen for the monaco-ready event in case Monaco loads after this script
  window.addEventListener('monaco-ready', () => {
    console.log('monaco-ready event received in main listener');
    if (!window.monoLanguageInitialized) {
      console.log('Initializing Mono language from monaco-ready event');
      initMonoLanguage();
    }
  });
});
