import { Home, FileText, Users, GitBranch, BookOpen, Code, Eye, Check, Loader } from 'lucide-react'
import './StageSidebar.css'

const STAGES = [
  { name: 'overview',      label: 'Project Overview',      desc: 'Vision & goals',                icon: Home },
  { name: 'requirements',  label: 'Requirements',          desc: 'Define project requirements',   icon: FileText },
  { name: 'user_research', label: 'User Research',         desc: 'Analyze user needs & personas', icon: Users },
  { name: 'task_flows',    label: 'Task Flows',            desc: 'Define user journeys & tasks',  icon: GitBranch },
  { name: 'user_stories',  label: 'User Stories',          desc: 'View sprint stories & tasks',   icon: BookOpen },
]

const CODE_STAGES = [
  { name: 'code',    label: 'Code Generation', desc: 'Generate frontend & backend', icon: Code },
  { name: 'preview', label: 'Preview',         desc: 'Live preview of generated app', icon: Eye },
]

export default function StageSidebar({ activeStage, completedStages = [], runningStage, onStageClick }) {
  const getStatus = (name) => {
    if (runningStage === name) return 'running'
    if (completedStages.includes(name)) return 'completed'
    if (name === activeStage) return 'active'

    // A stage is enabled if all previous stages are completed
    const idx = STAGES.findIndex(s => s.name === name)
    if (idx === 0) return 'active' // First stage always accessible
    const prevCompleted = STAGES.slice(0, idx).every(s => completedStages.includes(s.name))
    if (prevCompleted) return 'active'

    return 'disabled'
  }

  const renderStage = (stage) => {
    const status = getStatus(stage.name)
    const Icon = stage.icon

    return (
      <li
        key={stage.name}
        className={`stage-item ${status}`}
        onClick={() => status !== 'disabled' && onStageClick(stage.name)}
      >
        <div className="stage-icon">
          {status === 'running' ? (
            <Loader size={16} />
          ) : (
            <Icon size={16} />
          )}
        </div>
        <div className="stage-info">
          <div className="stage-label">{stage.label}</div>
          <div className="stage-desc">{stage.desc}</div>
        </div>
        {status === 'completed' && (
          <div className="stage-check">
            <Check size={16} color="#22c55e" />
          </div>
        )}
      </li>
    )
  }

  return (
    <nav className="stage-sidebar">
      <div className="stage-sidebar-header">Project Stages</div>
      <ul className="stage-list">
        {STAGES.map(renderStage)}
        <div className="stage-divider" />
        <div className="stage-divider-label">Code</div>
        {CODE_STAGES.map(renderStage)}
      </ul>
    </nav>
  )
}
