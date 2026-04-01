import { Zap, Download, Play, ArrowLeft, Loader2, History, Rocket } from 'lucide-react'
import './Header.css'

export default function Header({ projectName, isGenerating, onStartPreview, hasFiles, onGoBack, previewLoading, onToggleHistory, onToggleDeploy }) {
    const handleDownload = () => {
        window.open('/api/download', '_blank')
    }

    return (
        <header className="header">
            <div className="header-left">
                {onGoBack && (
                    <button
                        className="header-btn secondary back-btn"
                        onClick={onGoBack}
                        title="Back to Projects"
                    >
                        <ArrowLeft size={14} />
                        <span>Projects</span>
                    </button>
                )}
                <div className="logo">
                    <div className="logo-icon">
                        <Zap size={16} />
                    </div>
                    <span className="logo-text">AI Code Factory</span>
                </div>
                {projectName && (
                    <span className="project-badge">{projectName}</span>
                )}
            </div>

            <div className="header-right">
                {onToggleHistory && (
                    <button
                        className="header-btn secondary"
                        onClick={onToggleHistory}
                        disabled={!hasFiles}
                        title="Version History"
                    >
                        <History size={14} />
                        <span>History</span>
                    </button>
                )}
                <button
                    className="header-btn secondary"
                    onClick={handleDownload}
                    disabled={!hasFiles}
                    title="Download as ZIP"
                >
                    <Download size={14} />
                    <span>Export</span>
                </button>
                {onToggleDeploy && (
                    <button
                        className="header-btn deploy-btn"
                        onClick={onToggleDeploy}
                        disabled={!hasFiles}
                        title="Deploy Project"
                    >
                        <Rocket size={14} />
                        <span>Deploy</span>
                    </button>
                )}
                <button
                    className="header-btn primary"
                    onClick={onStartPreview}
                    disabled={isGenerating || !hasFiles || previewLoading}
                >
                    {previewLoading ? <Loader2 size={14} className="spinning" /> : <Play size={14} />}
                    <span>{previewLoading ? 'Starting...' : 'Preview'}</span>
                </button>
            </div>
        </header>
    )
}
