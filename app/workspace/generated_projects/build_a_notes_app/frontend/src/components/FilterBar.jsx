import React, { useState, useEffect } from 'react';
// [auto-removed] import axios from 'axios';  -- file not found

const FilterBar = (props) => {
  const [skills, setSkills] = useState([]);
  const [experience, setExperience] = useState([]);
  const [education, setEducation] = useState([]);
  const [location, setLocation] = useState([]);
  const [filteredCandidates, setFilteredCandidates] = useState([]);
  const [error, setError] = useState(null);

  const handleSkillChange = (e) => {
    const skill = e.target.value;
    setSkills((prevSkills) => [...prevSkills, skill]);
  };

  const handleExperienceChange = (e) => {
    const exp = e.target.value;
    setExperience((prevExperience) => [...prevExperience, exp]);
  };

  const handleEducationChange = (e) => {
    const edu = e.target.value;
    setEducation((prevEducation) => [...prevEducation, edu]);
  };

  const handleLocationChange = (e) => {
    const loc = e.target.value;
    setLocation((prevLocation) => [...prevLocation, loc]);
  };

  const handleFilter = async () => {
    try {
      const response = await axios.post('/api/candidate-search', {
        skills: skills.join(','),
        experience: experience.join(','),
        education: education.join(','),
        location: location.join(','),
      });
      setFilteredCandidates(response.data);
    } catch (error) {
      setError(error.message);
    }
  };

  return (
    <div style={{ padding: '20px', border: '1px solid #ccc', borderRadius: '10px' }}>
      <h2>Filter Candidates</h2>
      <div style={{ display: 'flex', flexDirection: 'column' }}>
        <label>Skill:</label>
        <select multiple={true} style={{ height: '100px' }} onChange={handleSkillChange}>
          <option value="JavaScript">JavaScript</option>
          <option value="Python">Python</option>
          <option value="Java">Java</option>
        </select>
        <label>Experience:</label>
        <select multiple={true} style={{ height: '100px' }} onChange={handleExperienceChange}>
          <option value="0-2 years">0-2 years</option>
          <option value="2-5 years">2-5 years</option>
          <option value="5-10 years">5-10 years</option>
        </select>
        <label>Education:</label>
        <select multiple={true} style={{ height: '100px' }} onChange={handleEducationChange}>
          <option value="Bachelor's degree">Bachelor's degree</option>
          <option value="Master's degree">Master's degree</option>
          <option value="PhD">PhD</option>
        </select>
        <label>Location:</label>
        <select multiple={true} style={{ height: '100px' }} onChange={handleLocationChange}>
          <option value="New York">New York</option>
          <option value="Los Angeles">Los Angeles</option>
          <option value="Chicago">Chicago</option>
        </select>
        <button style={{ padding: '10px', backgroundColor: '#4CAF50', color: '#fff' }} onClick={handleFilter}>
          Filter
        </button>
      </div>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {filteredCandidates.length > 0 && (
        <div>
          <h2>Filtered Candidates:</h2>
          <ul>
            {filteredCandidates.map((candidate) => (
              <li key={candidate.id}>{candidate.name}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default FilterBar;