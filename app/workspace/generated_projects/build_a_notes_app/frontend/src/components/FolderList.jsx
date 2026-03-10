import React, { useState, useEffect } from 'react';
// [auto-removed] import axios from 'axios';  -- file not found
import './FolderList.css';

const FolderList = () => {
  const [folders, setFolders] = useState([]);
  const [newFolderName, setNewFolderName] = useState('');
  const [renameFolderId, setRenameFolderId] = useState(null);
  const [renameFolderName, setRenameFolderName] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchFolders = async () => {
      try {
        setLoading(true);
        const response = await axios.get('/api/folders');
        setFolders(response.data);
      } catch (error) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };
    fetchFolders();
  }, []);

  const handleCreateFolder = async (event) => {
    event.preventDefault();
    try {
      const response = await axios.post('/api/folders', { name: newFolderName });
      setFolders([...folders, response.data]);
      setNewFolderName('');
    } catch (error) {
      setError(error.message);
    }
  };

  const handleRenameFolder = async (event, id) => {
    event.preventDefault();
    try {
      const response = await axios.patch(`/api/folders/${id}`, { name: renameFolderName });
      setFolders(folders.map((folder) => folder.id === id ? response.data : folder));
      setRenameFolderId(null);
      setRenameFolderName('');
    } catch (error) {
      setError(error.message);
    }
  };

  const handleDeleteFolder = async (event, id) => {
    event.preventDefault();
    try {
      await axios.delete(`/api/folders/${id}`);
      setFolders(folders.filter((folder) => folder.id !== id));
    } catch (error) {
      setError(error.message);
    }
  };

  return (
    <div className="folder-list">
      <h2>Folders</h2>
      {loading ? (
        <p>Loading...</p>
      ) : (
        <ul>
          {folders.map((folder) => (
            <li key={folder.id}>
              {renameFolderId === folder.id ? (
                <form onSubmit={(event) => handleRenameFolder(event, folder.id)}>
                  <input
                    type="text"
                    value={renameFolderName}
                    onChange={(event) => setRenameFolderName(event.target.value)}
                  />
                  <button type="submit">Rename</button>
                  <button type="button" onClick={() => setRenameFolderId(null)}>Cancel</button>
                </form>
              ) : (
                <div>
                  <span>{folder.name}</span>
                  <button onClick={() => setRenameFolderId(folder.id)}>Rename</button>
                  <button onClick={(event) => handleDeleteFolder(event, folder.id)}>Delete</button>
                </div>
              )}
            </li>
          ))}
        </ul>
      )}
      <form onSubmit={handleCreateFolder}>
        <input
          type="text"
          value={newFolderName}
          onChange={(event) => setNewFolderName(event.target.value)}
          placeholder="New folder name"
        />
        <button type="submit">Create Folder</button>
      </form>
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
};

export default FolderList;