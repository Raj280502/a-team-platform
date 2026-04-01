import { useState } from 'react'
import { X, Rocket, Download, FileCode2, CheckCircle2, Loader2, Box, Cloud, Terminal, Copy, ExternalLink } from 'lucide-react'
import './DeployModal.css'

const DEPLOY_TARGETS = [
    {
        id: 'configs',
        name: 'Generate Deploy Configs',
        icon: <FileCode2 size={20} />,
        desc: 'Create Dockerfile, vercel.json, railway.json, docker-compose.yml, and Procfile',
        color: '#a78bfa',
    },
    {
        id: 'download',
        name: 'Download Deploy-Ready ZIP',
        icon: <Download size={20} />,
        desc: 'Download project with all deployment configs included',
        color: '#34d399',
    },
    {
        id: 'vercel',
        name: 'Deploy to Vercel',
        icon: <Cloud size={20} />,
        desc: 'Push your project to Vercel for instant hosting',
        color: '#f472b6',
    },
    {
        id: 'docker',
        name: 'Deploy with Docker',
        icon: <Box size={20} />,
        desc: 'Build and run with Docker Compose locally',
        color: '#60a5fa',
    },
]

export default function DeployModal({ onClose, projectName }) {
    const [activeTarget, setActiveTarget] = useState(null)
    const [status, setStatus] = useState('idle')  // idle, loading, success, error
    const [generatedConfigs, setGeneratedConfigs] = useState(null)
    const [error, setError] = useState('')
    const [copied, setCopied] = useState('')

    const handleGenerateConfigs = async () => {
        setStatus('loading')
        setError('')
        try {
            const res = await fetch('/api/deploy/configs', { method: 'POST' })
            const data = await res.json()
            if (data.error) {
                setError(data.error)
                setStatus('error')
            } else {
                setGeneratedConfigs(data)
                setStatus('success')
            }
        } catch (err) {
            setError(err.message)
            setStatus('error')
        }
    }

    const handleDownloadReady = async () => {
        setStatus('loading')
        setError('')
        try {
            // Generate configs first
            await fetch('/api/deploy/configs', { method: 'POST' })
            // Then download
            window.open('/api/deploy/download-ready', '_blank')
            setStatus('success')
        } catch (err) {
            setError(err.message)
            setStatus('error')
        }
    }

    const handleAction = async (targetId) => {
        setActiveTarget(targetId)
        setStatus('idle')
        setGeneratedConfigs(null)
        setError('')

        if (targetId === 'configs') {
            await handleGenerateConfigs()
        } else if (targetId === 'download') {
            await handleDownloadReady()
        }
        // 'vercel' and 'docker' show instruction panels
    }

    const copyToClipboard = (text, label) => {
        navigator.clipboard.writeText(text)
        setCopied(label)
        setTimeout(() => setCopied(''), 2000)
    }

    const renderTargetContent = () => {
        if (!activeTarget) return null

        if (activeTarget === 'configs') {
            if (status === 'loading') {
                return (
                    <div className="deploy-status loading">
                        <Loader2 size={24} className="spinning" />
                        <span>Generating deployment configs...</span>
                    </div>
                )
            }
            if (status === 'success' && generatedConfigs) {
                return (
                    <div className="deploy-result">
                        <div className="deploy-status success">
                            <CheckCircle2 size={20} />
                            <span>Configs generated and added to project files!</span>
                        </div>
                        <div className="config-list">
                            {generatedConfigs.configs.map(name => (
                                <div key={name} className="config-item">
                                    <FileCode2 size={14} />
                                    <span>{name}</span>
                                    <button
                                        className="copy-btn"
                                        onClick={() => copyToClipboard(generatedConfigs.files[name], name)}
                                    >
                                        {copied === name ? <CheckCircle2 size={12} /> : <Copy size={12} />}
                                        {copied === name ? 'Copied!' : 'Copy'}
                                    </button>
                                </div>
                            ))}
                        </div>
                    </div>
                )
            }
        }

        if (activeTarget === 'download') {
            if (status === 'loading') {
                return (
                    <div className="deploy-status loading">
                        <Loader2 size={24} className="spinning" />
                        <span>Packaging project...</span>
                    </div>
                )
            }
            if (status === 'success') {
                return (
                    <div className="deploy-status success">
                        <CheckCircle2 size={20} />
                        <span>Download started! Check your downloads folder.</span>
                    </div>
                )
            }
        }

        if (activeTarget === 'vercel') {
            return (
                <div className="deploy-instructions">
                    <h4>Deploy to Vercel</h4>
                    <div className="instruction-steps">
                        <div className="step">
                            <span className="step-num">1</span>
                            <div className="step-content">
                                <p>Generate deploy configs first</p>
                                <button className="action-btn" onClick={handleGenerateConfigs} disabled={status === 'loading'}>
                                    {status === 'loading' ? <Loader2 size={14} className="spinning" /> : <FileCode2 size={14} />}
                                    Generate Configs
                                </button>
                                {status === 'success' && <span className="step-done"><CheckCircle2 size={14} /> Done</span>}
                            </div>
                        </div>
                        <div className="step">
                            <span className="step-num">2</span>
                            <div className="step-content">
                                <p>Download the project</p>
                                <button className="action-btn" onClick={handleDownloadReady}>
                                    <Download size={14} />
                                    Download ZIP
                                </button>
                            </div>
                        </div>
                        <div className="step">
                            <span className="step-num">3</span>
                            <div className="step-content">
                                <p>Push to GitHub and connect with Vercel</p>
                                <a href="https://vercel.com/new" target="_blank" rel="noopener noreferrer" className="action-btn link-btn">
                                    <ExternalLink size={14} />
                                    Open Vercel Dashboard
                                </a>
                            </div>
                        </div>
                        <div className="step">
                            <span className="step-num">4</span>
                            <div className="step-content">
                                <p>Or use Vercel CLI:</p>
                                <div className="code-block">
                                    <code>npx vercel --prod</code>
                                    <button className="copy-btn" onClick={() => copyToClipboard('npx vercel --prod', 'vercel-cmd')}>
                                        {copied === 'vercel-cmd' ? <CheckCircle2 size={12} /> : <Copy size={12} />}
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )
        }

        if (activeTarget === 'docker') {
            return (
                <div className="deploy-instructions">
                    <h4>Deploy with Docker</h4>
                    <div className="instruction-steps">
                        <div className="step">
                            <span className="step-num">1</span>
                            <div className="step-content">
                                <p>Generate deploy configs</p>
                                <button className="action-btn" onClick={handleGenerateConfigs} disabled={status === 'loading'}>
                                    {status === 'loading' ? <Loader2 size={14} className="spinning" /> : <FileCode2 size={14} />}
                                    Generate Configs
                                </button>
                                {status === 'success' && <span className="step-done"><CheckCircle2 size={14} /> Done</span>}
                            </div>
                        </div>
                        <div className="step">
                            <span className="step-num">2</span>
                            <div className="step-content">
                                <p>Build and run with Docker Compose:</p>
                                <div className="code-block">
                                    <code>docker-compose up --build</code>
                                    <button className="copy-btn" onClick={() => copyToClipboard('docker-compose up --build', 'docker-cmd')}>
                                        {copied === 'docker-cmd' ? <CheckCircle2 size={12} /> : <Copy size={12} />}
                                    </button>
                                </div>
                            </div>
                        </div>
                        <div className="step">
                            <span className="step-num">3</span>
                            <div className="step-content">
                                <p>Or build manually:</p>
                                <div className="code-block">
                                    <code>docker build -t {projectName || 'my-app'} .</code>
                                    <button className="copy-btn" onClick={() => copyToClipboard(`docker build -t ${projectName || 'my-app'} .`, 'docker-build')}>
                                        {copied === 'docker-build' ? <CheckCircle2 size={12} /> : <Copy size={12} />}
                                    </button>
                                </div>
                                <div className="code-block">
                                    <code>docker run -p 5000:5000 {projectName || 'my-app'}</code>
                                    <button className="copy-btn" onClick={() => copyToClipboard(`docker run -p 5000:5000 ${projectName || 'my-app'}`, 'docker-run')}>
                                        {copied === 'docker-run' ? <CheckCircle2 size={12} /> : <Copy size={12} />}
                                    </button>
                                </div>
                            </div>
                        </div>
                        <div className="step">
                            <span className="step-num">4</span>
                            <div className="step-content">
                                <p>Open <strong>http://localhost:5000</strong> in your browser</p>
                            </div>
                        </div>
                    </div>
                </div>
            )
        }

        if (error) {
            return (
                <div className="deploy-status error">
                    <span>❌ {error}</span>
                </div>
            )
        }

        return null
    }

    return (
        <div className="deploy-overlay" onClick={onClose}>
            <div className="deploy-modal" onClick={(e) => e.stopPropagation()}>
                <div className="deploy-header">
                    <div className="deploy-title">
                        <Rocket size={20} />
                        <h3>Deploy Project</h3>
                        {projectName && <span className="deploy-project-name">{projectName}</span>}
                    </div>
                    <button className="deploy-close" onClick={onClose}>
                        <X size={18} />
                    </button>
                </div>

                <div className="deploy-body">
                    <div className="deploy-targets">
                        {DEPLOY_TARGETS.map(target => (
                            <button
                                key={target.id}
                                className={`deploy-target ${activeTarget === target.id ? 'active' : ''}`}
                                onClick={() => handleAction(target.id)}
                                style={{ '--target-color': target.color }}
                            >
                                <div className="target-icon">{target.icon}</div>
                                <div className="target-info">
                                    <span className="target-name">{target.name}</span>
                                    <span className="target-desc">{target.desc}</span>
                                </div>
                            </button>
                        ))}
                    </div>

                    <div className="deploy-content">
                        {!activeTarget && (
                            <div className="deploy-placeholder">
                                <Terminal size={32} />
                                <p>Select a deployment option to get started</p>
                            </div>
                        )}
                        {renderTargetContent()}
                    </div>
                </div>
            </div>
        </div>
    )
}
