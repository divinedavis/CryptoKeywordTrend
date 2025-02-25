// File: src/App.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import { Chart, LineElement, CategoryScale, LinearScale, PointElement, Tooltip, Legend } from 'chart.js';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';

Chart.register(LineElement, CategoryScale, LinearScale, PointElement, Tooltip, Legend);

// Helper function to format a date as YYYY-MM-DD
const formatDate = (date) => {
  return new Date(date).toISOString().split('T')[0];
};

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
  // For each day, select the last data point (or compute an average if desired)
  const result = Object.keys(grouped).map(day => {
    const items = grouped[day];
    return items[items.length - 1];
  });
  // Sort the results by day
  result.sort((a, b) => new Date(a.created) - new Date(b.created));
  return result;
};

// Group price data (from CoinGecko) by day; for each day take the last price value
const groupPriceByDay = (prices) => {
  const grouped = {};
  prices.forEach(point => {
    const day = formatDate(point[0]);
    grouped[day] = point[1]; // Last available price for that day
  });
  const days = Object.keys(grouped).sort((a, b) => new Date(a) - new Date(b));
  const priceValues = days.map(day => grouped[day]);
  return { days, priceValues };
};

function App() {
  // State for trend (sentiment) data and price data
  const [trendData, setTrendData] = useState([]);
  const [priceData, setPriceData] = useState({ days: [], priceValues: [] });
  
  // Selected cryptocurrency
  const [crypto, setCrypto] = useState('bitcoin');

  // Default date range.
  // Change these defaults to test with January data if needed.
  // For example, to see January 2025 data, use:
  // const [startDate, setStartDate] = useState(new Date('2025-01-01'));
  // const [endDate, setEndDate] = useState(new Date('2025-01-31'));
  const [startDate, setStartDate] = useState(new Date(new Date().setDate(new Date().getDate() - 7)));
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

  // Fetch historical price data from CoinGecko
  const fetchPriceData = async () => {
    try {
      const diffTime = Math.abs(endDate - startDate);
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      const priceResponse = await axios.get(`https://api.coingecko.com/api/v3/coins/${crypto}/market_chart`, {
        params: {
          vs_currency: 'usd',
          days: diffDays
        }
      });
      const prices = priceResponse.data.prices;
      const groupedPrices = groupPriceByDay(prices);
      setPriceData(groupedPrices);
      console.log('Price API response:', priceResponse.data);
    } catch (error) {
      console.error('Error fetching price data:', error);
    }
  };

  // Fetch both trend and price data whenever crypto or date range changes
  const fetchData = async () => {
    await fetchTrendData();
    await fetchPriceData();
  };

  useEffect(() => {
    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [crypto, startDate, endDate]);

  // Group sentiment data by day
  const dailySentiment = groupSentimentByDay(trendData);

  // Use the price data days for labels if available; otherwise use sentiment dates.
  const labels = priceData.days.length > 0 ? priceData.days : dailySentiment.map(item => formatDate(item.created));

  const chartData = {
    labels,
    datasets: [
      {
        label: 'Sentiment Compound Score',
        data: dailySentiment.map(item => item.sentiment_compound),
        fill: false,
        backgroundColor: 'rgb(75, 192, 192)',
        borderColor: 'rgba(75, 192, 192, 0.4)',
        yAxisID: 'y',
      },
      {
        label: 'Price (USD)',
        data: priceData.priceValues,
        fill: false,
        backgroundColor: 'rgb(255, 99, 132)',
        borderColor: 'rgba(255, 99, 132, 0.4)',
        yAxisID: 'y1',
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
      y1: {
        type: 'linear',
        position: 'right',
        title: { display: true, text: 'Price (USD)' },
        grid: { drawOnChartArea: false },
      },
    },
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>Crypto Dashboard</h1>
      <div style={{ marginBottom: '20px' }}>
        <label style={{ marginRight: '10px' }}>Select Cryptocurrency:</label>
        <select value={crypto} onChange={(e) => setCrypto(e.target.value)}>
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
        {labels.length === 0 ? (
          <p>No data available for the selected criteria.</p>
        ) : (
          <Line data={chartData} options={options} />
        )}
      </div>
    </div>
  );
}

export default App;
