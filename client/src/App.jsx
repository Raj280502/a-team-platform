import { useState, useCallback, useRef, useEffect } from 'react'
import { Routes, Route, useParams, useNavigate } from 'react-router-dom'
import Header from './components/Header'
import ChatPanel from './components/ChatPanel'
import CodePanel from './components/CodePanel'
import PreviewPanel from './components/PreviewPanel'
import StatusBar from './components/StatusBar'
import ResizeHandle from './components/ResizeHandle'
import ProjectsPage from './pages/ProjectsPage'
import { useGeneration } from './hooks/useGeneration'
import './App.css'

function EditorView() {
  const { projectId } = useParams()
  const navigate = useNavigate()
  const [chatWidth, setChatWidth] = useState(380)
  const [previewWidth, setPreviewWidth] = useState(420)
  const [activeFile, setActiveFile] = useState(null)
  const [openTabs, setOpenTabs] = useState([])
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

  return (
    <div className="app-layout">
      <Header
        projectName={projectName}
        isGenerating={isGenerating}
        onStartPreview={startPreview}
        hasFiles={Object.keys(files).length > 0}
        onGoBack={() => navigate('/')}
        previewLoading={previewLoading}
      />

      <div className="workspace">
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
          previewLoading={previewLoading}
          previewError={previewError}
          onStartPreview={startPreview}
          hasFiles={Object.keys(files).length > 0}
        />
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
