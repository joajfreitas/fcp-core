/* eslint-disable @typescript-eslint/no-var-requires */
const vscode = require('vscode');
const path = require('path');
const fs = require('fs');
const cp = require('child_process');

const KEYWORDS = [
    {
        label: 'version',
        detail: 'file preamble',
        insertText: new vscode.SnippetString('version: "$1"'),
        documentation: 'Declare the FCP schema version.',
    },
    {
        label: 'struct',
        detail: 'type definition',
        insertText: new vscode.SnippetString('struct ${1:Name} {\n    ${2:field} @${3:1}: ${4:type},\n}'),
        documentation: 'Define a struct with one or more fields.',
    },
    {
        label: 'enum',
        detail: 'enumeration',
        insertText: new vscode.SnippetString('enum ${1:Name} {\n    ${2:Variant} = ${3:0},\n}'),
        documentation: 'Define an enum block.',
    },
    {
        label: 'impl',
        detail: 'implementation block',
        insertText: new vscode.SnippetString('impl ${1:StructName} {\n\n}'),
        documentation: 'Attach metadata or signals to existing types.',
    },
    {
        label: 'service',
        detail: 'service definition',
        insertText: new vscode.SnippetString('service ${1:Name} @${2:1} {\n    method ${3:Call}(${4:Input}) @${5:1} returns ${6:Output},\n}'),
        documentation: 'Declare a service with its RPC methods.',
    },
    {
        label: 'method',
        detail: 'RPC method',
        insertText: new vscode.SnippetString('method ${1:Name}(${2:Input}) @${3:1} returns ${4:Output}'),
        documentation: 'Declare an RPC method for a service.',
    },
    {
        label: 'device',
        detail: 'device definition',
        insertText: new vscode.SnippetString('device ${1:DeviceName} {\n    protocol ${2:protocol_name} {\n        impl ${3:StructName} {}\n\n        rpc {}\n        services: [],\n    }\n}'),
        documentation: 'Define a device block.',
    },
    {
        label: 'protocol',
        detail: 'protocol definition',
        insertText: new vscode.SnippetString('protocol ${1:ProtocolName} {\n    impl ${2:StructName} {}\n\n    rpc {}\n    services: [],\n}'),
        documentation: 'Define a protocol block.',
    },
    {
        label: 'mod',
        detail: 'module import',
        insertText: 'mod ',
        documentation: 'Reference another module.',
    },
    {
        label: 'Optional',
        detail: 'optional type',
        insertText: new vscode.SnippetString('Optional[${1:Type}]'),
        documentation: 'Wrap a type to make it optional.',
    },
];



const KEYWORD_COMPLETIONS = KEYWORDS.map((item, index) => {
    const completion = new vscode.CompletionItem(item.label, vscode.CompletionItemKind.Snippet);
    completion.detail = item.detail;
    completion.documentation = new vscode.MarkdownString(item.documentation);
    completion.insertText = item.insertText;
    if (item.filterText) {
        completion.filterText = item.filterText;
    }
    completion.sortText = `0${index}_${item.label}`;
    return completion;
});

function findRepoRoot(startPath) {
    let current = startPath;
    for (let i = 0; i < 8; i += 1) {
        const pyproject = path.join(current, 'pyproject.toml');
        const initFile = path.join(current, 'src', 'fcp', '__init__.py');
        if (fs.existsSync(pyproject) && fs.existsSync(initFile)) {
            return current;
        }
        const parent = path.dirname(current);
        if (parent === current) {
            break;
        }
        current = parent;
    }
    return null;
}

