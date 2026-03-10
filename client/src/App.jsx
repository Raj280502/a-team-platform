import { useState, useCallback, useRef, useEffect } from 'react'
import { Routes, Route, useParams, useNavigate } from 'react-router-dom'
import Header from './components/Header'
import ChatPanel from './components/ChatPanel'
import CodePanel from './components/CodePanel'
import PreviewPanel from './components/PreviewPanel'
import StatusBar from './components/StatusBar'
import ResizeHandle from './components/ResizeHandle'
import StageSidebar from './components/StageSidebar'
import ProjectsPage from './pages/ProjectsPage'
import OverviewPage from './pages/stages/OverviewPage'
import RequirementsPage from './pages/stages/RequirementsPage'
import UserResearchPage from './pages/stages/UserResearchPage'
import TaskFlowsPage from './pages/stages/TaskFlowsPage'
import UserStoriesPage from './pages/stages/UserStoriesPage'
import { useGeneration } from './hooks/useGeneration'
import './App.css'

const STAGES = ['overview', 'requirements', 'user_research', 'task_flows', 'user_stories']

function EditorView() {
  const { projectId } = useParams()
  const navigate = useNavigate()
  const [chatWidth, setChatWidth] = useState(380)
  const [previewWidth, setPreviewWidth] = useState(420)
  const [activeFile, setActiveFile] = useState(null)
  const [openTabs, setOpenTabs] = useState([])
  const [activeStage, setActiveStage] = useState('overview')
  const [promptInput, setPromptInput] = useState('')
  const chatRef = useRef(null)
  const hasAutoSwitched = useRef(false) // Prevents re-triggering auto-switch

  const {
    files,
    messages,
    status,
    currentStep,
    projectName,
    previewUrl,
    isGenerating,
    sendPrompt,
    startPreview,
    testsStatus,
    loadProject,
    stageData,
    runStage,
    runningStage,
    completedStages,
  } = useGeneration()

  // Load project from DB if projectId is in the URL
  useEffect(() => {
    if (projectId) {
      loadProject(projectId)
    }
  }, [projectId, loadProject])

  // Auto-switch to code view ONCE when project with files is loaded from DB
  useEffect(() => {
    if (!hasAutoSwitched.current && Object.keys(files).length > 0 && !runningStage && completedStages.length === 0) {
      hasAutoSwitched.current = true
      setActiveStage('code')
    }
  }, [files, runningStage, completedStages])

  const handleOpenFile = useCallback((path) => {
    setActiveFile(path)
    setOpenTabs(prev => prev.includes(path) ? prev : [...prev, path])
  }, [])

  const handleCloseTab = useCallback((path) => {
    setOpenTabs(prev => {
      const next = prev.filter(t => t !== path)
      if (activeFile === path) {
        setActiveFile(next.length > 0 ? next[next.length - 1] : null)
      }
      return next
    })
  }, [activeFile])

  // Auto-open first file when files change
  useEffect(() => {
    if (Object.keys(files).length > 0 && !activeFile) {
      const priority = ['frontend/src/App.jsx', 'backend/app.py', 'frontend/src/App.css']
      const first = priority.find(f => files[f]) || Object.keys(files)[0]
      handleOpenFile(first)
    }
  }, [files, activeFile, handleOpenFile])

  // Handle stage navigation
  const handleStageClick = (stageName) => {
    setActiveStage(stageName)
  }

  // Handle stage-gated "Next" buttons
  const handleNextStage = (currentStageName) => {
    const idx = STAGES.indexOf(currentStageName)
    if (idx < STAGES.length - 1) {
      const next = STAGES[idx + 1]
      setActiveStage(next)
      // Auto-run the next stage if not already completed
      if (!completedStages.includes(next)) {
        runStage(next)
      }
    }
  }

  // Handle initial prompt submission → starts first stage
  const handleStartFirstStage = (prompt) => {
    if (!prompt.trim()) return
    runStage('overview', prompt)
    setActiveStage('overview')
  }

  // Handle "Generate Code" after all SDLC stages
  const handleGenerateCode = () => {
    setActiveStage('code')
    // Trigger code generation via the existing pipeline
    fetch('/api/stages/generate', { method: 'POST' })
  }

  // Render the active stage page
  const renderStagePage = () => {
    const isRunning = runningStage === activeStage
    const userPrompt = promptInput || stageData?.project_overview?.title || projectName

    const handleGenerateStage = () => {
      runStage(activeStage, userPrompt)
    }

    switch (activeStage) {
      case 'overview':
        return (
          <OverviewPage
            data={stageData?.project_overview}
            isLoading={isRunning}
            onNext={() => handleNextStage('overview')}
            onGenerate={handleGenerateStage}
          />
        )
      case 'requirements':
        return (
          <RequirementsPage
            data={stageData?.requirements}
            isLoading={isRunning}
            onNext={() => handleNextStage('requirements')}
            onGenerate={handleGenerateStage}
          />
        )
      case 'user_research':
        return (
          <UserResearchPage
            data={stageData?.user_research}
            isLoading={isRunning}
            onNext={() => handleNextStage('user_research')}
            onGenerate={handleGenerateStage}
          />
        )
      case 'task_flows':
        return (
          <TaskFlowsPage
            data={stageData?.task_flows}
            isLoading={isRunning}
            onNext={() => handleNextStage('task_flows')}
            onGenerate={handleGenerateStage}
          />
        )
      case 'user_stories':
        return (
          <UserStoriesPage
            data={stageData?.user_stories}
            isLoading={isRunning}
            onGenerateCode={handleGenerateCode}
            onGenerate={handleGenerateStage}
          />
        )
      case 'code':
      case 'preview':
      default:
        return null // Show the code editor workspace
    }
  }

  const hasFiles = Object.keys(files).length > 0
  const showCodeEditor = activeStage === 'code' || activeStage === 'preview'

  return (
    <div className="app-layout">
      <Header
        projectName={projectName}
        isGenerating={isGenerating}
        onStartPreview={startPreview}
        hasFiles={Object.keys(files).length > 0}
        onGoBack={() => navigate('/')}
      />

      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        <StageSidebar
          activeStage={activeStage}
          completedStages={completedStages}
          runningStage={runningStage}
          onStageClick={handleStageClick}
        />

        {showCodeEditor ? (
          /* Code editor workspace */
          <div className="workspace" style={{ flex: 1 }}>
            <ChatPanel
              ref={chatRef}
              width={chatWidth}
              messages={messages}
              isGenerating={isGenerating}
              onSend={sendPrompt}
            />

            <ResizeHandle
              onResize={(dx) => setChatWidth(w => Math.max(300, Math.min(600, w + dx)))}
            />

            <CodePanel
              files={files}
              activeFile={activeFile}
              openTabs={openTabs}
              onOpenFile={handleOpenFile}
              onCloseTab={handleCloseTab}
            />

            <ResizeHandle
              onResize={(dx) => setPreviewWidth(w => Math.max(280, Math.min(700, w - dx)))}
            />

            <PreviewPanel
              width={previewWidth}
              previewUrl={previewUrl}
            />
          </div>
        ) : (
          /* SDLC stage pages */
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
            {!stageData?.project_overview && !runningStage ? (
              /* Initial prompt input */
              <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <div style={{ textAlign: 'center', maxWidth: 540 }}>
                  <div style={{ fontSize: '2.5rem', marginBottom: 16 }}>🏭</div>
                  <h2 style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: 8 }}>
                    What do you want to build?
                  </h2>
                  <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: 24 }}>
                    Describe your project idea and we'll generate the full SDLC pipeline — overview, requirements, user research, task flows, user stories, and code.
                  </p>
                  <div style={{ display: 'flex', gap: 10 }}>
                    <input
                      type="text"
                      value={promptInput}
                      onChange={(e) => setPromptInput(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && handleStartFirstStage(promptInput)}
                      placeholder="e.g. Build a notes app with markdown support and folder organization"
                      style={{
                        flex: 1, padding: '12px 18px', borderRadius: 10,
                        border: '1px solid var(--border-color)', background: 'var(--bg-secondary)',
                        color: 'var(--text-primary)', fontSize: '0.9rem', fontFamily: 'inherit',
                        outline: 'none',
                      }}
                    />
                    <button
                      className="stage-btn primary"
                      onClick={() => handleStartFirstStage(promptInput)}
                      disabled={!promptInput.trim()}
                    >
                      Generate
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              renderStagePage()
            )}
          </div>
        )}
      </div>

      <StatusBar
        status={status}
        currentStep={currentStep}
        filesCount={Object.keys(files).length}
        testsStatus={testsStatus}
      />
    </div>
  )
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<ProjectsPage />} />
      <Route path="/editor" element={<EditorView />} />
      <Route path="/editor/:projectId" element={<EditorView />} />
    </Routes>
  )
}
