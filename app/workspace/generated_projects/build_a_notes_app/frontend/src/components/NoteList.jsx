import React, { useState, useEffect } from 'react';
// [auto-removed] import axios from 'axios';  -- file not found
import Note from './Note';

const NoteList = ({ folderId }) => {
  const [notes, setNotes] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterTerm, setFilterTerm] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchNotes = async () => {
      setLoading(true);
      try {
        const response = await axios.get(`/api/notes?folderId=${folderId}`);
        setNotes(response.data);
      } catch (error) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };
    fetchNotes();
  }, [folderId]);

  const handleSearch = (event) => {
    setSearchTerm(event.target.value);
  };

  const handleFilter = (event) => {
    setFilterTerm(event.target.value);
  };

  const filteredNotes = notes.filter((note) => {
    const searchRegex = new RegExp(searchTerm, 'i');
    const filterRegex = new RegExp(filterTerm, 'i');
    return searchRegex.test(note.title) && filterRegex.test(note.content);
  });

  if (loading) {
    return <div style={{ textAlign: 'center' }}>Loading...</div>;
  }

  if (error) {
    return <div style={{ textAlign: 'center', color: 'red' }}>{error}</div>;
  }

  return (
    <div className="note-list">
      <input
        type="search"
        placeholder="Search notes"
        value={searchTerm}
        onChange={handleSearch}
        style={{ width: '100%', padding: '10px', marginBottom: '10px' }}
      />
      <input
        type="search"
        placeholder="Filter notes"
        value={filterTerm}
        onChange={handleFilter}
        style={{ width: '100%', padding: '10px', marginBottom: '10px' }}
      />
      {filteredNotes.map((note) => (
        <Note key={note.id} note={note} />
      ))}
    </div>
  );
};

export default NoteList;