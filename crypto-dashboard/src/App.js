// File: src/App.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import { Chart, LineElement, CategoryScale, LinearScale, PointElement, Tooltip, Legend } from 'chart.js';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';

Chart.register(LineElement, CategoryScale, LinearScale, PointElement, Tooltip, Legend);

// Helper function to format a date as YYYY-MM-DD
const formatDate = (date) => new Date(date).toISOString().split('T')[0];

// Group sentiment data by day using the "YYYY-MM-DD" date string as key
const groupSentimentByDay = (data) => {
  const grouped = {};
  data.forEach(item => {
    const day = formatDate(item.created);
    if (!grouped[day]) {
      grouped[day] = [];
    }
    grouped[day].push(item);
  });
  // For each day, select the last data point (you could also average the values)
  const result = Object.keys(grouped).map(day => {
    const items = grouped[day];
    return items[items.length - 1];
  });
  // Sort the results by date
  result.sort((a, b) => new Date(a.created) - new Date(b.created));
  return result;
};

function App() {
  // State for trend (sentiment) data
  const [trendData, setTrendData] = useState([]);
  
  // Selected cryptocurrency and date range
  const [crypto, setCrypto] = useState('bitcoin');
  const [startDate, setStartDate] = useState(new Date(new Date().setDate(new Date().getDate() - 7))); // Default 7 days ago
  const [endDate, setEndDate] = useState(new Date());

  // Fetch sentiment/trend data from our Flask API
  const fetchTrendData = async () => {
    try {
      const response = await axios.get(`http://127.0.0.1:5000/trends?crypto=${crypto}`);
      console.log('Trend API response:', response.data);
      // Filter data by the selected date range
      const filtered = response.data.filter(item => {
        const itemDate = new Date(item.created);
        return itemDate >= startDate && itemDate <= endDate;
      });
      setTrendData(filtered);
    } catch (error) {
      console.error('Error fetching trend data:', error);
    }
  };

  // Fetch data when crypto or date range changes
  useEffect(() => {
    fetchTrendData();
  }, [crypto, startDate, endDate]);

  // Group sentiment data by day
  const dailySentiment = groupSentimentByDay(trendData);

  // Prepare chart data using only sentiment compound scores
  const chartData = {
    labels: dailySentiment.map(item => formatDate(item.created)),
    datasets: [
      {
        label: 'Sentiment Compound Score',
        data: dailySentiment.map(item => item.sentiment_compound),
        fill: false,
        backgroundColor: 'rgb(75, 192, 192)',
        borderColor: 'rgba(75, 192, 192, 0.4)',
      },
    ],
  };

  const options = {
    scales: {
      y: {
        type: 'linear',
        position: 'left',
        title: { display: true, text: 'Sentiment Score' },
        ticks: { beginAtZero: true, suggestedMin: -1, suggestedMax: 1 },
      },
    },
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>Crypto Dashboard</h1>
      <div style={{ marginBottom: '20px' }}>
        <label style={{ marginRight: '10px' }}>Select Cryptocurrency:</label>
        <select value={crypto} onChange={e => setCrypto(e.target.value)}>
          <option value="bitcoin">Bitcoin</option>
          <option value="ethereum">Ethereum</option>
          <option value="solana">Solana</option>
          <option value="dogecoin">Dogecoin</option>
          <option value="cardano">Cardano</option>
          {/* Add more options as needed */}
        </select>
      </div>
      <div style={{ marginBottom: '20px' }}>
        <label style={{ marginRight: '10px' }}>Start Date:</label>
        <DatePicker selected={startDate} onChange={date => setStartDate(date)} />
      </div>
      <div style={{ marginBottom: '20px' }}>
        <label style={{ marginRight: '10px' }}>End Date:</label>
        <DatePicker selected={endDate} onChange={date => setEndDate(date)} />
      </div>
      <button onClick={fetchTrendData}>Fetch Data</button>
      <div style={{ marginTop: '40px' }}>
        {dailySentiment.length === 0 ? (
          <p>No data available for the selected criteria.</p>
        ) : (
          <Line data={chartData} options={options} />
        )}
      </div>
    </div>
  );
}

export default App;
