import { useState, useEffect } from 'react';
import BoxService from '../services/boxService';
import ConfirmModal from './ConfirmModal';
import { toast } from 'react-toastify';

function BoxesTab() {
  const [boxes, setBoxes] = useState([]);
  const [columnName, setColumnName] = useState('');
  const [rowNumber, setRowNumber] = useState('');
  const [newBoxId, setNewBoxId] = useState(''); // New state for the box ID input field
  const [loading, setLoading] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [boxToDelete, setBoxToDelete] = useState(null);

  useEffect(() => {
    fetchBoxes();
  }, []);

  const fetchBoxes = async () => {
    try {
      setLoading(true);
      const response = await BoxService.getAllBoxes();
      setBoxes(response.data);
    } catch (error) {
      console.error('Error fetching boxes:', error);
      toast.error('Failed to fetch boxes');
    } finally {
      setLoading(false);
    }
  };

  const handleAddBox = async (e) => {
    e.preventDefault();
    
    if (!newBoxId.trim() || !columnName.trim() || !rowNumber) {
      toast.error('Please fill in all fields');
      return;
    }

    // Validate box ID length (since it's VARCHAR(2))
    if (newBoxId.trim().length > 2) {
      toast.error('Box ID must be maximum 2 characters');
      return;
    }

    try {
      setLoading(true);
      const response = await BoxService.createBox({
        boxId: newBoxId.trim(),
        columnName: columnName.trim(),
        rowNumber: parseInt(rowNumber)
      });
      
      toast.success('Box added successfully');
      setNewBoxId('');
      setColumnName('');
      setRowNumber('');
      fetchBoxes();
    } catch (error) {
      console.error('Error adding box:', error);
      // Display more specific error message if available from the API response
      const errorMessage = error.response?.data?.message || 'Failed to add box';
      toast.error(errorMessage);
      setLoading(false);
    }
  };

  const openDeleteModal = (boxId) => {
    setBoxToDelete(boxId);
    setIsDeleteModalOpen(true);
  };

  const closeDeleteModal = () => {
    setIsDeleteModalOpen(false);
    setBoxToDelete(null);
  };

  const handleDeleteBox = async (boxId) => {
    try {
      setLoading(true);
      await BoxService.deleteBox(boxId);
      toast.success('Box deleted successfully');
      fetchBoxes();
    } catch (error) {
      console.error('Error deleting box:', error);
      toast.error('Failed to delete box');
      setLoading(false);
    } finally {
      closeDeleteModal();
    }
  };

  return (
    <div className="box-tab">
      <h2>Boxes Management</h2>
      
      <div className="control-panel">
        <form onSubmit={handleAddBox} className="add-box-form">
          <div className="form-group">
            <label htmlFor="newBoxId">Box ID (max 2 chars):</label>
            <input
              type="text"
              id="newBoxId"
              value={newBoxId}
              onChange={(e) => setNewBoxId(e.target.value)}
              maxLength={2}
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="columnName">Column Name:</label>
            <input
              type="text"
              id="columnName"
              value={columnName}
              onChange={(e) => setColumnName(e.target.value)}
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="rowNumber">Row Number:</label>
            <input
              type="number"
              id="rowNumber"
              value={rowNumber}
              onChange={(e) => setRowNumber(e.target.value)}
              required
            />
          </div>
          
          <button type="submit" disabled={loading}>
            {loading ? 'Adding...' : 'Add Box'}
          </button>
          
          <button type="button" onClick={fetchBoxes} disabled={loading}>
            {loading ? 'Refreshing...' : 'Refresh'}
          </button>
        </form>
      </div>
      
      <div className="box-table-container">
        <table className="box-table">
          <thead>
            <tr>
              <th>Box ID</th>
              <th>Column Name</th>
              <th>Row Number</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan="4" className="loading-cell">Loading...</td>
              </tr>
            ) : boxes.length === 0 ? (
              <tr>
                <td colSpan="4" className="empty-cell">No boxes found</td>
              </tr>
            ) : (
              boxes.map((box) => (
                <tr key={box.box_id}>
                  <td>{box.box_id}</td>
                  <td>{box.column_name}</td>
                  <td>{box.row_number}</td>
                  <td>
                    <button 
                      className="delete-btn"
                      onClick={() => openDeleteModal(box.box_id)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <ConfirmModal
        isOpen={isDeleteModalOpen}
        onClose={closeDeleteModal}
        onConfirm={() => boxToDelete && handleDeleteBox(boxToDelete)}
        title="Delete Box"
      />
    </div>
  );
}

export default BoxesTab;
