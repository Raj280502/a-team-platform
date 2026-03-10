import { useState, useCallback, useMemo } from 'react'
import {
  ReactFlow,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  MarkerType,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import { ChevronRight, Download } from 'lucide-react'
import './StagePages.css'

/* Custom node styles by type */
const nodeColors = {
  start:    { bg: '#22c55e', text: '#fff', border: '#16a34a' },
  action:   { bg: '#3b82f6', text: '#fff', border: '#2563eb' },
  decision: { bg: '#fbbf24', text: '#000', border: '#f59e0b' },
  system:   { bg: '#6b7280', text: '#fff', border: '#4b5563' },
  end:      { bg: '#ef4444', text: '#fff', border: '#dc2626' },
}

const nodeShapes = {
  start:    { borderRadius: '50%', width: 60, height: 60 },
  action:   { borderRadius: 8, width: 180, height: 50 },
  decision: { borderRadius: 4, width: 160, height: 60, transform: 'rotate(0deg)' },
  system:   { borderRadius: 8, width: 180, height: 50 },
  end:      { borderRadius: '50%', width: 60, height: 60 },
}

function convertFlowToReactFlow(flow) {
  if (!flow?.steps) return { nodes: [], edges: [] }

  const nodes = []
  const edges = []
  const cols = 3
  const xGap = 250
  const yGap = 120

  flow.steps.forEach((step, i) => {
    const color = nodeColors[step.type] || nodeColors.action
    const shape = nodeShapes[step.type] || nodeShapes.action
    const row = Math.floor(i / cols)
    const col = i % cols

    nodes.push({
      id: step.id,
      data: { label: step.label },
      position: { x: col * xGap + 50, y: row * yGap + 50 },
      style: {
        background: color.bg,
        color: color.text,
        border: `2px solid ${color.border}`,
        borderRadius: shape.borderRadius,
        width: shape.width,
        height: shape.height,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: '0.78rem',
        fontWeight: 600,
        boxShadow: `0 2px 8px ${color.bg}33`,
        textAlign: 'center',
        padding: '4px 8px',
      },
    })

    // Edges
    for (const conn of step.next_steps || []) {
      edges.push({
        id: `${step.id}-${conn.target_id}`,
        source: step.id,
        target: conn.target_id,
        label: conn.label || '',
        type: 'smoothstep',
        animated: step.type === 'decision',
        markerEnd: { type: MarkerType.ArrowClosed, width: 16, height: 16 },
        style: { stroke: '#64748b', strokeWidth: 1.5 },
        labelStyle: { fontSize: '0.7rem', fill: '#94a3b8', fontWeight: 600 },
      })
    }
  })

  return { nodes, edges }
}

function FlowDiagram({ flow }) {
  const { nodes: initialNodes, edges: initialEdges } = useMemo(
    () => convertFlowToReactFlow(flow),
    [flow]
  )
  const [nodes, , onNodesChange] = useNodesState(initialNodes)
  const [edges, , onEdgesChange] = useEdgesState(initialEdges)

  return (
    <div className="flow-container">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
        proOptions={{ hideAttribution: true }}
      >
        <Controls position="bottom-right" />
        <Background color="#334155" gap={20} size={1} />
      </ReactFlow>
    </div>
  )
}

function StepByStep({ flow }) {
  return (
    <div>
      {(flow.steps || []).map((step, i) => (
        <div className="stage-card" key={i} style={{ display: 'flex', gap: 14, alignItems: 'center' }}>
          <span
            style={{
              display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
              width: 28, height: 28, borderRadius: '50%',
              background: (nodeColors[step.type] || nodeColors.action).bg,
              color: (nodeColors[step.type] || nodeColors.action).text,
              fontSize: '0.72rem', fontWeight: 700, flexShrink: 0,
            }}
          >
            {i + 1}
          </span>
          <div>
            <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>
              {step.label}
            </div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
              Type: {step.type} {step.next_steps?.length ? `→ ${step.next_steps.map(n => n.target_id).join(', ')}` : ''}
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

export default function TaskFlowsPage({ data, isLoading, onNext, onGenerate }) {
  const [selectedFlow, setSelectedFlow] = useState(0)
  const [tab, setTab] = useState('diagram')

  if (isLoading) {
    return (
      <div className="stage-page">
        <div className="stage-loading">
          <div className="stage-loading-spinner" />
          <p>Generating task flows...</p>
        </div>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="stage-page">
        <div className="stage-empty">
          <div className="stage-empty-icon">🔄</div>
          <h3>Task Flows</h3>
          <p>Generate interactive user journey flowcharts for this project.</p>
          {onGenerate && (
            <button className="stage-btn primary" onClick={onGenerate} style={{ marginTop: 16 }}>
              Generate Task Flows
            </button>
          )}
        </div>
      </div>
    )
  }

  const flows = data.flows || []
  const activeFlow = flows[selectedFlow]

  return (
    <div className="stage-page" style={{ padding: 0 }}>
      <div className="research-layout">
        {/* Left: Flow list */}
        <div className="flow-list">
          <div style={{ padding: '16px 16px 10px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.72rem', fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', color: 'var(--text-muted)' }}>
              Task Flows
            </span>
          </div>
          {flows.map((flow, i) => (
            <div
              key={i}
              className={`flow-item ${i === selectedFlow ? 'active' : ''}`}
              onClick={() => { setSelectedFlow(i); setTab('diagram') }}
            >
              <div>
                <span className="flow-item-num">{i + 1}</span>
                <span className="flow-item-name">{flow.name}</span>
              </div>
              <div className="flow-item-roles" style={{ marginTop: 6 }}>
                {(flow.primary_roles || []).map((r, j) => (
                  <span className="tag" key={j}>{r}</span>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Right: Flow detail */}
        <div className="research-content">
          <div className="stage-page-header" style={{ marginBottom: 16 }}>
            <div>
              <h1>Task Flows</h1>
              <p>Analyzing user journeys</p>
            </div>
            <div className="stage-actions">
              <button className="stage-btn primary" onClick={onNext}>
                Next: User Stories <ChevronRight size={14} />
              </button>
            </div>
          </div>

          {activeFlow && (
            <>
              <div className="stage-card" style={{ marginBottom: 16 }}>
                <span className="tag" style={{ marginBottom: 8, display: 'inline-block' }}>Task Flow</span>
                <h3 style={{ fontSize: '1.1rem' }}>{activeFlow.name}</h3>
                <p>{activeFlow.description}</p>
                <div style={{ marginTop: 10, display: 'flex', gap: 16 }}>
                  <div>
                    <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 600 }}>Primary Roles: </span>
                    {(activeFlow.primary_roles || []).map((r, i) => (
                      <span className="tag" key={i}>{r}</span>
                    ))}
                  </div>
                  {activeFlow.secondary_roles?.length > 0 && (
                    <div>
                      <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 600 }}>Secondary: </span>
                      {activeFlow.secondary_roles.map((r, i) => (
                        <span className="tag" key={i} style={{ background: 'rgba(156,163,175,0.15)', color: '#9ca3af' }}>{r}</span>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Tab switcher */}
              <div className="tab-switcher">
                <button className={`tab-btn ${tab === 'diagram' ? 'active' : ''}`} onClick={() => setTab('diagram')}>
                  Task Flow Diagram
                </button>
                <button className={`tab-btn ${tab === 'steps' ? 'active' : ''}`} onClick={() => setTab('steps')}>
                  Step-by-Step Process
                </button>
              </div>

              {tab === 'diagram' ? (
                <FlowDiagram flow={activeFlow} />
              ) : (
                <StepByStep flow={activeFlow} />
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}
