import { useRef, useEffect } from 'react'
import Editor from '@monaco-editor/react'
import { X, FileCode } from 'lucide-react'
import './EditorPane.css'

const LANG_MAP = {
    py: 'python',
    jsx: 'javascript',
    tsx: 'typescript',
    js: 'javascript',
    ts: 'typescript',
    css: 'css',
    html: 'html',
    json: 'json',
    md: 'markdown',
}

function getLanguage(path) {
    const ext = path.split('.').pop()
    return LANG_MAP[ext] || 'plaintext'
}

function getFileName(path) {
    return path.split('/').pop()
}

export default function EditorPane({ files, activeFile, openTabs, onOpenFile, onCloseTab }) {
    const editorRef = useRef(null)

    const handleEditorMount = (editor) => {
        editorRef.current = editor
    }

    const handleEditorChange = (value) => {
        if (!activeFile || !value) return
        // Debounced save
        clearTimeout(window.__saveTimeout)
        window.__saveTimeout = setTimeout(() => {
            fetch(`/api/file/${activeFile}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content: value }),
            })
        }, 1000)
    }

    if (!activeFile || !files[activeFile]) {
        return (
            <div className="editor-container">
                <div className="editor-empty-state">
                    <FileCode size={36} className="empty-icon" />
                    <p>Select a file to view its code</p>
                </div>
            </div>
        )
    }

    return (
        <div className="editor-container">
            {/* Tab bar */}
            <div className="editor-tab-bar">
                {openTabs.map(tab => (
                    <button
                        key={tab}
                        className={`editor-tab ${tab === activeFile ? 'active' : ''}`}
                        onClick={() => onOpenFile(tab)}
                    >
                        <span className="tab-name">{getFileName(tab)}</span>
                        <span className="tab-close" onClick={(e) => { e.stopPropagation(); onCloseTab(tab) }}>
                            <X size={11} />
                        </span>
                    </button>
                ))}
            </div>

            {/* Monaco Editor */}
            <div className="editor-wrapper">
                <Editor
                    key={activeFile}
                    height="100%"
                    language={getLanguage(activeFile)}
                    value={files[activeFile] || ''}
                    theme="vs-dark"
                    onChange={handleEditorChange}
                    onMount={handleEditorMount}
                    options={{
                        fontSize: 13,
                        fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
                        minimap: { enabled: false },
                        scrollBeyondLastLine: false,
                        padding: { top: 10 },
                        lineNumbers: 'on',
                        renderLineHighlight: 'line',
                        bracketPairColorization: { enabled: true },
                        smoothScrolling: true,
                        cursorBlinking: 'smooth',
                        cursorSmoothCaretAnimation: 'on',
                        wordWrap: 'on',
                        automaticLayout: true,
                    }}
                />
            </div>
        </div>
    )
}