function collectSymbols(document) {
    const text = document.getText();
    const symbols = new Map();

    const patterns = [
        { regex: /\bstruct\s+([A-Za-z_][A-Za-z0-9_]*)/g, kind: vscode.CompletionItemKind.Struct, detail: 'struct' },
        { regex: /\benum\s+([A-Za-z_][A-Za-z0-9_]*)/g, kind: vscode.CompletionItemKind.Enum, detail: 'enum' },
        { regex: /\bservice\s+([A-Za-z_][A-Za-z0-9_]*)/g, kind: vscode.CompletionItemKind.Class, detail: 'service' },
        { regex: /\bdevice\s+([A-Za-z_][A-Za-z0-9_]*)/g, kind: vscode.CompletionItemKind.Class, detail: 'device' },
        { regex: /\bimpl\s+([A-Za-z_][A-Za-z0-9_]*)\s+for\s+([A-Za-z_][A-Za-z0-9_]*)/g, kind: vscode.CompletionItemKind.Reference, detail: 'impl alias' },
        { regex: /\bprotocol\s+([A-Za-z_][A-Za-z0-9_]*)/g, kind: vscode.CompletionItemKind.Module, detail: 'protocol' },
        { regex: /\bimpl\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?=\{)/g, kind: vscode.CompletionItemKind.Reference, detail: 'protocol impl' },
    ];

    patterns.forEach((pattern) => {
        let match = pattern.regex.exec(text);
        while (match) {
            const name = match[1];
            if (name && !symbols.has(name)) {
                const completion = new vscode.CompletionItem(name, pattern.kind);
                completion.detail = `${pattern.detail} reference`;
                completion.insertText = name;
                symbols.set(name, completion);
            }
            match = pattern.regex.exec(text);
        }
    });

    const fieldRegex = /\b([A-Za-z_][A-Za-z0-9_]*)\s*@/g;
    let fieldMatch = fieldRegex.exec(text);
    while (fieldMatch) {
        const fieldName = fieldMatch[1];
        if (fieldName && !symbols.has(fieldName)) {
            const completion = new vscode.CompletionItem(fieldName, vscode.CompletionItemKind.Field);
            completion.detail = 'field';
            completion.insertText = fieldName;
            symbols.set(fieldName, completion);
        }
        fieldMatch = fieldRegex.exec(text);
    }

    return Array.from(symbols.values());
}

function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
}

function computeRange(document, rangeLike) {
    if (!rangeLike || !rangeLike.start || !rangeLike.end) {
        const lastLine = Math.max(document.lineCount - 1, 0);
        const lineLength = Math.max(document.lineAt(lastLine).text.length, 1);
        return new vscode.Range(new vscode.Position(0, 0), new vscode.Position(lastLine, lineLength));
    }

    const startLine = clamp(rangeLike.start.line ?? 0, 0, document.lineCount ? document.lineCount - 1 : 0);
    const startChar = clamp(rangeLike.start.character ?? 0, 0, document.lineAt(Math.max(startLine, 0)).text.length);
    const endLine = clamp(rangeLike.end.line ?? startLine, startLine, document.lineCount ? document.lineCount - 1 : startLine);
    const endChar = clamp(rangeLike.end.character ?? startChar + 1, 0, document.lineAt(endLine).text.length);

    if (endLine === startLine && endChar <= startChar) {
        return new vscode.Range(new vscode.Position(startLine, startChar), new vscode.Position(endLine, startChar + 1));
    }

    return new vscode.Range(new vscode.Position(startLine, startChar), new vscode.Position(endLine, endChar));
}

function severityFrom(error) {
    const value = typeof error.severity === 'string' ? error.severity.toLowerCase() : '';
    switch (value) {
        case 'warning':
            return vscode.DiagnosticSeverity.Warning;
        case 'information':
        case 'info':
            return vscode.DiagnosticSeverity.Information;
        case 'hint':
            return vscode.DiagnosticSeverity.Hint;
        case 'error':
        default:
            return vscode.DiagnosticSeverity.Error;
    }
}

function preparePythonEnv(context) {
    const extensionRoot = context.extensionPath;
    const repoRoot = findRepoRoot(extensionRoot) || extensionRoot;
    const env = { ...process.env };
    const srcPath = path.join(repoRoot, 'src');
    env.FCP_VSCODE_REPO_ROOT = repoRoot;
    if (env.PYTHONPATH) {
        env.PYTHONPATH = `${srcPath}${path.delimiter}${env.PYTHONPATH}`;
    } else {
        env.PYTHONPATH = srcPath;
    }
    return { env, repoRoot };
}

function getPythonCandidates() {
    const config = vscode.workspace.getConfiguration('fcp');
    const configured = config.get('pythonInterpreter');
    if (typeof configured === 'string' && configured.trim().length > 0) {
        return [configured.trim()];
    }
    return process.platform === 'win32' ? ['python', 'python3'] : ['python3', 'python'];
}

