import { useState, useCallback, useRef, useEffect } from 'react'

const STEP_LABELS = {
    starting: '🚀 Starting generation...',
    overview_complete: '📋 Project overview generated',
    requirements_complete: '🎯 Requirements gathered',
    user_research_complete: '👥 User research completed',
    task_flows_complete: '🔄 Task flows mapped',
    user_stories_complete: '📚 User stories written',
    strategist_complete: '🧠 Technical scope analyzed',
    architect_complete: '📐 Architecture designed',
    coder_plan_ready: '📋 File plan ready',
    coder_complete: '🔨 Code generated',
    repair_complete: '🔧 Code repaired',
    preview_starting: '🌐 Starting preview servers...',
    preview_ready: '🌐 Preview ready!',
    preview_failed: '⚠️ Preview failed to start',
    complete: '✅ Done!',
    error: '❌ Error occurred',
    chat_processing: '💬 Processing changes...',
    chat_complete: '✅ Changes applied!',
}

export function useGeneration() {
    const [files, setFiles] = useState({})
    const [messages, setMessages] = useState([])
    const [status, setStatus] = useState('idle') // idle, generating, complete, error
    const [currentStep, setCurrentStep] = useState('')
    const [projectName, setProjectName] = useState('')
    const [previewUrl, setPreviewUrl] = useState('')
    const [previewLoading, setPreviewLoading] = useState(false)
    const [previewError, setPreviewError] = useState('')
    const [isGenerating, setIsGenerating] = useState(false)
    const [testsStatus, setTestsStatus] = useState(null)
    const eventSourceRef = useRef(null)

    // Add a message to the chat
    const addMessage = useCallback((role, text, type = 'message') => {
        setMessages(prev => [...prev, { id: Date.now(), role, text, type, ts: new Date() }])
    }, [])

    // Add a pipeline step indicator
    const addStep = useCallback((text, done = false) => {
        setMessages(prev => [...prev, {
            id: Date.now(),
            role: 'system',
            text,
            type: done ? 'step-done' : 'step',
            ts: new Date(),
        }])
    }, [])

    // Mark all pending step indicators as done (stops spinners)
    const markAllStepsDone = useCallback(() => {
        setMessages(prev => prev.map(m =>
            m.type === 'step' ? { ...m, type: 'step-done' } : m
        ))
    }, [])

    // Parse raw API error into friendly message
    const parseErrorMessage = useCallback((raw) => {
        const str = typeof raw === 'object' ? JSON.stringify(raw) : String(raw)
        // Groq rate limit
        const rateMatch = str.match(/rate.?limit/i)
        if (rateMatch) {
            const timeMatch = str.match(/(\d+m[\d.]+s|\d+ (?:seconds?|minutes?))/i)
            const wait = timeMatch ? timeMatch[1] : 'a few minutes'
            return `⏳ Groq rate limit reached. Please try again in ${wait}. You can upgrade at console.groq.com/settings/billing`
        }
        // Generic API error with message field
        const msgMatch = str.match(/['"]message['"]\s*:\s*['"]([^'"]+)['"]/)
        if (msgMatch) return msgMatch[1]
        // Fallback
        return str.length > 200 ? str.substring(0, 200) + '...' : str
    }, [])

    // Load files from API
    const loadFiles = useCallback(async () => {
        try {
            const res = await fetch('/api/files')
            const data = await res.json()
            const fileMap = {}
            for (const [path, info] of Object.entries(data.files || {})) {
                fileMap[path] = info.content
            }
            setFiles(fileMap)
        } catch (e) {
            console.error('Failed to load files:', e)
        }
    }, [])

    // Start SSE event stream
    const startStream = useCallback(() => {
        if (eventSourceRef.current) eventSourceRef.current.close()

        const es = new EventSource('/api/stream')
        let lastStep = ''
        eventSourceRef.current = es

        es.onmessage = (event) => {
            const data = JSON.parse(event.data)

            // Step updates
            if (data.step && data.step !== lastStep) {
                const label = STEP_LABELS[data.step] || data.step
                if (data.step !== 'complete' && data.step !== 'error') {
                    addStep(label, false)
                }
                setCurrentStep(data.step)
                lastStep = data.step

                // Track preview loading state
                if (data.step === 'preview_starting') {
                    setPreviewLoading(true)
                    setPreviewError('')
                } else if (data.step === 'preview_ready') {
                    setPreviewLoading(false)
                    setPreviewError('')
                } else if (data.step === 'preview_failed') {
                    setPreviewLoading(false)
                    setPreviewError('Preview servers failed to start')
                }
            }

            // Real-time file updates — merge new files into state as they arrive
            if (data.new_files && Object.keys(data.new_files).length > 0) {
                setFiles(prev => {
                    const updated = { ...prev }
                    for (const [path, info] of Object.entries(data.new_files)) {
                        updated[path] = info.content
                    }
                    return updated
                })
                // Show which files were just generated
                const fileNames = Object.keys(data.new_files)
                for (const fn of fileNames) {
                    addStep(`📄 Generated: ${fn}`, true)
                }
            }

            // Project name
            if (data.project_name) setProjectName(data.project_name)

            // Tests
            if (data.tests_passed !== undefined) {
                setTestsStatus(data.tests_passed ? 'passed' : 'failed')
            }

            // Preview URL
            if (data.preview_url) setPreviewUrl(data.preview_url)

            // Final event
            if (data.final) {
                es.close()
                eventSourceRef.current = null
                loadFiles()  // Final sync to ensure all files are loaded

                if (data.step === 'complete') {
                    setStatus('complete')
                    setIsGenerating(false)
                    markAllStepsDone()
                    addStep('✅ Project generated successfully!', true)
                } else if (data.step === 'error') {
                    setStatus('error')
                    setIsGenerating(false)
                    markAllStepsDone()
                    addStep('❌ Generation failed', true)
                }
            }
        }

        es.onerror = () => {
            es.close()
            eventSourceRef.current = null
            markAllStepsDone()
        }
    }, [addStep, loadFiles, markAllStepsDone])

    // Send a prompt
    const sendPrompt = useCallback(async (text) => {
        if (!text.trim() || isGenerating) return

        addMessage('user', text)
        setIsGenerating(true)
        setStatus('generating')

        const hasFiles = Object.keys(files).length > 0
        const endpoint = hasFiles ? '/api/chat' : '/api/generate'

        addStep('🧠 Analyzing your request...')
        startStream()

        try {
            const res = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: text }),
            })
            const data = await res.json()

            if (data.error) {
                setIsGenerating(false)
                setStatus('error')
                markAllStepsDone()
                addStep('❌ ' + parseErrorMessage(data.error), true)
            }
        } catch (err) {
            setIsGenerating(false)
            setStatus('error')
            markAllStepsDone()
            addStep('❌ Network error: ' + err.message, true)
        }
    }, [isGenerating, files, addMessage, addStep, startStream, markAllStepsDone, parseErrorMessage])

    // Start preview
    const startPreview = useCallback(async () => {
        setPreviewLoading(true)
        setPreviewError('')
        setPreviewUrl('')
        addStep('🌐 Starting preview servers...', false)
        try {
            const res = await fetch('/api/preview/start', { method: 'POST' })
            const data = await res.json()
            if (data.started) {
                setPreviewUrl(data.url)
                setPreviewLoading(false)
                setPreviewError('')
                markAllStepsDone()
                addStep('🌐 Preview ready!', true)
            } else {
                setPreviewLoading(false)
                setPreviewError(data.error || 'Preview failed to start')
                markAllStepsDone()
                addStep('⚠️ Preview failed: ' + (data.error || 'Unknown error'), true)
            }
        } catch (e) {
            setPreviewLoading(false)
            setPreviewError('Network error starting preview')
            markAllStepsDone()
            addStep('⚠️ Preview error: ' + e.message, true)
            console.error('Preview failed:', e)
        }
    }, [addStep, markAllStepsDone])

    // Load a project from the database
    const loadProject = useCallback(async (projectId) => {
        try {
            const res = await fetch(`/api/projects/${projectId}`)
            if (!res.ok) {
                console.error('Failed to load project:', res.status)
                return
            }
            const data = await res.json()

            // Restore files
            const fileMap = {}
            for (const [path, info] of Object.entries(data.files || {})) {
                fileMap[path] = typeof info === 'string' ? info : info.content
            }
            setFiles(fileMap)

            // Restore project name
            if (data.project?.name) {
                setProjectName(data.project.name)
            }

            // Restore chat messages
            if (data.messages?.length > 0) {
                const restored = data.messages.map((m, i) => ({
                    id: Date.now() + i,
                    role: m.role,
                    text: m.text || m.content || '',
                    type: m.type || m.msg_type || 'message',
                    ts: m.ts ? new Date(m.ts) : new Date(),
                }))
                setMessages(restored)
            }

            setStatus('complete')
            setCurrentStep('complete')
            setIsGenerating(false)
        } catch (err) {
            console.error('Load project error:', err)
        }
    }, [])

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            if (eventSourceRef.current) eventSourceRef.current.close()
        }
    }, [])

    return {
        files,
        setFiles,
        messages,
        status,
        currentStep,
        projectName,
        previewUrl,
        previewLoading,
        previewError,
        isGenerating,
        sendPrompt,
        startPreview,
        testsStatus,
        loadFiles,
        loadProject,
    }
}

