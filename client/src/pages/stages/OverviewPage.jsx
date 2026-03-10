import { Target, BarChart3, Clock, Cpu, ChevronRight } from 'lucide-react'
import './StagePages.css'

export default function OverviewPage({ data, isLoading, onNext, onGenerate }) {
  if (isLoading) {
    return (
      <div className="stage-page">
        <div className="stage-loading">
          <div className="stage-loading-spinner" />
          <p>Generating project overview...</p>
        </div>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="stage-page">
        <div className="stage-empty">
          <div className="stage-empty-icon">📋</div>
          <h3>Project Overview</h3>
          <p>Generate a comprehensive project overview with goals, audience, and recommendations.</p>
          {onGenerate && (
            <button className="stage-btn primary" onClick={onGenerate} style={{ marginTop: 16 }}>
              Generate Overview
            </button>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="stage-page">
      <div className="stage-page-header">
        <div>
          <h1>{data.title || 'Project Overview'}</h1>
          <p>{data.description}</p>
        </div>
        <div className="stage-actions">
          <button className="stage-btn primary" onClick={onNext}>
            Next: Requirements <ChevronRight size={14} />
          </button>
        </div>
      </div>

      {/* Goals */}
      <h3 className="section-title"><Target size={18} /> Goals</h3>
      <div className="stage-grid">
        {(data.goals || []).map((goal, i) => (
          <div className="stage-card" key={i}>
            <p>{goal}</p>
          </div>
        ))}
      </div>

      {/* Key Metrics */}
      {data.key_metrics?.length > 0 && (
        <>
          <h3 className="section-title"><BarChart3 size={18} /> Success Metrics</h3>
          <div className="stage-grid">
            {data.key_metrics.map((metric, i) => (
              <div className="stage-card" key={i}>
                <p>{metric}</p>
              </div>
            ))}
          </div>
        </>
      )}

      {/* Target Audience */}
      <h3 className="section-title">👥 Target Audience</h3>
      <div className="stage-card">
        <p>{data.target_audience}</p>
      </div>

      {/* Technical Recommendations */}
      {data.tech_recommendations && (
        <>
          <h3 className="section-title"><Cpu size={18} /> Tech Recommendations</h3>
          <div className="stage-card">
            <p>{data.tech_recommendations}</p>
          </div>
        </>
      )}

      {/* Timeline */}
      {data.timeline_estimate && (
        <>
          <h3 className="section-title"><Clock size={18} /> Timeline Estimate</h3>
          <div className="stage-card">
            <p>{data.timeline_estimate}</p>
          </div>
        </>
      )}

      {/* Domain */}
      {data.domain && (
        <div style={{ marginTop: 16 }}>
          <span className="tag">{data.domain}</span>
        </div>
      )}
    </div>
  )
}
