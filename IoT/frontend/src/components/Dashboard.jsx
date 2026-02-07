import { useEffect, useState } from "react";
import { fetchLatestData } from "../services/api";
import "../styles/dashboard.css";

function getAqiInfo(aqi) {
  if (aqi <= 50) return { label: "Good", color: "#2ecc71", gradient: "linear-gradient(135deg, #2ecc71, #27ae60)" };
  if (aqi <= 100) return { label: "Moderate", color: "#f1c40f", gradient: "linear-gradient(135deg, #f1c40f, #f39c12)" };
  if (aqi <= 150) return { label: "Unhealthy (Sensitive)", color: "#e67e22", gradient: "linear-gradient(135deg, #e67e22, #d35400)" };
  if (aqi <= 200) return { label: "Unhealthy", color: "#e74c3c", gradient: "linear-gradient(135deg, #e74c3c, #c0392b)" };
  if (aqi <= 300) return { label: "Very Unhealthy", color: "#8e44ad", gradient: "linear-gradient(135deg, #8e44ad, #71368a)" };
  return { label: "Hazardous", color: "#7f0000", gradient: "linear-gradient(135deg, #7f0000, #5a0000)" };
}

export default function Dashboard() {
  const [data, setData] = useState(null);

  useEffect(() => {
    const loadData = () =>
      fetchLatestData().then(setData).catch(() => {});

    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, []);

  if (!data) return <div className="loading"><div className="spinner"></div>Loading air quality data...</div>;

  const aqiInfo = getAqiInfo(data.aqi);

  const allMetrics = [
    { icon: "🔬", label: "PM1.0", value: data.pm1, unit: "µg/m³", color: "#3b82f6" },
    { icon: "💨", label: "PM2.5", value: data.pm25, unit: "µg/m³", color: "#8b5cf6" },
    { icon: "🌫️", label: "PM10", value: data.pm10, unit: "µg/m³", color: "#ec4899" },
    { icon: "🌡️", label: "Temperature", value: data.temperature, unit: "°C", color: "#f59e0b" },
    { icon: "💧", label: "Humidity", value: data.humidity, unit: "%", color: "#10b981" },
    { icon: "⚗️", label: "Gas", value: data.gas, unit: "KΩ", color: "#06b6d4" }
  ];

  return (
    <div className="container">
      <header className="header">
        <h1 className="title">Aerolytics 🌍</h1>
        <p className="subtitle">Real-time Air Quality Monitoring</p>
      </header>

      <div className="aqi-banner" style={{ background: aqiInfo.gradient }}>
        <div className="aqi-content">
          <div className="aqi-info">
            <span className="aqi-value-large">{data.aqi}</span>
            <span className="aqi-status">{aqiInfo.label}</span>
          </div>
        </div>
      </div>

      <div className="aqi-reference">
        <h3 className="reference-title">📊 AQI Reference Guide</h3>
        <div className="reference-table">
          <div className="reference-row reference-header">
            <div className="reference-cell">AQI Range</div>
            <div className="reference-cell">Air Quality</div>
            <div className="reference-cell">Meaning</div>
          </div>
          <div className="reference-row" style={{ borderLeftColor: '#2ecc71' }}>
            <div className="reference-cell">0 – 50</div>
            <div className="reference-cell">Good</div>
            <div className="reference-cell">Clean air</div>
          </div>
          <div className="reference-row" style={{ borderLeftColor: '#f1c40f' }}>
            <div className="reference-cell">51 – 100</div>
            <div className="reference-cell">Moderate</div>
            <div className="reference-cell">Acceptable</div>
          </div>
          <div className="reference-row" style={{ borderLeftColor: '#e67e22' }}>
            <div className="reference-cell">101 – 150</div>
            <div className="reference-cell">Unhealthy for Sensitive Groups</div>
            <div className="reference-cell">Asthma risk</div>
          </div>
          <div className="reference-row" style={{ borderLeftColor: '#e74c3c' }}>
            <div className="reference-cell">151 – 200</div>
            <div className="reference-cell">Unhealthy</div>
            <div className="reference-cell">Health effects</div>
          </div>
          <div className="reference-row" style={{ borderLeftColor: '#8e44ad' }}>
            <div className="reference-cell">201 – 300</div>
            <div className="reference-cell">Very Unhealthy</div>
            <div className="reference-cell">Serious effects</div>
          </div>
          <div className="reference-row" style={{ borderLeftColor: '#7f0000' }}>
            <div className="reference-cell">301 – 500</div>
            <div className="reference-cell">Hazardous</div>
            <div className="reference-cell">Emergency</div>
          </div>
        </div>
      </div>

      <div className="metrics-grid">
        {allMetrics.map((metric, idx) => (
          <div key={idx} className="metric-card" style={{ borderLeftColor: metric.color }}>
            <div className="metric-header">
              <span className="metric-icon">{metric.icon}</span>
              <span className="metric-label">{metric.label}</span>
            </div>
            <div className="metric-display">
              <span className="metric-number" style={{ color: metric.color }}>{metric.value}</span>
              <span className="metric-unit-text">{metric.unit}</span>
            </div>
          </div>
        ))}
      </div>

      <footer className="footer">
        <div className="updated-info">
          <span className="update-icon">🕐</span>
          <span>Last updated: {new Date(data.created_at).toLocaleString()}</span>
        </div>
        <div className="refresh-indicator">
          <div className="pulse"></div>
          Auto-refreshing every 5 seconds
        </div>
      </footer>
    </div>
  );
}
