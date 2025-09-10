import { useState, useEffect } from 'react';
import '../index.css';

function ConfirmModal({ isOpen, onClose, onConfirm, title = 'Confirm Delete' }) {
  const [confirmText, setConfirmText] = useState('');
  const [isValid, setIsValid] = useState(false);

  useEffect(() => {
    // Reset state when modal opens
    if (isOpen) {
      setConfirmText('');
      setIsValid(false);
    }
  }, [isOpen]);

  const handleConfirmTextChange = (e) => {
    const value = e.target.value;
    setConfirmText(value);
    setIsValid(value.trim() === 'CONFIRM');
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (isValid) {
      onConfirm();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-container">
        <div className="modal-header">
          <h3>{title}</h3>
          <button className="modal-close-btn" onClick={onClose}>×</button>
        </div>
        <div className="modal-body">
          <p>This action cannot be undone. Please type <strong>CONFIRM</strong> to proceed.</p>
          <form onSubmit={handleSubmit}>
            <input
              type="text"
              value={confirmText}
              onChange={handleConfirmTextChange}
              placeholder="Type CONFIRM here"
              className="confirm-input"
              autoFocus
            />
            <div className="modal-footer">
              <button type="button" className="cancel-btn" onClick={onClose}>
                Cancel
              </button>
              <button 
                type="submit" 
                className={`confirm-btn ${isValid ? 'active' : 'disabled'}`}
                disabled={!isValid}
              >
                Delete
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default ConfirmModal;
