import { useState, useCallback, useRef, useEffect } from 'react'
import { Routes, Route, useParams, useNavigate } from 'react-router-dom'
import Header from './components/Header'
import ChatPanel from './components/ChatPanel'
import CodePanel from './components/CodePanel'
import PreviewPanel from './components/PreviewPanel'
import StatusBar from './components/StatusBar'
import ResizeHandle from './components/ResizeHandle'
import VersionHistory from './components/VersionHistory'
import DeployModal from './components/DeployModal'
import ProjectsPage from './pages/ProjectsPage'
import StageSidebar from './components/StageSidebar'
import OverviewPage from './pages/stages/OverviewPage'
import RequirementsPage from './pages/stages/RequirementsPage'
import UserResearchPage from './pages/stages/UserResearchPage'
import TaskFlowsPage from './pages/stages/TaskFlowsPage'
import UserStoriesPage from './pages/stages/UserStoriesPage'
import { useGeneration } from './hooks/useGeneration'
import './App.css'

function EditorView() {
  const { projectId } = useParams()
  const navigate = useNavigate()
  const [chatWidth, setChatWidth] = useState(380)
  const [previewWidth, setPreviewWidth] = useState(420)
  const [activeFile, setActiveFile] = useState(null)
  const [openTabs, setOpenTabs] = useState([])
  const [showHistory, setShowHistory] = useState(false)
  const [showDeploy, setShowDeploy] = useState(false)
  const chatRef = useRef(null)

  const {
    files,
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
    loadProject,
    loadFiles,
    activeStage,
    setActiveStage,
    completedStages,
    stageData,
    fetchStages,
  } = useGeneration()

  // Load project from DB if projectId is in the URL
  useEffect(() => {
    if (projectId) {
      loadProject(projectId)
    }
  }, [projectId, loadProject])

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

  const handleVersionRestore = useCallback(() => {
    // Reload files after version restore
    if (loadFiles) loadFiles()
    if (projectId) loadProject(projectId)
  }, [loadFiles, loadProject, projectId])

  return (
    <div className="app-layout">
      <Header
        projectName={projectName}
        isGenerating={isGenerating}
        onStartPreview={startPreview}
        hasFiles={Object.keys(files).length > 0}
        onGoBack={() => navigate('/')}
        previewLoading={previewLoading}
        onToggleHistory={projectId ? () => setShowHistory(prev => !prev) : undefined}
        onToggleDeploy={() => setShowDeploy(true)}
      />

      <div className="workspace">
        <StageSidebar
          activeStage={activeStage}
          completedStages={completedStages}
          runningStage={isGenerating ? (currentStep || '').replace('running_', '').replace('_complete', '') : null}
          onStageClick={setActiveStage}
        />

        <ChatPanel
          ref={chatRef}
          width={chatWidth}
          messages={messages}
          isGenerating={isGenerating}
          onSend={(text) => sendPrompt(text, activeStage)}
        />
        <ResizeHandle onResize={(dx) => setChatWidth(w => Math.max(300, Math.min(600, w + dx)))} />

        <div className="main-content" style={{ flex: 1, height: '100%', overflow: 'auto', display: 'flex', flexDirection: 'column' }}>
          {activeStage === 'overview' && (
            <OverviewPage
              data={stageData.overview}
              isLoading={currentStep === 'running_overview'}
              onNext={() => setActiveStage('requirements')}
              onGenerate={() => sendPrompt('Generate Requirements based on overview', 'requirements')}
            />
          )}

          {activeStage === 'requirements' && (
            <RequirementsPage
              data={stageData.requirements}
              isLoading={currentStep === 'running_requirements'}
              onNext={() => setActiveStage('user_research')}
              onGenerate={() => sendPrompt('Generate User Research based on requirements', 'user_research')}
            />
          )}

          {activeStage === 'user_research' && (
            <UserResearchPage
              data={stageData.user_research}
              isLoading={currentStep === 'running_user_research'}
              onNext={() => setActiveStage('task_flows')}
              onGenerate={() => sendPrompt('Generate Task Flows based on user research', 'task_flows')}
            />
          )}

          {activeStage === 'task_flows' && (
            <TaskFlowsPage
              data={stageData.task_flows}
              isLoading={currentStep === 'running_task_flows'}
              onNext={() => setActiveStage('user_stories')}
              onGenerate={() => sendPrompt('Generate User Stories based on task flows', 'user_stories')}
            />
          )}

          {activeStage === 'user_stories' && (
            <UserStoriesPage
              data={stageData.user_stories}
              isLoading={currentStep === 'running_user_stories'}
              onNext={() => setActiveStage('code')}
              onGenerate={() => sendPrompt('Generate Code implementation', 'code')}
            />
          )}

          {(activeStage === 'code' || activeStage === 'preview') && (
            <div style={{ display: 'flex', width: '100%', height: '100%' }}>
              <CodePanel
                files={files}
                activeFile={activeFile}
                openTabs={openTabs}
                onOpenFile={handleOpenFile}
                onCloseTab={handleCloseTab}
              />
              <ResizeHandle onResize={(dx) => setPreviewWidth(w => Math.max(280, Math.min(700, w - dx)))} />
              <PreviewPanel
                width={previewWidth}
                previewUrl={previewUrl}
                previewLoading={previewLoading}
                previewError={previewError}
                onStartPreview={startPreview}
                hasFiles={Object.keys(files).length > 0}
              />
            </div>
          )}
        </div>
      </div>

      <StatusBar
        status={status}
        currentStep={currentStep}
        filesCount={Object.keys(files).length}
        testsStatus={testsStatus}
      />

      {/* Version History Slide-Over Panel */}
      {showHistory && projectId && (
        <div className="history-panel-overlay" onClick={() => setShowHistory(false)}>
          <div className="history-panel" onClick={(e) => e.stopPropagation()}>
            <VersionHistory
              projectId={projectId}
              onRestore={handleVersionRestore}
              onClose={() => setShowHistory(false)}
            />
          </div>
        </div>
      )}

      {/* Deploy Modal */}
      {showDeploy && (
        <DeployModal
          onClose={() => setShowDeploy(false)}
          projectName={projectName}
        />
      )}
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
