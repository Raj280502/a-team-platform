import React, { useState } from 'react';
// [auto-removed] import axios from 'axios';  -- file not found
import './InstructionInput.css';

const InstructionInput = ({ recipeId, instruction, setInstruction, addInstruction, updateInstruction }) => {
  const [error, setError] = useState(null);

  const handleInputChange = (e) => {
    setInstruction(e.target.value);
  };

  const handleAddInstruction = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`/api/recipes/${recipeId}/instructions`, { instruction });
      addInstruction(response.data);
      setInstruction('');
    } catch (error) {
      setError(error.message);
    }
  };

  const handleUpdateInstruction = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.put(`/api/recipes/${recipeId}/instructions/${instruction.id}`, { instruction: instruction.text });
      updateInstruction(response.data);
      setInstruction('');
    } catch (error) {
      setError(error.message);
    }
  };

  return (
    <div className="instruction-input">
      <input
        type="text"
        value={instruction}
        onChange={handleInputChange}
        placeholder="Enter instruction"
        style={{ width: '100%', padding: '10px', fontSize: '16px' }}
      />
      {instruction.id ? (
        <button
          onClick={handleUpdateInstruction}
          style={{ backgroundColor: 'green', color: 'white', padding: '10px 20px', border: 'none', borderRadius: '5px', cursor: 'pointer' }}
        >
          Update Instruction
        </button>
      ) : (
        <button
          onClick={handleAddInstruction}
          style={{ backgroundColor: 'blue', color: 'white', padding: '10px 20px', border: 'none', borderRadius: '5px', cursor: 'pointer' }}
        >
          Add Instruction
        </button>
      )}
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
};

export default InstructionInput;