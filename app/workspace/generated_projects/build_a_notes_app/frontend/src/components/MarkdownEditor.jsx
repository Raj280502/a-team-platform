import React, { useState, useEffect } from 'react';
// [auto-removed] import axios from 'axios';  -- file not found

const MarkdownEditor = ({ noteId, noteContent, handleSaveNote }) => {
  const [editorContent, setEditorContent] = useState(noteContent);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState(null);

  const handleEditorChange = (event) => {
    setEditorContent(event.target.value);
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const response = await axios.put(`/api/notes/${noteId}`, {
        content: editorContent,
      });
      if (response.status === 200) {
        handleSaveNote();
      } else {
        setError('Failed to save note');
      }
    } catch (error) {
      setError(error.message);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="markdown-editor">
      <textarea
        className="editor"
        value={editorContent}
        onChange={handleEditorChange}
        placeholder="Write your note here..."
      />
      {isSaving ? (
        <button className="save-button" disabled>Saving...</button>
      ) : (
        <button className="save-button" onClick={handleSave}>
          Save
        </button>
      )}
      {error && <div className="error-message">{error}</div>}
    </div>
  );
};

export default MarkdownEditor;