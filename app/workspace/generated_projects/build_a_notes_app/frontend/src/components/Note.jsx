// [auto-removed] import React from 'react';  -- file not found

const Note = ({ note }) => {
  return (
    <div className="item-card" style={{ flexDirection: 'column', alignItems: 'flex-start' }}>
      <div className="item-title">{note.title || 'Untitled'}</div>
      {note.content && (
        <div className="item-description" style={{ marginTop: '8px', whiteSpace: 'pre-wrap' }}>
          {note.content.length > 200 ? note.content.slice(0, 200) + '...' : note.content}
        </div>
      )}
      {note.folder && (
        <span style={{ fontSize: '0.75rem', color: '#9ca3af', marginTop: '8px' }}>
          📁 {note.folder}
        </span>
      )}
    </div>
  );
};

export default Note;