function runPythonLint(context, document, outputChannel) {
    const script = path.join(context.extensionPath, 'python', 'lint.py');
    const payload = JSON.stringify({
        text: document.getText(),
        uri: document.uri.toString(),
        path: document.uri.scheme === 'file' ? document.uri.fsPath : '',
    });
    const candidates = getPythonCandidates();
    const { env, repoRoot } = preparePythonEnv(context);

    return new Promise((resolve) => {
        let attempt = 0;

        const tryNext = () => {
            if (attempt >= candidates.length) {
                resolve({ errors: [], internalError: 'Python interpreter not found.' });
                return;
            }

            const command = candidates[attempt];
            attempt += 1;
            let settled = false;

            const proc = cp.spawn(command, [script], {
                cwd: repoRoot,
                env,
            });

            proc.on('error', (error) => {
                if (error.code === 'ENOENT') {
                    tryNext();
                    return;
                }
                if (!settled) {
                    settled = true;
                    resolve({ errors: [], internalError: String(error) });
                }
            });

            let stdout = '';
            let stderr = '';

            proc.stdout.setEncoding('utf8');
            proc.stdout.on('data', (chunk) => {
                stdout += chunk;
            });

            proc.stderr.setEncoding('utf8');
            proc.stderr.on('data', (chunk) => {
                stderr += chunk;
            });

            const timeout = setTimeout(() => {
                if (!settled) {
                    settled = true;
                    proc.kill();
                    resolve({ errors: [], internalError: 'FCP parser timed out.' });
                }
            }, 5000);

            proc.on('close', () => {
                clearTimeout(timeout);
                if (settled) {
                    return;
                }
                settled = true;

                if (stderr.trim().length > 0) {
                    outputChannel.appendLine('[fcp] parser stderr:');
                    outputChannel.appendLine(stderr.trim());
                }

                if (!stdout.trim()) {
                    resolve({ errors: [], internalError: 'Empty response from parser.' });
                    return;
                }

                try {
                    const parsed = JSON.parse(stdout);
                    resolve(parsed);
                } catch (err) {
                    resolve({ errors: [], internalError: `Failed to parse python output: ${err}` });
                }
            });

            if (proc.pid) {
                proc.stdin.write(payload);
                proc.stdin.end();
            }
        };

        tryNext();
    });
}

function activate(context) {
    const outputChannel = vscode.window.createOutputChannel('FCP Language');
    context.subscriptions.push(outputChannel);

    const diagnostics = vscode.languages.createDiagnosticCollection('fcp');
    context.subscriptions.push(diagnostics);

    const completionProvider = vscode.languages.registerCompletionItemProvider(
        { language: 'fcp' },
        {
            provideCompletionItems(document) {
                return [...KEYWORD_COMPLETIONS, ...collectSymbols(document)];
            },
        },
        ' ', ':', '[', '{', '@', '"'
    );
    context.subscriptions.push(completionProvider);

    const pendingTimers = new Map();

    const scheduleDiagnostics = (document) => {
        if (document.languageId !== 'fcp') {
            return;
        }
        const key = document.uri.toString();
        if (pendingTimers.has(key)) {
            clearTimeout(pendingTimers.get(key));
        }
        const timer = setTimeout(async () => {
            pendingTimers.delete(key);
            const result = await runPythonLint(context, document, outputChannel);

            if (result.internalError) {
                outputChannel.appendLine(`[fcp] ${result.internalError}`);
            }

            const issues = Array.isArray(result.errors) ? result.errors : [];
            const diagnosticsForDocument = issues.map((error) => {
                const range = computeRange(document, error.range);
                const diagnostic = new vscode.Diagnostic(range, error.message || 'FCP error', severityFrom(error));
                diagnostic.source = 'fcp';
                return diagnostic;
            });

            diagnostics.set(document.uri, diagnosticsForDocument);
        }, 200);
        pendingTimers.set(key, timer);
    };

    context.subscriptions.push(
        vscode.workspace.onDidChangeTextDocument((event) => scheduleDiagnostics(event.document))
    );

    context.subscriptions.push(
        vscode.workspace.onDidOpenTextDocument((document) => scheduleDiagnostics(document))
    );

    context.subscriptions.push(
        vscode.workspace.onDidCloseTextDocument((document) => {
            diagnostics.delete(document.uri);
            const key = document.uri.toString();
            if (pendingTimers.has(key)) {
                clearTimeout(pendingTimers.get(key));
                pendingTimers.delete(key);
            }
        })
    );

    vscode.workspace.textDocuments.forEach((document) => scheduleDiagnostics(document));
}

function deactivate() {
    // Nothing to clean up explicitly.
}

module.exports = {
    activate,
    deactivate,
};
