import { useState, useCallback } from 'react'
import { Code2, Terminal as TerminalIcon, FileCode } from 'lucide-react'
import FileTree from './FileTree'
import EditorPane from './EditorPane'
import './CodePanel.css'

export default function CodePanel({ files, activeFile, openTabs, onOpenFile, onCloseTab }) {
    const [activeTab, setActiveTab] = useState('code') // 'code' | 'terminal'

    return (
        <div className="code-panel">
            {/* Toolbar */}
            <div className="code-toolbar">
                <div className="toolbar-tabs">
                    <button
                        className={`toolbar-tab ${activeTab === 'code' ? 'active' : ''}`}
                        onClick={() => setActiveTab('code')}
                    >
                        <Code2 size={13} />
                        <span>Code</span>
                    </button>
                    <button
                        className={`toolbar-tab ${activeTab === 'terminal' ? 'active' : ''}`}
                        onClick={() => setActiveTab('terminal')}
                    >
                        <TerminalIcon size={13} />
                        <span>Terminal</span>
                    </button>
                </div>
                <div className="toolbar-info">
                    <FileCode size={12} />
                    <span>{Object.keys(files).length} files</span>
                </div>
            </div>

            {/* Code view */}
            {activeTab === 'code' && (
                <div className="code-body">
                    <FileTree
                        files={files}
                        activeFile={activeFile}
                        onSelect={onOpenFile}
                    />
                    <EditorPane
                        files={files}
                        activeFile={activeFile}
                        openTabs={openTabs}
                        onOpenFile={onOpenFile}
                        onCloseTab={onCloseTab}
                    />
                </div>
            )}

            {/* Terminal view */}
            {activeTab === 'terminal' && (
                <div className="terminal-pane">
                    <div className="terminal-output" id="terminal-output">
                        <span className="terminal-prompt">$</span> Pipeline output will appear here...
                    </div>
                </div>
            )}
        </div>
    )
}
