import React, { useState, useEffect } from 'react';
// [auto-removed] import axios from 'axios';  -- file not found
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const MatchScoreChart = ({ jobId, resumeId }) => {
  const [matchScores, setMatchScores] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchMatchScores = async () => {
      setLoading(true);
      try {
        const response = await axios.get(`/api/resume-analysis`, {
          params: { jobId, resumeId },
        });
        setMatchScores(response.data.matchScores);
      } catch (error) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };
    fetchMatchScores();
  }, [jobId, resumeId]);

  const chartData = {
    labels: matchScores.map((score) => score.category),
    datasets: [
      {
        label: 'Match Scores',
        data: matchScores.map((score) => score.score),
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Match Scores Chart',
      },
    },
  };

  if (loading) {
    return <div style={{ textAlign: 'center' }}>Loading...</div>;
  }

  if (error) {
    return <div style={{ textAlign: 'center', color: 'red' }}>{error}</div>;
  }

  return (
    <div style={{ width: '80%', margin: '40px auto' }}>
      <Line options={chartOptions} data={chartData} />
    </div>
  );
};

export default MatchScoreChart;