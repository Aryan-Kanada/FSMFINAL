const axios = require('axios');

const ARYAN_SERVICE_URL = 'http://127.0.0.1:5000';

class ASRSIntegrationService {
    
    // Send data to aryan.py
    static async sendToAryan(data) {
        try {
            console.log('Sending data to aryan.py:', JSON.stringify(data, null, 2));
            const response = await axios.post(`${ARYAN_SERVICE_URL}/backend-data`, data, {
                timeout: 5000,
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            console.log('Response from aryan.py:', response.data);
            return response.data;
        } catch (error) {
            console.error('Error sending to aryan.py:', error.message);
            return null;
        }
    }
    
    // Call this when order is placed
    static async notifyOrderPlacement(orderData) {
        const data = {
            type: 'order_placed',
            order_id: orderData.order_id,
            customer_name: orderData.customer_name,
            order_items: orderData.items || []
        };
        
        return await this.sendToAryan(data);
    }
    
    // Call this when product is added to inventory
    static async notifyProductAdded(subcomPlace, itemId, status) {
        const data = {
            type: 'product_added',
            subcom_place: subcomPlace,
            item_id: itemId,
            status: status
        };
        
        return await this.sendToAryan(data);
    }
    
    // Call this when product is retrieved manually
    static async notifyProductRetrieved(retrievalData) {
        const data = {
            type: 'product_retrieved',
            item_id: retrievalData.item_id,
            quantity: retrievalData.quantity,
            locations: retrievalData.locations
        };
        
        return await this.sendToAryan(data);
    }
}

module.exports = ASRSIntegrationService;
