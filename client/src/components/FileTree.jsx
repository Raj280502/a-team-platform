import { useMemo } from 'react'
import { ChevronRight, FolderOpen } from 'lucide-react'
import './FileTree.css'

const FILE_ICONS = {
    py: '🐍',
    jsx: '⚛️',
    tsx: '⚛️',
    js: '📜',
    ts: '📜',
    css: '🎨',
    html: '🌐',
    json: '📋',
    txt: '📄',
    md: '📖',
}

function getIcon(name) {
    const ext = name.split('.').pop()
    return FILE_ICONS[ext] || '📄'
}

export default function FileTree({ files, activeFile, onSelect }) {
    // Build tree structure
    const tree = useMemo(() => {
        const root = {}
        for (const path of Object.keys(files).sort()) {
            const parts = path.split('/')
            let node = root
            for (let i = 0; i < parts.length - 1; i++) {
                if (!node[parts[i]]) node[parts[i]] = { __children: {} }
                node = node[parts[i]].__children
            }
            node[parts[parts.length - 1]] = null // leaf = file
        }
        return root
    }, [files])

    const renderNode = (obj, prefix = '', depth = 0) => {
        return Object.entries(obj).map(([name, value]) => {
            if (name === '__children') return null
            const fullPath = prefix ? `${prefix}/${name}` : name
            const isFolder = value !== null

            if (isFolder) {
                return (
                    <div key={fullPath}>
                        <div
                            className="tree-item folder"
                            style={{ paddingLeft: 12 + depth * 14 }}
                        >
                            <FolderOpen size={13} className="tree-icon folder-icon" />
                            <span className="tree-name">{name}</span>
                        </div>
                        {renderNode(value.__children || value, fullPath, depth + 1)}
                    </div>
                )
            }

            return (
                <div
                    key={fullPath}
                    className={`tree-item file ${fullPath === activeFile ? 'active' : ''}`}
                    style={{ paddingLeft: 12 + depth * 14 }}
                    onClick={() => onSelect(fullPath)}
                >
                    <span className="tree-icon">{getIcon(name)}</span>
                    <span className="tree-name truncate">{name}</span>
                </div>
            )
        })
    }

    return (
        <div className="file-tree">
            <div className="file-tree-header">
                <span>Explorer</span>
            </div>
            <div className="file-tree-items">
                {Object.keys(files).length === 0 ? (
                    <div className="tree-empty">No files yet</div>
                ) : (
                    renderNode(tree)
                )}
            </div>
        </div>
    )
}
