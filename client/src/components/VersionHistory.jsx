import { useState, useEffect, useCallback } from 'react'
import { History, RotateCcw, Save, Clock, FileCode2, X } from 'lucide-react'
import './VersionHistory.css'

export default function VersionHistory({ projectId, onRestore, onClose }) {
    const [versions, setVersions] = useState([])
    const [loading, setLoading] = useState(true)
    const [saving, setSaving] = useState(false)
    const [restoring, setRestoring] = useState(null)

    const fetchVersions = useCallback(async () => {
        if (!projectId) return
        try {
            const res = await fetch(`/api/projects/${projectId}/versions`)
            const data = await res.json()
            setVersions(data.versions || [])
        } catch (err) {
            console.error('Failed to load versions:', err)
        } finally {
            setLoading(false)
        }
    }, [projectId])

    useEffect(() => {
        fetchVersions()
    }, [fetchVersions])

    const handleSave = async () => {
        setSaving(true)
        try {
            const label = prompt('Version label (optional):') || ''
            await fetch(`/api/projects/${projectId}/versions`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ label }),
            })
            await fetchVersions()
        } catch (err) {
            console.error('Save version failed:', err)
        } finally {
            setSaving(false)
        }
    }

    const handleRestore = async (versionNum) => {
        if (!window.confirm(`Restore to version ${versionNum}? Current files will be saved as a new version first.`)) return
        setRestoring(versionNum)
        try {
            const res = await fetch(`/api/projects/${projectId}/versions/${versionNum}/restore`, {
                method: 'POST',
            })
            const data = await res.json()
            if (data.status === 'restored') {
                onRestore?.()
                await fetchVersions()
            }
        } catch (err) {
            console.error('Restore failed:', err)
        } finally {
            setRestoring(null)
        }
    }

    const formatDate = (iso) => {
        const d = new Date(iso)
        const now = new Date()
        const diffMs = now - d
        const diffMins = Math.floor(diffMs / 60000)
        const diffHours = Math.floor(diffMs / 3600000)
        if (diffMins < 1) return 'Just now'
        if (diffMins < 60) return `${diffMins}m ago`
        if (diffHours < 24) return `${diffHours}h ago`
        return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
    }

    return (
        <div className="version-history">
            <div className="vh-header">
                <div className="vh-title">
                    <History size={16} />
                    <span>Version History</span>
                </div>
                <div className="vh-actions">
                    <button className="vh-save-btn" onClick={handleSave} disabled={saving}>
                        <Save size={14} />
                        {saving ? 'Saving...' : 'Save Version'}
                    </button>
                    {onClose && (
                        <button className="vh-close-btn" onClick={onClose}>
                            <X size={14} />
                        </button>
                    )}
                </div>
            </div>

            <div className="vh-list">
                {loading && <div className="vh-loading">Loading versions...</div>}
                {!loading && versions.length === 0 && (
                    <div className="vh-empty">
                        <p>No versions saved yet</p>
                        <p className="vh-hint">Click "Save Version" to create a snapshot</p>
                    </div>
                )}
                {versions.map(v => (
                    <div key={v.id} className="vh-item">
                        <div className="vh-item-info">
                            <span className="vh-label">{v.label || `Version ${v.version_num}`}</span>
                            <div className="vh-meta">
                                <span><FileCode2 size={12} /> {v.file_count} files</span>
                                <span><Clock size={12} /> {formatDate(v.created_at)}</span>
                            </div>
                        </div>
                        <button
                            className="vh-restore-btn"
                            onClick={() => handleRestore(v.version_num)}
                            disabled={restoring === v.version_num}
                        >
                            <RotateCcw size={12} />
                            {restoring === v.version_num ? 'Restoring...' : 'Restore'}
                        </button>
                    </div>
                ))}
            </div>
        </div>
    )
}
