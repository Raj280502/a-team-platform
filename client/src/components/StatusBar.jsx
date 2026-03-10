import './StatusBar.css'

export default function StatusBar({ status, currentStep, filesCount, testsStatus }) {
    const dotClass = {
        idle: '',
        generating: 'generating',
        complete: 'active',
        error: 'error',
    }[status] || ''

    const statusText = {
        idle: 'Ready',
        generating: 'Generating...',
        complete: 'Complete',
        error: 'Error',
    }[status] || 'Ready'

    return (
        <div className="status-bar">
            <div className="status-left">
                <div className="status-item">
                    <div className={`status-dot ${dotClass}`} />
                    <span>{statusText}</span>
                </div>
                {currentStep && currentStep !== 'idle' && (
                    <div className="status-item">
                        <span className="status-label">Step:</span>
                        <span className="status-value">{currentStep}</span>
                    </div>
                )}
            </div>
            <div className="status-right">
                {testsStatus && (
                    <div className="status-item">
                        <span>{testsStatus === 'passed' ? '✅' : '❌'} Tests</span>
                    </div>
                )}
                <span>Files: {filesCount}</span>
                <span className="status-brand">Groq LLM</span>
            </div>
        </div>
    )
}
