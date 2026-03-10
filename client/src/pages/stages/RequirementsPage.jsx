import { useState } from 'react'
import { ChevronRight, Filter } from 'lucide-react'
import './StagePages.css'

export default function RequirementsPage({ data, isLoading, onNext, onGenerate }) {
  const [filter, setFilter] = useState('all')

  if (isLoading) {
    return (
      <div className="stage-page">
        <div className="stage-loading">
          <div className="stage-loading-spinner" />
          <p>Generating project requirements...</p>
        </div>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="stage-page">
        <div className="stage-empty">
          <div className="stage-empty-icon">📝</div>
          <h3>Project Requirements</h3>
          <p>Generate functional and non-functional requirements for this project.</p>
          {onGenerate && (
            <button className="stage-btn primary" onClick={onGenerate} style={{ marginTop: 16 }}>
              Generate Requirements
            </button>
          )}
        </div>
      </div>
    )
  }

  const fr = data.functional_requirements || []
  const nfr = data.non_functional_requirements || []
  const filtered = filter === 'all' ? fr : fr.filter(r => r.priority === filter)

  return (
    <div className="stage-page">
      <div className="stage-page-header">
        <div>
          <h1>Project Requirements</h1>
          <p>Define project requirements</p>
        </div>
        <div className="stage-actions">
          <button className="stage-btn primary" onClick={onNext}>
            Next: User Research <ChevronRight size={14} />
          </button>
        </div>
      </div>

      {/* Functional Requirements */}
      <h3 className="section-title">✅ Functional Requirements ({fr.length})</h3>

      <div style={{ display: 'flex', gap: 6, marginBottom: 16 }}>
        {['all', 'high', 'medium', 'low'].map(f => (
          <button
            key={f}
            className={`tab-btn ${filter === f ? 'active' : ''}`}
            onClick={() => setFilter(f)}
            style={{ padding: '4px 12px', borderRadius: 6, border: 'none', fontSize: '0.78rem', cursor: 'pointer', background: filter === f ? 'var(--bg-secondary)' : 'transparent', color: filter === f ? 'var(--text-primary)' : 'var(--text-muted)', fontFamily: 'inherit', fontWeight: 500 }}
          >
            {f === 'all' ? 'All' : f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
      </div>

      {filtered.map((req, i) => (
        <div className="stage-card" key={i} style={{ display: 'flex', gap: 16, alignItems: 'flex-start' }}>
          <span style={{ fontFamily: 'monospace', fontSize: '0.75rem', color: '#818cf8', fontWeight: 700, whiteSpace: 'nowrap' }}>
            {req.id}
          </span>
          <div style={{ flex: 1 }}>
            <h3>{req.title}</h3>
            <p>{req.description}</p>
            <div style={{ marginTop: 8, display: 'flex', gap: 8 }}>
              <span className={`priority-badge priority-${req.priority}`}>{req.priority}</span>
              {req.category && <span className="tag">{req.category}</span>}
            </div>
          </div>
        </div>
      ))}

      {/* Non-Functional Requirements */}
      {nfr.length > 0 && (
        <>
          <h3 className="section-title">🔒 Non-Functional Requirements ({nfr.length})</h3>
          {nfr.map((req, i) => (
            <div className="stage-card" key={i} style={{ display: 'flex', gap: 16, alignItems: 'flex-start' }}>
              <span style={{ fontFamily: 'monospace', fontSize: '0.75rem', color: '#818cf8', fontWeight: 700, whiteSpace: 'nowrap' }}>
                {req.id}
              </span>
              <div style={{ flex: 1 }}>
                <h3>{req.title}</h3>
                <p>{req.description}</p>
                <div style={{ marginTop: 8, display: 'flex', gap: 8 }}>
                  <span className={`priority-badge priority-${req.priority}`}>{req.priority}</span>
                  {req.category && <span className="tag">{req.category}</span>}
                </div>
              </div>
            </div>
          ))}
        </>
      )}

      {/* Constraints */}
      {data.constraints?.length > 0 && (
        <>
          <h3 className="section-title">⚠️ Constraints</h3>
          <div className="stage-card">
            {data.constraints.map((c, i) => (
              <div className="stage-list-item" key={i}>{c}</div>
            ))}
          </div>
        </>
      )}

      {/* Assumptions */}
      {data.assumptions?.length > 0 && (
        <>
          <h3 className="section-title">💡 Assumptions</h3>
          <div className="stage-card">
            {data.assumptions.map((a, i) => (
              <div className="stage-list-item" key={i}>{a}</div>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
