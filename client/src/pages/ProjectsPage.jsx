import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Search, FileCode2, Calendar, Layers, Trash2, FolderOpen, Download } from 'lucide-react'
import './ProjectsPage.css'

export default function ProjectsPage() {
    const [projects, setProjects] = useState([])
    const [loading, setLoading] = useState(true)
    const [search, setSearch] = useState('')
    const [deleteTarget, setDeleteTarget] = useState(null)
    const navigate = useNavigate()

    const fetchProjects = useCallback(async () => {
        try {
            const res = await fetch('/api/projects')
            const data = await res.json()
            setProjects(data.projects || [])
        } catch (err) {
            console.error('Failed to load projects:', err)
        } finally {
            setLoading(false)
        }
    }, [])

    useEffect(() => {
        fetchProjects()
    }, [fetchProjects])

    const handleOpen = (projectId) => {
        navigate(`/editor/${projectId}`)
    }

    const handleDelete = async () => {
        if (!deleteTarget) return
        try {
            await fetch(`/api/projects/${deleteTarget}`, { method: 'DELETE' })
            setProjects(prev => prev.filter(p => p.id !== deleteTarget))
        } catch (err) {
            console.error('Delete failed:', err)
        }
        setDeleteTarget(null)
    }

    const handleDownload = (e, projectId) => {
        e.stopPropagation()
        // TODO: implement per-project download from DB
        window.open('/api/download', '_blank')
    }

    const filtered = projects.filter(p =>
        p.name.toLowerCase().includes(search.toLowerCase()) ||
        p.prompt.toLowerCase().includes(search.toLowerCase())
    )

    const formatDate = (iso) => {
        const d = new Date(iso)
        const now = new Date()
        const diffMs = now - d
        const diffMins = Math.floor(diffMs / 60000)
        const diffHours = Math.floor(diffMs / 3600000)
        const diffDays = Math.floor(diffMs / 86400000)

        if (diffMins < 1) return 'Just now'
        if (diffMins < 60) return `${diffMins}m ago`
        if (diffHours < 24) return `${diffHours}h ago`
        if (diffDays < 7) return `${diffDays}d ago`
        return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
    }

    return (
        <div className="projects-page">
            {/* Header */}
            <header className="projects-header">
                <div className="logo">
                    <span className="icon">🏭</span>
                    AI Code Factory
                </div>
                <button className="new-project-btn" onClick={() => navigate('/editor')}>
                    <Plus size={18} />
                    New Project
                </button>
            </header>

            {/* Hero */}
            <section className="projects-hero">
                <h1>Your Projects</h1>
                <p>Browse, open, or manage your AI-generated applications</p>

                <div className="search-bar-wrap">
                    <div className="search-bar">
                        <Search size={18} />
                        <input
                            type="text"
                            placeholder="Search projects by name or prompt..."
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                        />
                    </div>
                </div>
            </section>

            {!loading && filtered.length > 0 && (
                <div className="project-count">
                    {filtered.length} project{filtered.length !== 1 ? 's' : ''}
                    {search && ` matching "${search}"`}
                </div>
            )}

            {/* Loading */}
            {loading && (
                <div className="skeleton-grid">
                    {[1, 2, 3].map(i => <div key={i} className="skeleton-card" />)}
                </div>
            )}

            {/* Grid */}
            {!loading && (
                <div className="projects-grid">
                    {filtered.length === 0 ? (
                        <div className="empty-state">
                            <div className="empty-icon">📂</div>
                            <h2>{search ? 'No matches found' : 'No projects yet'}</h2>
                            <p>{search ? 'Try a different search term' : 'Create your first AI-generated project!'}</p>
                            {!search && (
                                <button className="new-project-btn" onClick={() => navigate('/editor')}>
                                    <Plus size={18} />
                                    Create Project
                                </button>
                            )}
                        </div>
                    ) : (
                        filtered.map(project => (
                            <div
                                key={project.id}
                                className="project-card"
                                onClick={() => handleOpen(project.id)}
                            >
                                <div className="card-top">
                                    <h3>{project.name}</h3>
                                    <span className={`status-badge ${project.status}`}>
                                        {project.status === 'complete' && '●'}
                                        {project.status === 'generating' && '◌'}
                                        {project.status === 'error' && '✕'}
                                        {' '}{project.status}
                                    </span>
                                </div>

                                <div className="card-prompt">
                                    {project.prompt || 'No description'}
                                </div>

                                <div className="card-meta">
                                    <span className="tech-badge">
                                        <Layers size={12} />
                                        {project.tech_stack}
                                    </span>
                                    <span className="meta-item">
                                        <FileCode2 size={14} />
                                        {project.file_count} files
                                    </span>
                                    <span className="meta-item">
                                        <Calendar size={14} />
                                        {formatDate(project.created_at)}
                                    </span>
                                </div>

                                <div className="card-actions">
                                    <button
                                        className="open-btn"
                                        onClick={(e) => { e.stopPropagation(); handleOpen(project.id) }}
                                    >
                                        <FolderOpen size={14} /> Open
                                    </button>
                                    <button onClick={(e) => handleDownload(e, project.id)}>
                                        <Download size={14} /> Download
                                    </button>
                                    <button
                                        className="delete-btn"
                                        onClick={(e) => { e.stopPropagation(); setDeleteTarget(project.id) }}
                                    >
                                        <Trash2 size={14} /> Delete
                                    </button>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            )}

            {/* Delete Confirmation Modal */}
            {deleteTarget && (
                <div className="modal-overlay" onClick={() => setDeleteTarget(null)}>
                    <div className="modal-box" onClick={(e) => e.stopPropagation()}>
                        <h3>Delete Project?</h3>
                        <p>This will permanently remove the project and all its files. This action cannot be undone.</p>
                        <div className="modal-actions">
                            <button className="cancel-btn" onClick={() => setDeleteTarget(null)}>
                                Cancel
                            </button>
                            <button className="confirm-delete-btn" onClick={handleDelete}>
                                Delete
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
