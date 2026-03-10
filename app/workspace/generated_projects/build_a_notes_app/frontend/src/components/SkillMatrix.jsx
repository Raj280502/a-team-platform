import React, { useState, useEffect } from 'react';
// [auto-removed] import axios from 'axios';  -- file not found

const SkillMatrix = (props) => {
  const [skills, setSkills] = useState([]);
  const [keywords, setKeywords] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchSkills = async () => {
      setLoading(true);
      try {
        const response = await axios.get('/api/resume-analysis');
        setSkills(response.data.skills);
        setKeywords(response.data.keywords);
      } catch (error) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };
    fetchSkills();
  }, []);

  if (loading) {
    return <div style={{ textAlign: 'center' }}>Loading...</div>;
  }

  if (error) {
    return <div style={{ textAlign: 'center', color: 'red' }}>{error}</div>;
  }

  return (
    <div className="skill-matrix">
      <h2>Skill Matrix</h2>
      <table>
        <thead>
          <tr>
            <th>Skill</th>
            <th>Keywords</th>
          </tr>
        </thead>
        <tbody>
          {skills.map((skill, index) => (
            <tr key={index}>
              <td>{skill.name}</td>
              <td>
                {keywords
                  .filter((keyword) => keyword.skillId === skill.id)
                  .map((keyword, index) => (
                    <span key={index} style={{ marginRight: '10px' }}>
                      {keyword.name}
                    </span>
                  ))}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default SkillMatrix;