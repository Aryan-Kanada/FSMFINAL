import { useState, useEffect } from 'react';
import ItemService from '../services/itemService';
import BoxService from '../services/boxService';
import SubCompartmentService from '../services/subCompartmentService';
import { toast } from 'react-toastify';

function OperationsTab() {
  const [activeOperation, setActiveOperation] = useState(null);
  const [items, setItems] = useState([]);
  const [boxes, setBoxes] = useState([]);
  const [availableBoxes, setAvailableBoxes] = useState([]);
  const [selectedItem, setSelectedItem] = useState('');
  const [selectedBox, setSelectedBox] = useState('');
  const [subId, setSubId] = useState('');
  const [quantity, setQuantity] = useState(1);
  const [availableItems, setAvailableItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  useEffect(() => {
    fetchItems();
    fetchBoxes();
    fetchAvailableItems();
  }, []);

  const fetchItems = async () => {
    try {
      const response = await ItemService.getAllItems();
      setItems(response.data);
    } catch (error) {
      console.error('Error fetching items:', error);
      toast.error('Failed to load items');
    }
  };

  const fetchBoxes = async () => {
    try {
      const response = await BoxService.getAllBoxes();
      setBoxes(response.data);
    } catch (error) {
      console.error('Error fetching boxes:', error);
      toast.error('Failed to load boxes');
    }
  };
  
  const fetchAvailableBoxes = async () => {
    try {
      const response = await BoxService.getBoxesWithEmptyCompartments();
      setAvailableBoxes(response.data);
    } catch (error) {
      console.error('Error fetching available boxes:', error);
      toast.error('Failed to load available boxes');
    }
  };

  const fetchAvailableItems = async () => {
    try {
      const response = await ItemService.getAvailableItems();
      setAvailableItems(response.data);
    } catch (error) {
      console.error('Error fetching available items:', error);
    }
  };

  const showAddProductOptions = () => {
    setActiveOperation('add');
    setResult(null);
    fetchAvailableBoxes(); // Fetch boxes with empty compartments when selecting add operation
  };

  const showRetrieveProductOptions = () => {
    setActiveOperation('retrieve');
    fetchAvailableItems();
    setResult(null);
  };

  const showItemLocationsOptions = () => {
    setActiveOperation('locations');
    setResult(null);
  };

  const handleAddProduct = async (e) => {
    e.preventDefault();
    
    if (!selectedItem || !selectedBox || !subId) {
      toast.error('Please fill in all required fields');
      return;
    }

    try {
      setLoading(true);
      // Convert values properly to ensure they match the expected types
      const payload = {
        itemId: Number(selectedItem),
        boxId: selectedBox,
        subId: subId.toString()
      };
      
      console.log('Sending payload:', payload); // Debug the payload
      
      const response = await SubCompartmentService.addProduct(payload);
      
      // Get item name for the result display
      const itemName = items.find(item => item.item_id === Number(selectedItem))?.name || 'Unknown';
      
      setResult({
        success: true,
        message: 'Product added successfully!',
        details: {
          item: itemName,
          location: `${selectedBox}${subId}`,
          status: 'Occupied',
          action: response.data.action
        }
      });
      
      toast.success('Product added successfully');
      
      // Reset form fields
      setSubId('');
      setSelectedBox('');
      
      // Refresh available boxes after adding a product
      fetchAvailableBoxes();
      
      setLoading(false);
    } catch (error) {
      console.error('Error adding product:', error);
      setResult({
        success: false,
        message: `Failed to add product: ${error.response?.data?.error || error.message}`
      });
      toast.error(`Failed to add product: ${error.response?.data?.error || error.message}`);
      setLoading(false);
    }
  };

  const handleRetrieveProduct = async (e) => {
    e.preventDefault();
    
    if (!selectedItem || !quantity || quantity < 1) {
      toast.error('Please select an item and enter a valid quantity');
      return;
    }

    try {
      setLoading(true);
      const response = await SubCompartmentService.retrieveProduct({
        itemId: parseInt(selectedItem),
        quantity: parseInt(quantity)
      });
      
      // Get item name for the result display
      const itemName = items.find(item => item.item_id === parseInt(selectedItem))?.name || 'Unknown';
      
      setResult({
        success: true,
        message: `Successfully retrieved ${quantity} item(s)!`,
        details: {
          item: itemName,
          quantity: response.data.quantity,
          locations: response.data.locations.map(loc => ({
            place: loc.subcom_place,
            displayLoc: `${loc.column_name}${loc.row_number}${loc.sub_id}`
          }))
        }
      });
      
      toast.success(`Successfully retrieved ${quantity} item(s)!`);
      setLoading(false);
      
      // Refresh available items
      fetchAvailableItems();
    } catch (error) {
      console.error('Error retrieving product:', error);
      setResult({
        success: false,
        message: `Failed to retrieve product: ${error.response?.data?.message || error.message}`
      });
      toast.error(`Error: ${error.response?.data?.message || error.message}`);
      setLoading(false);
    }
  };

  const fetchItemLocations = async (e) => {
    e.preventDefault();
    
    if (!selectedItem) {
      toast.error('Please select an item');
      return;
    }

    try {
      setLoading(true);
      const response = await ItemService.getItemLocations(selectedItem);
      const itemName = items.find(item => item.item_id === parseInt(selectedItem))?.name || 'Unknown';
      
      if (response.data.length === 0) {
        setResult({
          success: true,
          message: `No locations found for ${itemName}`,
          details: { 
            item: itemName,
            count: 0,
            locations: []
          }
        });
      } else {
        setResult({
          success: true,
          message: `Found ${response.data.length} location(s) for ${itemName}`,
          details: { 
            item: itemName,
            count: response.data.length,
            locations: response.data.map(loc => ({
              place: loc.subcom_place,
              displayLoc: `${loc.column_name}${loc.row_number}${loc.sub_id}`
            }))
          }
        });
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Error fetching item locations:', error);
      setResult({
        success: false,
        message: `Failed to fetch locations: ${error.response?.data?.message || error.message}`
      });
      toast.error(`Error: ${error.response?.data?.message || error.message}`);
      setLoading(false);
    }
  };

  const renderOptions = () => {
    switch (activeOperation) {
      case 'add':
        return (
          <form onSubmit={handleAddProduct} className="operation-form">
            <h3>Add Product Options</h3>
            
            <div className="form-group">
              <label htmlFor="productType">Select Product Type:</label>
              <select
                id="productType"
                value={selectedItem}
                onChange={(e) => setSelectedItem(e.target.value)}
                required
              >
                <option value="">Select Product</option>
                {items.map((item) => (
                  <option key={item.item_id} value={item.item_id}>
                    {item.name} (ID: {item.item_id})
                  </option>
                ))}
              </select>
            </div>
            
            <div className="form-group">
              <label htmlFor="boxId">Box ID:</label>
              <select
                id="boxId"
                value={selectedBox}
                onChange={(e) => setSelectedBox(e.target.value)}
                required
              >
                <option value="">Select Box</option>
                {availableBoxes.map((box) => (
                  <option key={box.box_id} value={box.box_id}>
                    {box.column_name}{box.row_number}
                  </option>
                ))}
              </select>
            </div>
            
            <div className="form-group">
              <label htmlFor="subCompartmentId">Sub Compartment ID:</label>
              <input
                type="text"
                id="subCompartmentId"
                value={subId}
                onChange={(e) => setSubId(e.target.value)}
                placeholder="e.g., a, b"
                required
              />
            </div>
            
            <button type="submit" disabled={loading}>
              {loading ? 'Processing...' : 'Add Product to Storage'}
            </button>
          </form>
        );
        
      case 'retrieve':
        return (
          <form onSubmit={handleRetrieveProduct} className="operation-form">
            <h3>Retrieve Product Options</h3>
            
            {availableItems.length === 0 ? (
              <p>No products available for retrieval.</p>
            ) : (
              <>
                <div className="form-group">
                  <label htmlFor="retrieveProduct">Select Product Type to Retrieve:</label>
                  {availableItems.map((item) => (
                    <div className="radio-option" key={item.item_id}>
                      <input
                        type="radio"
                        id={`product-${item.item_id}`}
                        name="retrieveProduct"
                        value={item.item_id}
                        onChange={() => setSelectedItem(item.item_id)}
                        required
                      />
                      <label htmlFor={`product-${item.item_id}`}>
                        {item.name} (Available: {item.available_count})
                      </label>
                    </div>
                  ))}
                </div>
                
                <div className="form-group">
                  <label htmlFor="quantity">Quantity to Retrieve:</label>
                  <input
                    type="number"
                    id="quantity"
                    min="1"
                    value={quantity}
                    onChange={(e) => setQuantity(e.target.value)}
                    required
                  />
                </div>
                
                <button type="submit" disabled={loading}>
                  {loading ? 'Processing...' : 'Retrieve Product'}
                </button>
              </>
            )}
          </form>
        );
        
      case 'locations':
        return (
          <form onSubmit={fetchItemLocations} className="operation-form">
            <h3>Item Storage Details</h3>
            
            <div className="form-group">
              <label htmlFor="itemForLocations">Select Item:</label>
              <select
                id="itemForLocations"
                value={selectedItem}
                onChange={(e) => setSelectedItem(e.target.value)}
                required
              >
                <option value="">Select Item</option>
                {items.map((item) => (
                  <option key={item.item_id} value={item.item_id}>
                    {item.name} (ID: {item.item_id})
                  </option>
                ))}
              </select>
            </div>
            
            <button type="submit" disabled={loading}>
              {loading ? 'Finding Locations...' : 'Show Locations'}
            </button>
          </form>
        );
        
      default:
        return <p>Select an operation from the buttons above.</p>;
    }
  };

  const renderResults = () => {
    if (!result) return null;
    
    return (
      <div className={`result-box ${result.success ? 'success' : 'error'}`}>
        <h3>Results</h3>
        <p><strong>{result.message}</strong></p>
        
        {result.details && (
          <div className="result-details">
            {result.details.item && (
              <p><strong>Item:</strong> {result.details.item}</p>
            )}
            
            {result.details.location && (
              <p><strong>Location:</strong> {result.details.location}</p>
            )}
            
            {result.details.status && (
              <p><strong>Status:</strong> {result.details.status}</p>
            )}
            
            {result.details.action && (
              <p><strong>Note:</strong> {result.details.action === 'updated' ? 'Updated empty place to occupied' : 'Added to new place'}</p>
            )}
            
            {result.details.quantity && (
              <p><strong>Quantity:</strong> {result.details.quantity}</p>
            )}
            
            {result.details.locations && result.details.locations.length > 0 && (
              <>
                <p><strong>Locations:</strong></p>
                <ul className="locations-list">
                  {result.details.locations.map((location, index) => (
                    <li key={location.place}>
                      {index + 1}. {location.displayLoc} (ID: {location.place})
                    </li>
                  ))}
                </ul>
              </>
            )}
            
            {activeOperation === 'retrieve' && (
              <p><strong>Retrieval Strategy:</strong> Column-wise (A1→A7, then B1→B7, etc.)</p>
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="operations-tab">
      <h2>Operations</h2>
      
      <div className="operations-buttons">
        <button 
          onClick={showAddProductOptions}
          className={activeOperation === 'add' ? 'active' : ''}
        >
          Add Product
        </button>
        <button 
          onClick={showRetrieveProductOptions}
          className={activeOperation === 'retrieve' ? 'active' : ''}
        >
          Retrieve Product
        </button>
        <button 
          onClick={showItemLocationsOptions}
          className={activeOperation === 'locations' ? 'active' : ''}
        >
          View Item Locations
        </button>
      </div>
      
      <div className="options-panel">
        {renderOptions()}
      </div>
      
      <div className="results-panel">
        {renderResults()}
      </div>
    </div>
  );
}

export default OperationsTab;
