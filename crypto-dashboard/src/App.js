import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import { Chart, LineElement, CategoryScale, LinearScale, PointElement, Tooltip, Legend } from 'chart.js';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';

Chart.register(LineElement, CategoryScale, LinearScale, PointElement, Tooltip, Legend);

function App() {
  const [trendData, setTrendData] = useState([]);
  const [crypto, setCrypto] = useState('bitcoin');
  const [startDate, setStartDate] = useState(new Date(new Date().setDate(new Date().getDate() - 7))); // default 7 days ago
  const [endDate, setEndDate] = useState(new Date());

  const fetchData = async () => {
    try {
      const response = await axios.get(`http://127.0.0.1:5000/trends?crypto=${crypto}`);
      console.log('API response:', response.data);
      // Filter data by the selected date range
      const filteredData = response.data.filter(item => {
        const itemDate = new Date(item.created);
        return itemDate >= startDate && itemDate <= endDate;
      });
      setTrendData(filteredData);
    } catch (error) {
      console.error('Error fetching trend data:', error);
    }
  };

  useEffect(() => {
    fetchData();
  }, [crypto, startDate, endDate]);

  // Prepare data for the line chart using compound sentiment score
  const chartData = {
    labels: trendData.map(item => new Date(item.created).toLocaleString()),
    datasets: [
      {
        label: 'Sentiment Compound Score',
        data: trendData.map(item => item.sentiment_compound),
        fill: false,
        backgroundColor: 'rgb(75, 192, 192)',
        borderColor: 'rgba(75, 192, 192, 0.4)',
      },
    ],
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
      <button onClick={fetchData}>Fetch Data</button>
      <div style={{ marginTop: '40px' }}>
        {trendData.length === 0 ? (
          <p>No data available for the selected criteria.</p>
        ) : (
          <Line data={chartData} />
        )}
      </div>
    </div>
  );
}

export default App;
