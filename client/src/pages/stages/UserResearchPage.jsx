import { useState } from 'react'
import { User, ChevronRight } from 'lucide-react'
import './StagePages.css'

export default function UserResearchPage({ data, isLoading, onNext, onGenerate }) {
  const [selectedRole, setSelectedRole] = useState(0)

  if (isLoading) {
    return (
      <div className="stage-page">
        <div className="stage-loading">
          <div className="stage-loading-spinner" />
          <p>Analyzing user needs & creating personas...</p>
        </div>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="stage-page">
        <div className="stage-empty">
          <div className="stage-empty-icon">👥</div>
          <h3>User Research</h3>
          <p>Generate user roles, personas, and empathy maps for this project.</p>
          {onGenerate && (
            <button className="stage-btn primary" onClick={onGenerate} style={{ marginTop: 16 }}>
              Generate User Research
            </button>
          )}
        </div>
      </div>
    )
  }

  const roles = data.roles || []
  const personas = data.personas || []
  const activeRole = roles[selectedRole]
  const rolePersona = personas.find(p => p.role === activeRole?.name) || personas[selectedRole] || personas[0]

  return (
    <div className="stage-page" style={{ padding: 0 }}>
      <div className="research-layout">
        {/* Left: User Roles */}
        <div className="role-list">
          <div style={{ padding: '16px 16px 10px', fontSize: '0.72rem', fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', color: 'var(--text-muted)' }}>
            User Roles
          </div>
          {roles.map((role, i) => (
            <div
              key={i}
              className={`role-item ${i === selectedRole ? 'active' : ''}`}
              onClick={() => setSelectedRole(i)}
            >
              <div className="role-item-icon">
                <User size={14} />
              </div>
              <div className="role-item-info">
                <h4>{role.name}</h4>
                <p>{role.description}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Right: Persona Detail */}
        <div className="research-content">
          <div className="stage-page-header" style={{ marginBottom: 20 }}>
            <div>
              <h1>User Research</h1>
              <p>Understanding your users</p>
            </div>
            <div className="stage-actions">
              <button className="stage-btn primary" onClick={onNext}>
                Next: Task Flows <ChevronRight size={14} />
              </button>
            </div>
          </div>

          {rolePersona ? (
            <>
              {/* Persona Header */}
              <div className="persona-header">
                <div className="persona-badge">{rolePersona.role}</div>
                <h2 className="persona-name">{rolePersona.name}</h2>
                <div className="persona-details">
                  {rolePersona.age} years old · {rolePersona.occupation} · {rolePersona.location}
                </div>
              </div>

              {/* Goals / Characteristics / Pain Points */}
              <div className="stage-grid-3">
                <div className="info-card goals">
                  <h4>🎯 Goals</h4>
                  <ul>
                    {(rolePersona.goals || []).map((g, i) => (
                      <li key={i}>{g}</li>
                    ))}
                  </ul>
                </div>

                <div className="info-card characteristics">
                  <h4>✅ Key Characteristics</h4>
                  <ul>
                    {(rolePersona.key_characteristics || []).map((c, i) => (
                      <li key={i}>{c}</li>
                    ))}
                  </ul>
                </div>

                <div className="info-card pain-points">
                  <h4>⚠️ Pain Points</h4>
                  <ul>
                    {(rolePersona.pain_points || []).map((p, i) => (
                      <li key={i}>{p}</li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Empathy Map */}
              {rolePersona.empathy_map && (
                <>
                  <h3 className="section-title">Empathy Map</h3>
                  <div className="empathy-map">
                    {['thinks', 'feels', 'says', 'does'].map(quad => (
                      <div className="empathy-quadrant" key={quad}>
                        <h4>{quad.charAt(0).toUpperCase() + quad.slice(1)}</h4>
                        <ul>
                          {(rolePersona.empathy_map[quad] || []).map((item, i) => (
                            <li key={i}>{item}</li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </>
          ) : (
            <div className="stage-empty">
              <p>Select a user role to view persona details</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
