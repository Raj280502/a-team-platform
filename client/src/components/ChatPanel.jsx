import { useState, useRef, useEffect, forwardRef } from 'react'
import { Send, Sparkles } from 'lucide-react'
import './ChatPanel.css'

const SUGGESTIONS = [
    { icon: '📋', text: 'Build a task manager with categories, priorities, and due dates' },
    { icon: '🍳', text: 'Build a recipe book app where users can add, search, and favorite recipes' },
    { icon: '💰', text: 'Build a personal expense tracker with charts and budget categories' },
    { icon: '📝', text: 'Build a notes app with markdown support and folder organization' },
]

const ChatPanel = forwardRef(function ChatPanel({ width, messages, isGenerating, onSend }, ref) {
    const [input, setInput] = useState('')
    const messagesEndRef = useRef(null)
    const textareaRef = useRef(null)

    // Auto-scroll to bottom
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages])

    const handleSend = () => {
        if (!input.trim() || isGenerating) return
        onSend(input.trim())
        setInput('')
        if (textareaRef.current) textareaRef.current.style.height = '24px'
    }

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSend()
        }
    }

    const handleInput = (e) => {
        setInput(e.target.value)
        const el = e.target
        el.style.height = '24px'
        el.style.height = Math.min(el.scrollHeight, 120) + 'px'
    }

    const useSuggestion = (text) => {
        setInput(text)
        onSend(text)
    }

    const showWelcome = messages.length === 0

    return (
        <div className="chat-panel" style={{ width }} ref={ref}>
            <div className="chat-messages">
                {showWelcome ? (
                    <div className="chat-welcome">
                        <div className="welcome-glow" />
                        <Sparkles className="welcome-icon" size={38} />
                        <h2 className="welcome-title">What do you want to build?</h2>
                        <p className="welcome-desc">
                            Describe your app and I'll generate a complete working project
                            with a Flask API backend and React frontend.
                        </p>
                        <div className="suggestions">
                            {SUGGESTIONS.map((s, i) => (
                                <button
                                    key={i}
                                    className="suggestion-chip"
                                    onClick={() => useSuggestion(s.text)}
                                >
                                    <span className="suggestion-icon">{s.icon}</span>
                                    <span>{s.text}</span>
                                </button>
                            ))}
                        </div>
                    </div>
                ) : (
                    messages.map((msg) => {
                        if (msg.type === 'step' || msg.type === 'step-done') {
                            return (
                                <div key={msg.id} className={`step-indicator ${msg.type === 'step-done' ? 'done' : ''}`}>
                                    {msg.type !== 'step-done' && <span className="spinner" />}
                                    <span>{msg.text}</span>
                                </div>
                            )
                        }
                        return (
                            <div key={msg.id} className="chat-message">
                                <div className={`msg-avatar ${msg.role}`}>
                                    {msg.role === 'user' ? 'U' : 'AI'}
                                </div>
                                <div className="msg-body">
                                    <div className="msg-sender">{msg.role === 'user' ? 'You' : 'AI Code Factory'}</div>
                                    <div className="msg-text">{msg.text}</div>
                                </div>
                            </div>
                        )
                    })
                )}
                <div ref={messagesEndRef} />
            </div>

            <div className="chat-input-area">
                <div className={`chat-input-box ${isGenerating ? 'disabled' : ''}`}>
                    <textarea
                        ref={textareaRef}
                        className="chat-input"
                        value={input}
                        onChange={handleInput}
                        onKeyDown={handleKeyDown}
                        placeholder={isGenerating ? 'Generating...' : 'Describe your app...'}
                        rows={1}
                        disabled={isGenerating}
                    />
                    <button
                        className="send-btn"
                        onClick={handleSend}
                        disabled={!input.trim() || isGenerating}
                    >
                        <Send size={15} />
                    </button>
                </div>
            </div>
        </div>
    )
})

export default ChatPanel
