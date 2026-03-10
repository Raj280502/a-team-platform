import React, { useState } from 'react';
// [auto-removed] import axios from 'axios';  -- file not found

const FolderForm = ({ onCreateFolder }) => {
  const [folderName, setFolderName] = useState('');
  const [error, setError] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      const response = await axios.post('/api/folders', { name: folderName });
      onCreateFolder(response.data);
      setFolderName('');
    } catch (error) {
      setError(error.message);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ maxWidth: '300px', margin: '20px auto', padding: '20px', border: '1px solid #ccc', borderRadius: '10px', boxShadow: '0 0 10px rgba(0, 0, 0, 0.1)' }}>
      <h2>Create New Folder</h2>
      <div style={{ marginBottom: '20px' }}>
        <label htmlFor="folderName" style={{ display: 'block', marginBottom: '10px' }}>Folder Name:</label>
        <input type="text" id="folderName" value={folderName} onChange={(event) => setFolderName(event.target.value)} style={{ width: '100%', height: '40px', padding: '10px', border: '1px solid #ccc', borderRadius: '5px' }} />
      </div>
      {error && <p style={{ color: 'red', marginBottom: '20px' }}>{error}</p>}
      <button type="submit" style={{ width: '100%', height: '40px', backgroundColor: '#4CAF50', color: '#fff', padding: '10px', border: 'none', borderRadius: '5px', cursor: 'pointer' }}>Create Folder</button>
    </form>
  );
};

export default FolderForm;