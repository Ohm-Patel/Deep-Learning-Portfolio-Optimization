import React, { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { TrendingUp, DollarSign, Plus, Minus, Calculator } from 'lucide-react';

const PortfolioOptimizer = () => {
  const DOW30_STOCKS = [
    'AAPL', 'AMGN', 'AMZN', 'AXP', 'BA', 'CAT', 'CRM', 'CSCO', 'CVX', 'DIS',
    'GS', 'HD', 'HON', 'IBM', 'JNJ', 'JPM', 'KO', 'MCD', 'MMM',
    'MRK', 'MSFT', 'NKE', 'NVDA', 'PG', 'SHW', 'TRV', 'UNH', 'VZ', 'V', 'WMT'
  ];

  const PIE_COLORS = [
    '#22c55e', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', 
    '#06b6d4', '#f97316', '#ec4899', '#84cc16', '#6366f1',
    '#14b8a6', '#f472b6', '#a855f7', '#10b981', '#f59e0b'
  ];

  const [selectedStocks, setSelectedStocks] = useState([{ stock: '', weight: '' }]);
  const [totalCapital, setTotalCapital] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const addStock = () => {
    setSelectedStocks([...selectedStocks, { stock: '', weight: '' }]);
  };

  const removeStock = (index) => {
    if (selectedStocks.length > 1) {
      setSelectedStocks(selectedStocks.filter((_, i) => i !== index));
    }
  };

  const updateStock = (index, field, value) => {
    const updated = [...selectedStocks];
    updated[index][field] = value;
    setSelectedStocks(updated);
  };

  const getAvailableStocks = (currentIndex) => {
    const selectedStockSymbols = selectedStocks
      .map((item, index) => index !== currentIndex ? item.stock : null)
      .filter(Boolean);
    return DOW30_STOCKS.filter(stock => !selectedStockSymbols.includes(stock));
  };

  const handleOptimize = async () => {
    setLoading(true);
    setError('');
    
    try {
      // Validate inputs
      const stocksArray = selectedStocks.map(item => item.stock).filter(Boolean);
      if (stocksArray.length === 0) {
        setError('Please select at least one stock');
        setLoading(false);
        return;
      }

      if (!totalCapital || parseFloat(totalCapital) <= 0) {
        setError('Please enter a valid total capital amount');
        setLoading(false);
        return;
      }

      // Check for custom weights
      const hasWeights = selectedStocks.some(item => item.weight !== '');
      let customWeightsArray = null;

      if (hasWeights) {
        customWeightsArray = selectedStocks
          .filter(item => item.stock)
          .map(item => item.weight ? parseFloat(item.weight) : 0);
        
        const weightSum = customWeightsArray.reduce((sum, weight) => sum + weight, 0);
        if (Math.abs(weightSum - 1.0) > 0.01) {
          setError('Custom weights must sum to 1.0');
          setLoading(false);
          return;
        }
      }

      const requestBody = {
        selected_stocks: stocksArray,
        total_capital: parseFloat(totalCapital),
        custom_weights: customWeightsArray
      };

      const response = await fetch('http://localhost:8000/api/portfolio/optimize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      if (data.error) {
        setError(data.error);
      } else {
        setResults(data);
      }
    } catch (err) {
      console.error('Error:', err);
      setError(`Failed to optimize portfolio: ${err.message}`);
    }
    
    setLoading(false);
  };

  const formatGrowthData = (growthData) => {
    if (!growthData || !growthData.optimized) return [];
    const days = growthData.optimized.length;
    return Array.from({ length: days }, (_, i) => ({
      day: i + 1,
      optimized: parseFloat(growthData.optimized[i].toFixed(2)),
      ...(growthData.custom && { custom: parseFloat(growthData.custom[i].toFixed(2)) })
    }));
  };

  const formatAllocationsData = (allocations) => {
    if (!allocations) return [];
    return Object.entries(allocations).map(([stock, weight], index) => ({
      stock,
      amount: Math.round(weight * parseFloat(totalCapital)),
      percentage: (weight * 100).toFixed(1),
      color: PIE_COLORS[index % PIE_COLORS.length]
    }));
  };

  // Custom tooltip content for pie chart
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div style={{
          backgroundColor: '#111827',
          border: '1px solid #374151',
          borderRadius: '6px',
          padding: '8px 12px',
          color: '#ffffff'
        }}>
          <p style={{ margin: 0, fontSize: '14px' }}>
            {`${data.stock}: ${data.percentage}% (${data.amount.toLocaleString()})`}
          </p>
        </div>
      );
    }
    return null;
  };

  // Custom label function for pie chart
  const renderCustomizedLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent, payload }) => {
    const RADIAN = Math.PI / 180;
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);

    if (percent < 0.08) return null;

    return (
      <text 
        x={x} 
        y={y} 
        fill="#ffffff" 
        textAnchor={x > cx ? 'start' : 'end'} 
        dominantBaseline="central"
        fontSize={12}
        fontWeight="600"
      >
        {payload.stock}
      </text>
    );
  };

  const chartData = results ? formatGrowthData(results.growth_data) : [];
  const allocationData = results ? formatAllocationsData(results.allocations) : [];

  // CSS Styles
  const styles = {
    container: {
      minHeight: '100vh',
      backgroundColor: '#000000',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
      width: '100%',
      overflowX: 'hidden'
    },
    wrapper: {
      maxWidth: '1400px',
      margin: '0 auto',
      padding: 'clamp(16px, 2vw, 32px)'
    },
    header: {
      textAlign: 'center',
      marginBottom: '32px'
    },
    title: {
      fontSize: 'clamp(2rem, 5vw, 3rem)',
      fontWeight: '700',
      color: '#ffffff',
      marginBottom: '16px',
      letterSpacing: '0.025em'
    },
    subtitle: {
      fontSize: '1rem',
      color: '#9ca3af',
      maxWidth: '512px',
      margin: '0 auto'
    },
    inputSection: {
      backgroundColor: '#0c0c0c',
      border: '1px solid #374151',
      borderRadius: '8px',
      padding: '32px',
      marginBottom: '32px'
    },
    gridLg: {
      display: 'grid',
      gridTemplateColumns: '1fr 1fr',
      gap: '32px'
    },
    stockSectionHeader: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      marginBottom: '16px',
      flexWrap: 'wrap',
      gap: '8px'
    },
    sectionTitle: {
      fontSize: '1.125rem',
      fontWeight: '500',
      color: '#ffffff'
    },
    addButton: {
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      padding: '8px 16px',
      backgroundColor: '#22c55e',
      color: '#000000',
      fontWeight: '500',
      border: 'none',
      borderRadius: '6px',
      cursor: 'pointer',
      transition: 'background-color 0.2s',
      fontSize: '14px'
    },
    stockList: {
      maxHeight: '280px',
      overflowY: 'auto',
      marginBottom: '16px'
    },
    stockRow: {
      display: 'flex',
      alignItems: 'center',
      gap: '12px',
      padding: '12px',
      backgroundColor: '#111827',
      borderRadius: '6px',
      border: '1px solid #374151',
      marginBottom: '12px'
    },
    selectInput: {
      flex: '1',
      padding: '8px 12px',
      backgroundColor: '#000000',
      border: '1px solid #374151',
      color: '#ffffff',
      borderRadius: '6px',
      fontSize: '14px',
      outline: 'none',
      minWidth: '120px'
    },
    weightInput: {
      width: '80px',
      padding: '8px 12px',
      backgroundColor: '#000000',
      border: '1px solid #374151',
      color: '#ffffff',
      borderRadius: '6px',
      fontSize: '14px',
      outline: 'none'
    },
    removeButton: {
      padding: '8px',
      color: '#ef4444',
      backgroundColor: 'transparent',
      border: 'none',
      cursor: 'pointer',
      borderRadius: '4px',
      transition: 'color 0.2s'
    },
    helpText: {
      color: '#6b7280',
      fontSize: '0.875rem'
    },
    formGroup: {
      marginBottom: '24px'
    },
    label: {
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      color: '#ffffff',
      fontWeight: '500',
      marginBottom: '12px'
    },
    textInput: {
      width: '100%',
      padding: '12px 16px',
      backgroundColor: '#000000',
      border: '1px solid #374151',
      color: '#ffffff',
      borderRadius: '6px',
      fontSize: '16px',
      outline: 'none'
    },
    optimizeButton: {
      width: '100%',
      backgroundColor: '#22c55e',
      color: '#000000',
      fontWeight: '500',
      padding: '12px 24px',
      border: 'none',
      borderRadius: '6px',
      cursor: 'pointer',
      transition: 'background-color 0.2s',
      fontSize: '16px'
    },
    summary: {
      backgroundColor: '#111827',
      borderRadius: '6px',
      padding: '16px',
      border: '1px solid #374151',
      marginTop: '16px'
    },
    summaryTitle: {
      color: '#ffffff',
      fontWeight: '500',
      marginBottom: '12px'
    },
    summaryRow: {
      display: 'flex',
      justifyContent: 'space-between',
      color: '#9ca3af',
      fontSize: '0.875rem',
      marginBottom: '8px'
    },
    errorBox: {
      marginTop: '16px',
      padding: '16px',
      backgroundColor: '#7f1d1d',
      border: '1px solid #dc2626',
      borderRadius: '6px',
      color: '#fca5a5'
    },
    resultsSection: {
      marginTop: '32px'
    },
    chartContainer: {
      backgroundColor: '#0c0c0c',
      border: '1px solid #374151',
      borderRadius: '8px',
      padding: '24px',
      marginBottom: '32px'
    },
    chartTitle: {
      display: 'flex',
      alignItems: 'center',
      gap: '12px',
      fontSize: '1.25rem',
      fontWeight: '500',
      color: '#ffffff',
      marginBottom: '24px'
    },
    chartWrapper: {
      height: '320px'
    },
    pieChartWrapper: {
      height: '280px'
    },
    noData: {
      height: '320px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      color: '#6b7280'
    },
    gridMd: {
      display: 'grid',
      gridTemplateColumns: '1fr 1fr',
      gap: '32px'
    },
    allocationList: {
      marginBottom: '20px'
    },
    allocationItem: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '12px',
      backgroundColor: '#111827',
      borderRadius: '6px',
      border: '1px solid #374151',
      marginBottom: '8px'
    },
    stockInfo: {
      display: 'flex',
      alignItems: 'center',
      gap: '12px'
    },
    dot: {
      width: '8px',
      height: '8px',
      borderRadius: '50%'
    },
    stockSymbol: {
      fontWeight: '500',
      color: '#ffffff'
    },
    amountInfo: {
      textAlign: 'right'
    },
    amount: {
      fontSize: '1rem',
      fontWeight: '500',
      color: '#ffffff'
    },
    percentage: {
      fontSize: '0.875rem',
      color: '#9ca3af'
    },
    totalSection: {
      marginTop: '16px',
      paddingTop: '16px',
      borderTop: '1px solid #374151',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center'
    },
    totalLabel: {
      fontSize: '1rem',
      fontWeight: '500',
      color: '#ffffff'
    },
    totalAmount: {
      fontSize: '1.125rem',
      fontWeight: '500',
      color: '#22c55e'
    },
    spinner: {
      width: '16px',
      height: '16px',
      border: '2px solid #9ca3af',
      borderTop: '2px solid #000000',
      borderRadius: '50%',
      animation: 'spin 1s linear infinite'
    }
  };

  return (
    <div className="full-viewport" style={styles.container}>
      <style>{`
          /* Global fit/reset so the app uses the full screen */
          html, body, #root { width: 100%; max-width: 100%; height: 100%; margin: 0; padding: 0; background:#000; }
          *, *::before, *::after { box-sizing: border-box; }
          :root { color-scheme: dark; }

          @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
          
          input:focus, select:focus {
            border-color: #22c55e !important;
            box-shadow: 0 0 0 2px rgba(34, 197, 94, 0.2) !important;
          }
          button:hover { opacity: 0.9; }
          button:disabled { background-color: #374151 !important; color: #9ca3af !important; cursor: not-allowed !important; }
          option { background-color: #000000; color: #ffffff; }

          .recharts-tooltip-wrapper .recharts-default-tooltip { background-color: #111827 !important; border: 1px solid #374151 !important; border-radius: 6px !important; color: #ffffff !important; }
          .recharts-tooltip-wrapper .recharts-tooltip-label,
          .recharts-tooltip-wrapper .recharts-tooltip-item-name,
          .recharts-tooltip-wrapper .recharts-tooltip-item-value { color: #ffffff !important; }
          .recharts-legend-wrapper .recharts-legend-item-text { color: #ffffff !important; }

          /* RESPONSIVE LAYOUT FIXES */
          /* collapse two-column grids earlier so they don't overflow on laptops */
          @media (max-width: 1100px) {
            .grid-responsive { grid-template-columns: 1fr !important; }
          }
          @media (max-width: 768px) {
            .mobile-stack { flex-direction: column; align-items: stretch !important; }
            .mobile-stack button { margin-top: 8px; }
            .grid-responsive { grid-template-columns: 1fr !important; }
          }
        `}
      </style>
      
      <div style={styles.wrapper}>
        {/* Header */}
        <div style={styles.header}>
          <h1 style={styles.title}>Portfolio Optimizer</h1>
          <p style={styles.subtitle}>
            Invest smarter with LSTM-powered portfolio optimization
          </p>
        </div>

        {/* Input Section */}
        <div style={styles.inputSection}>
          {/* IMPORTANT: className must be separate from style for media queries to work */}
          <div className="grid-responsive" style={styles.gridLg}>
            {/* Stock Selection */}
            <div>
              <div className="mobile-stack" style={styles.stockSectionHeader}>
                <h3 style={styles.sectionTitle}>Select Stocks</h3>
                <button onClick={addStock} style={styles.addButton}>
                  <Plus size={16} />
                  Add Stock
                </button>
              </div>
              
              <div style={styles.stockList}>
                {selectedStocks.map((item, index) => (
                  <div key={index} style={styles.stockRow}>
                    <select
                      value={item.stock}
                      onChange={(e) => updateStock(index, 'stock', e.target.value)}
                      style={styles.selectInput}
                    >
                      <option value="">Select Stock</option>
                      {getAvailableStocks(index).map(stock => (
                        <option key={stock} value={stock}>{stock}</option>
                      ))}
                    </select>
                    
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      max="1"
                      placeholder="Weight"
                      value={item.weight}
                      onChange={(e) => updateStock(index, 'weight', e.target.value)}
                      style={styles.weightInput}
                    />
                    
                    <button
                      onClick={() => removeStock(index)}
                      disabled={selectedStocks.length === 1}
                      style={styles.removeButton}
                    >
                      <Minus size={16} />
                    </button>
                  </div>
                ))}
              </div>
              
              <p style={styles.helpText}>
                Optional: enter values that sum to 1.0 to compare your portfolio to the optimal portfolio
              </p>
            </div>

            {/* Capital and Controls */}
            <div>
              <div style={styles.formGroup}>
                <label style={styles.label}>
                  <DollarSign size={20} />
                  Total Capital
                </label>
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  value={totalCapital}
                  onChange={(e) => setTotalCapital(e.target.value)}
                  placeholder="10000"
                  style={styles.textInput}
                />
              </div>

              <button
                onClick={handleOptimize}
                disabled={loading}
                style={styles.optimizeButton}
              >
                {loading ? (
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                    <div style={styles.spinner}></div>
                    Running Simulations (May Take A While)...
                  </div>
                ) : (
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                    <Calculator size={16} />
                    Optimize Portfolio
                  </div>
                )}
              </button>

              {/* Summary */}
              <div style={styles.summary}>
                <h4 style={styles.summaryTitle}>Summary</h4>
                <div style={styles.summaryRow}>
                  <span>Selected Stocks:</span>
                  <span>{selectedStocks.filter(item => item.stock).length}</span>
                </div>
                <div style={styles.summaryRow}>
                  <span>Capital:</span>
                  <span>${totalCapital ? parseFloat(totalCapital).toLocaleString() : '0'}</span>
                </div>
                <div style={styles.summaryRow}>
                  <span>Weights:</span>
                  <span>{selectedStocks.some(item => item.weight) ? 'Custom' : 'Auto'}</span>
                </div>
              </div>
            </div>
          </div>

          {error && (
            <div style={styles.errorBox}>
              <p>{error}</p>
            </div>
          )}
        </div>

        {/* Results */}
        {results && (
          <div style={styles.resultsSection}>
            {/* Portfolio Growth Chart */}
            <div style={styles.chartContainer}>
              <h2 style={styles.chartTitle}>
                <TrendingUp size={24} color="#22c55e" />
                Expected Portfolio Growth (75 Days)
              </h2>
              {chartData.length > 0 ? (
                <div style={styles.chartWrapper}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                      <XAxis 
                        dataKey="day" 
                        stroke="#9CA3AF"
                        fontSize={12}
                        axisLine={{ stroke: '#4B5563' }}
                        tickLine={{ stroke: '#4B5563' }}
                      />
                      <YAxis 
                        stroke="#9CA3AF"
                        fontSize={12}
                        tickFormatter={(value) => `${value.toFixed(1)}%`}
                        axisLine={{ stroke: '#4B5563' }}
                        tickLine={{ stroke: '#4B5563' }}
                      />
                      <Tooltip 
                        contentStyle={{
                          backgroundColor: '#111827',
                          border: '1px solid #374151',
                          borderRadius: '6px',
                          color: '#F9FAFB'
                        }}
                        formatter={(value, name) => [`${value.toFixed(2)}%`, name]}
                      />
                      <Legend />
                      <Line 
                        type="monotone" 
                        dataKey="optimized" 
                        stroke="#22C55E" 
                        strokeWidth={2}
                        name="Optimized Portfolio"
                        dot={false}
                      />
                      {chartData[0]?.custom !== undefined && (
                        <Line 
                          type="monotone" 
                          dataKey="custom" 
                          stroke="#F59E0B" 
                          strokeWidth={2}
                          name="Custom Portfolio"
                          dot={false}
                          strokeDasharray="2 2"
                        />
                      )}
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div style={styles.noData}>
                  <p>No chart data available</p>
                </div>
              )}
            </div>

            {/* Capital Allocation */}
            <div className="grid-responsive" style={styles.gridMd}>
              {/* Allocation Pie Chart */}
              <div style={styles.chartContainer}>
                <h3 style={styles.chartTitle}>
                  <DollarSign size={20} color="#22c55e" />
                  Capital Allocation
                </h3>
                {allocationData.length > 0 ? (
                  <div style={styles.pieChartWrapper}>
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={allocationData}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={renderCustomizedLabel}
                          outerRadius={100}
                          fill="#8884d8"
                          stroke="#636363"
                          dataKey="amount"
                        >
                          {allocationData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip 
                          contentStyle={{
                            backgroundColor: '#111827',
                            border: '1px solid #374151',
                            borderRadius: '6px',
                            color: '#ffffff'
                          }}
                          labelStyle={{
                            color: '#ffffff'
                          }}
                          formatter={(value, name, props) => [
                            `${props.payload.stock}: ${props.payload.percentage}% ($${value.toLocaleString()})`,
                            ''
                          ]}
                        />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                ) : (
                  <div style={styles.noData}>
                    <p>No allocation data available</p>
                  </div>
                )}
              </div>

              {/* Allocation Details */}
              <div style={styles.chartContainer}>
                <h3 style={styles.sectionTitle}>Investment Breakdown</h3>
                <div style={styles.allocationList}>
                  {allocationData.map(({ stock, amount, percentage, color }) => (
                    <div key={stock} style={styles.allocationItem}>
                      <div style={styles.stockInfo}>
                        <div style={{...styles.dot, backgroundColor: color}}></div>
                        <span style={styles.stockSymbol}>{stock}</span>
                      </div>
                      <div style={styles.amountInfo}>
                        <div style={styles.amount}>
                          ${amount.toLocaleString()}
                        </div>
                        <div style={styles.percentage}>
                          {percentage}%
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                
                <div style={styles.totalSection}>
                  <span style={styles.totalLabel}>Total Capital:</span>
                  <span style={styles.totalAmount}>
                    ${parseFloat(totalCapital || 0).toLocaleString()}
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PortfolioOptimizer;
