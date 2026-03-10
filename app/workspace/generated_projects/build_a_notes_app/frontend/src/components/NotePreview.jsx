import React, { useState, useEffect } from 'react';
// [auto-removed] import axios from 'axios';  -- file not found
// [auto-removed] import DOMPurify from 'dompurify';  -- file not found
import './NotePreview.css';

const NotePreview = ({ noteId }) => {
  const [note, setNote] = useState({});
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const fetchNote = async () => {
      setIsLoading(true);
      try {
        const response = await axios.get(`/api/notes/${noteId}`);
        setNote(response.data);
      } catch (error) {
        setError(error.message);
      } finally {
        setIsLoading(false);
      }
    };
    fetchNote();
  }, [noteId]);

  if (isLoading) {
    return <div className="note-preview">Loading...</div>;
  }

  if (error) {
    return <div className="note-preview">Error: {error}</div>;
  }

  const sanitizedNoteContent = DOMPurify.sanitize(note.content);

  return (
    <div className="note-preview">
      <h2 className="note-title">{note.title}</h2>
      <div
        className="note-content"
        dangerouslySetInnerHTML={{ __html: sanitizedNoteContent }}
      />
    </div>
  );
};

export default NotePreview;