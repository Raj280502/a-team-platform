import { useState } from 'react'
import { ChevronRight, ChevronDown, BookOpen } from 'lucide-react'
import './StagePages.css'

export default function UserStoriesPage({ data, isLoading, onGenerateCode, onGenerate }) {
  const [expandedEpics, setExpandedEpics] = useState({})

  if (isLoading) {
    return (
      <div className="stage-page">
        <div className="stage-loading">
          <div className="stage-loading-spinner" />
          <p>Generating user stories...</p>
        </div>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="stage-page">
        <div className="stage-empty">
          <div className="stage-empty-icon">📖</div>
          <h3>User Stories</h3>
          <p>Generate epics, sprints, and user stories for this project.</p>
          {onGenerate && (
            <button className="stage-btn primary" onClick={onGenerate} style={{ marginTop: 16 }}>
              Generate User Stories
            </button>
          )}
        </div>
      </div>
    )
  }

  const epics = data.epics || []
  const totalStories = epics.reduce(
    (sum, e) => sum + (e.sprints || []).reduce((s, sp) => s + (sp.stories || []).length, 0),
    0
  )

  const toggleEpic = (i) => {
    setExpandedEpics(prev => ({ ...prev, [i]: !prev[i] }))
  }

  return (
    <div className="stage-page">
      <div className="stage-page-header">
        <div>
          <h1>User Stories</h1>
          <p>{totalStories} stories across {epics.length} epics</p>
        </div>
        <div className="stage-actions">
          <button className="stage-btn primary" onClick={onGenerateCode}>
            Generate Code <ChevronRight size={14} />
          </button>
        </div>
      </div>

      {epics.map((epic, ei) => {
        const isExpanded = expandedEpics[ei] !== false // default open

        return (
          <div className="epic-section" key={ei}>
            <div className="epic-header" onClick={() => toggleEpic(ei)}>
              {isExpanded ? <ChevronDown size={18} /> : <ChevronRight size={18} />}
              <BookOpen size={18} color="#818cf8" />
              <h3>{epic.name}</h3>
              <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginLeft: 'auto' }}>
                {(epic.sprints || []).reduce((s, sp) => s + (sp.stories || []).length, 0)} stories
              </span>
            </div>

            {isExpanded && (
              <>
                <p className="epic-desc">{epic.description}</p>

                {(epic.sprints || []).map((sprint, si) => (
                  <div className="sprint-card" key={si}>
                    <div className="sprint-header">
                      <div>
                        <div className="sprint-name">{sprint.name}</div>
                        <div className="sprint-goal">{sprint.goal}</div>
                      </div>
                      <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                        {(sprint.stories || []).length} stories
                      </span>
                    </div>

                    {(sprint.stories || []).map((story, sti) => (
                      <div className="story-card" key={sti}>
                        <div className="story-card-header">
                          <span className="story-id">{story.id}</span>
                          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                            <span className={`priority-badge priority-${story.priority}`}>
                              {story.priority}
                            </span>
                            <span className="story-points" title="Story points">
                              {story.story_points}
                            </span>
                          </div>
                        </div>
                        <div className="story-title">{story.title}</div>
                        <div className="story-format">
                          <strong>As a</strong> {story.as_a}, <strong>I want</strong> {story.i_want}, <strong>so that</strong> {story.so_that}
                        </div>
                        {story.acceptance_criteria?.length > 0 && (
                          <ul className="story-criteria">
                            {story.acceptance_criteria.map((ac, aci) => (
                              <li key={aci}>{ac}</li>
                            ))}
                          </ul>
                        )}
                      </div>
                    ))}
                  </div>
                ))}
              </>
            )}
          </div>
        )
      })}
    </div>
  )
}
