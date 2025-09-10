import { useState, useEffect, useRef } from 'react';
import TransactionService from '../services/transactionService';
import { toast } from 'react-toastify';

function TransactionsTab() {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sortOption, setSortOption] = useState('id_asc');
  const [autoRefresh, setAutoRefresh] = useState(false);
  const autoRefreshTimerRef = useRef(null);

  useEffect(() => {
    fetchTransactions();
    
    return () => {
      // Clean up timer on unmount
      if (autoRefreshTimerRef.current) {
        clearInterval(autoRefreshTimerRef.current);
      }
    };
  }, []);

  useEffect(() => {
    // Set up or clear auto-refresh timer when autoRefresh state changes
    if (autoRefresh) {
      autoRefreshTimerRef.current = setInterval(fetchTransactions, 5000);
    } else if (autoRefreshTimerRef.current) {
      clearInterval(autoRefreshTimerRef.current);
      autoRefreshTimerRef.current = null;
    }
    
    return () => {
      if (autoRefreshTimerRef.current) {
        clearInterval(autoRefreshTimerRef.current);
      }
    };
  }, [autoRefresh]);

  // Refetch when sort option changes
  useEffect(() => {
    fetchTransactions();
  }, [sortOption]);

  const fetchTransactions = async () => {
    try {
      setLoading(true);
      const response = await TransactionService.getAllTransactions(sortOption);
      setTransactions(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching transactions:', error);
      toast.error('Failed to fetch transactions');
      setLoading(false);
    }
  };

  const handleSortChange = (e) => {
    setSortOption(e.target.value);
  };

  const toggleAutoRefresh = () => {
    setAutoRefresh(prev => !prev);
    if (!autoRefresh) {
      toast.info('Auto-refresh activated (5s)');
    }
  };

  const formatDateTime = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="transactions-tab">
      <h2>Transactions</h2>
      
      <div className="control-panel">
        <div className="transaction-controls">
          <div className="sort-control">
            <label htmlFor="sortOption">Sort By:</label>
            <select
              id="sortOption"
              value={sortOption}
              onChange={handleSortChange}
              disabled={loading}
            >
              <option value="id_asc">Transaction ID (asc)</option>
              <option value="newest_first">Newest First</option>
              <option value="added_only">Added Only</option>
              <option value="retrieved_only">Retrieved Only</option>
            </select>
          </div>
          
          <div className="refresh-control">
            <button 
              onClick={fetchTransactions} 
              disabled={loading}
              className="refresh-button"
            >
              {loading ? 'Refreshing...' : 'Refresh'}
            </button>
            
            <div className="auto-refresh-control">
              <input
                type="checkbox"
                id="autoRefresh"
                checked={autoRefresh}
                onChange={toggleAutoRefresh}
              />
              <label htmlFor="autoRefresh">Auto Refresh (5s)</label>
            </div>
          </div>
        </div>
      </div>
      
      <div className="transaction-table-container">
        <table className="transaction-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Item</th>
              <th>Location</th>
              <th>Action</th>
              <th>Time</th>
            </tr>
          </thead>
          <tbody>
            {loading && transactions.length === 0 ? (
              <tr>
                <td colSpan="5" className="loading-cell">Loading...</td>
              </tr>
            ) : transactions.length === 0 ? (
              <tr>
                <td colSpan="5" className="empty-cell">No transactions found</td>
              </tr>
            ) : (
              transactions.map((transaction) => (
                <tr key={transaction.tran_id}>
                  <td>{transaction.tran_id}</td>
                  <td>{transaction.item_name || 'Unknown'}</td>
                  <td>{transaction.subcom_place || 'N/A'}</td>
                  <td>
                    <span className={`action-badge ${transaction.action}`}>
                      {transaction.action}
                    </span>
                  </td>
                  <td>{formatDateTime(transaction.time)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default TransactionsTab;
