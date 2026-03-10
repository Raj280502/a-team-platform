import { useState, useEffect, useCallback, useRef } from 'react'
import { RefreshCw, Globe, ExternalLink, Play, Loader2, AlertTriangle } from 'lucide-react'
import './PreviewPanel.css'

export default function PreviewPanel({ width, previewUrl, previewLoading, previewError, onStartPreview, hasFiles }) {
    const [iframeError, setIframeError] = useState(false)
    const [iframeLoading, setIframeLoading] = useState(false)
    const iframeRef = useRef(null)
    const retryTimerRef = useRef(null)
    const prevUrlRef = useRef('')

    const hasPreview = previewUrl && previewUrl !== ''
    const isLoading = previewLoading || iframeLoading
    const errorMessage = previewError || (iframeError ? 'Preview failed to load — the app may have crashed' : '')

    // When previewUrl changes, load it with loading state
    useEffect(() => {
        if (hasPreview && previewUrl !== prevUrlRef.current) {
            prevUrlRef.current = previewUrl
            setIframeError(false)
            setIframeLoading(true)

            // Safety timeout: if iframe doesn't load in 15s, show error
            if (retryTimerRef.current) clearTimeout(retryTimerRef.current)
            retryTimerRef.current = setTimeout(() => {
                setIframeLoading(prev => {
                    if (prev) setIframeError(true)
                    return false
                })
            }, 15000)
        }
    }, [previewUrl, hasPreview])

    // Cleanup timer
    useEffect(() => {
        return () => {
            if (retryTimerRef.current) clearTimeout(retryTimerRef.current)
        }
    }, [])

    const handleIframeLoad = useCallback(() => {
        setIframeLoading(false)
        setIframeError(false)
        if (retryTimerRef.current) clearTimeout(retryTimerRef.current)
    }, [])

    const handleIframeError = useCallback(() => {
        setIframeLoading(false)
        setIframeError(true)
        if (retryTimerRef.current) clearTimeout(retryTimerRef.current)
    }, [])

    const handleRefresh = useCallback(() => {
        if (iframeRef.current && hasPreview) {
            setIframeError(false)
            setIframeLoading(true)
            // Force reload by toggling src
            const url = iframeRef.current.src
            iframeRef.current.src = 'about:blank'
            setTimeout(() => {
                if (iframeRef.current) iframeRef.current.src = url
            }, 100)

            // Safety timeout
            if (retryTimerRef.current) clearTimeout(retryTimerRef.current)
            retryTimerRef.current = setTimeout(() => {
                setIframeLoading(prev => {
                    if (prev) setIframeError(true)
                    return false
                })
            }, 15000)
        }
    }, [hasPreview])

    const handleExternal = useCallback(() => {
        if (previewUrl) window.open(previewUrl, '_blank')
    }, [previewUrl])

    const handleRetryPreview = useCallback(() => {
        setIframeError(false)
        if (onStartPreview) onStartPreview()
    }, [onStartPreview])

    // Determine what to show in the body
    const renderBody = () => {
        // Loading state (starting preview servers)
        if (previewLoading) {
            return (
                <div className="preview-placeholder">
                    <Loader2 size={36} className="placeholder-icon spinning" />
                    <p>Starting preview servers...</p>
                    <span className="placeholder-hint">Installing dependencies and launching dev servers</span>
                </div>
            )
        }

        // Has URL — show iframe (with inline loading overlay)
        if (hasPreview) {
            return (
                <>
                    {iframeLoading && (
                        <div className="preview-loading-overlay">
                            <Loader2 size={28} className="spinning" />
                            <span>Loading preview...</span>
                        </div>
                    )}
                    {iframeError && (
                        <div className="preview-error-overlay">
                            <AlertTriangle size={32} className="error-icon" />
                            <p>Preview failed to load</p>
                            <span className="error-hint">{errorMessage || 'The app may still be starting up'}</span>
                            <div className="error-actions">
                                <button className="retry-btn" onClick={handleRefresh}>
                                    <RefreshCw size={14} /> Refresh
                                </button>
                                <button className="retry-btn primary" onClick={handleRetryPreview}>
                                    <Play size={14} /> Restart Preview
                                </button>
                            </div>
                        </div>
                    )}
                    <iframe
                        ref={iframeRef}
                        id="preview-iframe"
                        src={previewUrl}
                        title="Preview"
                        onLoad={handleIframeLoad}
                        onError={handleIframeError}
                        style={{ opacity: iframeError ? 0 : 1 }}
                    />
                </>
            )
        }

        // Error but no URL
        if (errorMessage) {
            return (
                <div className="preview-placeholder error">
                    <AlertTriangle size={36} className="placeholder-icon error-icon" />
                    <p>Preview failed</p>
                    <span className="placeholder-hint">{errorMessage}</span>
                    {hasFiles && (
                        <button className="retry-btn primary" onClick={handleRetryPreview} style={{ marginTop: 12 }}>
                            <Play size={14} /> Retry Preview
                        </button>
                    )}
                </div>
            )
        }

        // Default: no preview yet
        return (
            <div className="preview-placeholder">
                <Globe size={40} className="placeholder-icon" />
                <p>Preview will appear here</p>
                <span className="placeholder-hint">
                    {hasFiles
                        ? 'Click ▶ Preview to start the app'
                        : 'Generate a project to see the live preview'}
                </span>
                {hasFiles && (
                    <button className="retry-btn primary" onClick={handleRetryPreview} style={{ marginTop: 12 }}>
                        <Play size={14} /> Start Preview
                    </button>
                )}
            </div>
        )
    }

    return (
        <div className="preview-panel" style={{ width }}>
            {/* Header */}
            <div className="preview-header">
                <span className="preview-label">Preview</span>
                <div className="preview-url-bar">
                    <Globe size={11} className="url-lock" />
                    <span className="url-text">
                        {hasPreview ? previewUrl.replace('http://', '') : 'localhost:5173'}
                    </span>
                </div>
                <div className="preview-actions">
                    <button
                        className="preview-btn"
                        onClick={handleRefresh}
                        title="Refresh"
                        disabled={!hasPreview || isLoading}
                    >
                        <RefreshCw size={13} className={isLoading ? 'spinning' : ''} />
                    </button>
                    <button
                        className="preview-btn"
                        onClick={handleExternal}
                        title="Open in new tab"
                        disabled={!hasPreview}
                    >
                        <ExternalLink size={13} />
                    </button>
                </div>
            </div>

            {/* Body */}
            <div className="preview-body">
                {renderBody()}
            </div>
        </div>
    )
}
