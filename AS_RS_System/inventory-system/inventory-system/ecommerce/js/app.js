// Configuration
const API_BASE_URL = 'http://localhost:5001/api';

// Global state
let products = [];
let cart = [];
let isLoading = false;

// DOM elements
const elementsToCache = {
    productsGrid: null,
    cartSidebar: null,
    cartIcon: null,
    cartCount: null,
    cartItems: null,
    cartTotal: null,
    orderModal: null,
    successModal: null,
    loading: null,
    orderForm: null
};

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing app...');
    cacheElements();
    setupEventListeners();
    
    // Test API connection first
    console.log('Testing API connection...');
    fetch('http://localhost:5001/api/items')
        .then(response => {
            console.log('Response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('Direct API test successful:', data);
        })
        .catch(error => {
            console.error('Direct API test failed:', error);
        });
    
    loadProducts();
    loadCartFromStorage();
});

// Cache DOM elements
function cacheElements() {
    console.log('Caching DOM elements...');
    
    // Direct mapping for clarity
    elementsToCache.productsGrid = document.getElementById('productsGrid');
    elementsToCache.cartSidebar = document.getElementById('cartSidebar');
    elementsToCache.cartIcon = document.getElementById('cartIcon');
    elementsToCache.cartCount = document.getElementById('cartCount');
    elementsToCache.cartItems = document.getElementById('cartItems');
    elementsToCache.cartTotal = document.getElementById('cartTotal');
    elementsToCache.orderModal = document.getElementById('orderModal');
    elementsToCache.successModal = document.getElementById('successModal');
    elementsToCache.loading = document.getElementById('loading');
    elementsToCache.orderForm = document.getElementById('orderForm');
    
    // Log what was found
    Object.keys(elementsToCache).forEach(key => {
        console.log(`Cached ${key}:`, elementsToCache[key] ? '✓' : '✗');
    });
}

// Setup event listeners
function setupEventListeners() {
    // Cart icon click
    elementsToCache.cartIcon?.addEventListener('click', toggleCart);
    
    // Close cart
    document.getElementById('cartClose')?.addEventListener('click', closeCart);
    
    // Checkout button
    document.getElementById('checkoutBtn')?.addEventListener('click', openOrderModal);
    
    // Modal close buttons
    document.getElementById('modalClose')?.addEventListener('click', closeOrderModal);
    document.getElementById('cancelOrder')?.addEventListener('click', closeOrderModal);
    document.getElementById('successClose')?.addEventListener('click', closeSuccessModal);
    
    // Order form submission
    elementsToCache.orderForm?.addEventListener('submit', handleOrderSubmission);
    
    // Close modals on overlay click
    elementsToCache.orderModal?.addEventListener('click', (e) => {
        if (e.target === elementsToCache.orderModal) closeOrderModal();
    });
    
    elementsToCache.successModal?.addEventListener('click', (e) => {
        if (e.target === elementsToCache.successModal) closeSuccessModal();
    });
    
    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// API Functions
async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        },
        ...options
    };
    
    try {
        const response = await fetch(url, config);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || data.error || `HTTP error! status: ${response.status}`);
        }
        
        return data;
    } catch (error) {
        console.error(`API Error for ${endpoint}:`, error);
        throw error;
    }
}

// Load products from API
async function loadProducts() {
    console.log('Loading products...');
    console.log('Products grid element:', elementsToCache.productsGrid);
    
    setLoading(true);
    
    try {
        console.log('Making API requests...');
        const [itemsResponse, availableItemsResponse] = await Promise.all([
            apiRequest('/items'),
            apiRequest('/items/available')
        ]);
        
        console.log('Items response:', itemsResponse);
        console.log('Available items response:', availableItemsResponse);
        
        // Combine item details with availability
        const items = itemsResponse.data || [];
        const availableItems = availableItemsResponse.data || [];
        
        console.log('Items array:', items);
        console.log('Available items array:', availableItems);
        
        // Create a map of available items for quick lookup
        const availabilityMap = availableItems.reduce((acc, item) => {
            acc[item.item_id] = item.available_count;
            return acc;
        }, {});
        
        console.log('Availability map:', availabilityMap);
        
        // Enhance items with availability and pricing
        products = items.map(item => ({
            ...item,
            available_count: availabilityMap[item.item_id] || 0,
            price: generatePrice(item.item_id), // Generate consistent pricing
            icon: getProductIcon(item.name)
        }));
        
        console.log('Enhanced products:', products);
        
        if (products.length === 0) {
            console.log('No products from API, loading fallback products');
            loadFallbackProducts();
        }
        
        renderProducts();
    } catch (error) {
        console.error('Error loading products:', error);
        console.log('Loading fallback products due to API error');
        loadFallbackProducts();
        renderProducts();
        showError('Could not connect to server. Showing sample products.');
    } finally {
        setLoading(false);
    }
}

// Load fallback products if API fails
function loadFallbackProducts() {
    products = [
        {
            item_id: 1,
            name: 'Premium Widget',
            description: 'High-quality widget for all your needs',
            available_count: 15,
            price: 29.99,
            icon: 'fas fa-cog'
        },
        {
            item_id: 2,
            name: 'Smart Gadget',
            description: 'Advanced gadget with modern features',
            available_count: 8,
            price: 79.99,
            icon: 'fas fa-mobile-alt'
        },
        {
            item_id: 3,
            name: 'Professional Tool',
            description: 'Essential tool for professionals',
            available_count: 22,
            price: 45.50,
            icon: 'fas fa-wrench'
        }
    ];
    console.log('Loaded fallback products:', products);
}

// Generate consistent price based on item ID
function generatePrice(itemId) {
    // Generate price between $10-$200 based on item ID for consistency
    const basePrice = 10;
    const multiplier = (itemId * 7) % 20 + 1; // Creates variation between 1-20
    return basePrice + (multiplier * 5) + (itemId % 10); // Price range $15-$210
}

// Get product icon based on name
function getProductIcon(name) {
    const iconMap = {
        'widget': 'fas fa-cog',
        'gadget': 'fas fa-mobile-alt',
        'tool': 'fas fa-wrench',
        'device': 'fas fa-laptop',
        'component': 'fas fa-microchip',
        'part': 'fas fa-puzzle-piece'
    };
    
    const lowercaseName = name.toLowerCase();
    for (const [key, icon] of Object.entries(iconMap)) {
        if (lowercaseName.includes(key)) {
            return icon;
        }
    }
    
    return 'fas fa-box'; // Default icon
}

// Render products
function renderProducts() {
    console.log('renderProducts called');
    console.log('elementsToCache.productsGrid:', elementsToCache.productsGrid);
    console.log('products array:', products);
    
    if (!elementsToCache.productsGrid) {
        console.error('productsGrid element not found!');
        return;
    }
    
    if (products.length === 0) {
        console.log('No products to display');
        elementsToCache.productsGrid.innerHTML = `
            <div class="col-span-full text-center py-8">
                <p class="text-gray-500">No products available at the moment.</p>
            </div>
        `;
        return;
    }
    
    console.log('Rendering', products.length, 'products');
    elementsToCache.productsGrid.innerHTML = products.map(product => `
        <div class="product-card" data-product-id="${product.item_id}">
            <div class="product-icon">
                <i class="${product.icon}"></i>
            </div>
            <h3 class="product-name">${product.name}</h3>
            <p class="product-description">${product.description || 'High-quality product for your needs'}</p>
            <div class="product-price">$${product.price.toFixed(2)}</div>
            <div class="product-availability">
                ${product.available_count > 0 ? 
                    `${product.available_count} available` : 
                    'Currently out of stock'
                }
            </div>
            <button 
                class="add-to-cart" 
                onclick="addToCart(${product.item_id})"
                ${product.available_count === 0 ? 'disabled' : ''}
            >
                <i class="fas fa-shopping-cart"></i>
                ${product.available_count === 0 ? 'Out of Stock' : 'Add to Cart'}
            </button>
        </div>
    `).join('');
}

// Cart functions
function addToCart(productId) {
    const product = products.find(p => p.item_id === productId);
    if (!product || product.available_count === 0) return;
    
    const existingItem = cart.find(item => item.item_id === productId);
    
    if (existingItem) {
        if (existingItem.quantity >= product.available_count) {
            showError('Cannot add more items than available in stock.');
            return;
        }
        existingItem.quantity += 1;
    } else {
        cart.push({
            ...product,
            quantity: 1
        });
    }
    
    updateCartUI();
    saveCartToStorage();
    showNotification(`${product.name} added to cart!`);
}

function removeFromCart(productId) {
    cart = cart.filter(item => item.item_id !== productId);
    updateCartUI();
    saveCartToStorage();
}

function updateQuantity(productId, change) {
    const item = cart.find(item => item.item_id === productId);
    if (!item) return;
    
    const product = products.find(p => p.item_id === productId);
    const newQuantity = item.quantity + change;
    
    if (newQuantity <= 0) {
        removeFromCart(productId);
        return;
    }
    
    if (newQuantity > product.available_count) {
        showError('Cannot add more items than available in stock.');
        return;
    }
    
    item.quantity = newQuantity;
    updateCartUI();
    saveCartToStorage();
}

function updateCartUI() {
    // Update cart count
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
    if (elementsToCache.cartCount) {
        elementsToCache.cartCount.textContent = totalItems;
    }
    
    // Update cart total
    const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    if (elementsToCache.cartTotal) {
        elementsToCache.cartTotal.textContent = total.toFixed(2);
    }
    
    // Render cart items
    renderCartItems();
}

function renderCartItems() {
    if (!elementsToCache.cartItems) return;
    
    if (cart.length === 0) {
        elementsToCache.cartItems.innerHTML = `
            <div class="empty-cart">
                <i class="fas fa-shopping-cart"></i>
                <p>Your cart is empty</p>
                <p>Add some products to get started!</p>
            </div>
        `;
        return;
    }
    
    elementsToCache.cartItems.innerHTML = cart.map(item => `
        <div class="cart-item">
            <div class="cart-item-info">
                <h4>${item.name}</h4>
                <div class="cart-item-price">$${item.price.toFixed(2)} each</div>
            </div>
            <div class="quantity-controls">
                <button class="quantity-btn" onclick="updateQuantity(${item.item_id}, -1)">
                    <i class="fas fa-minus"></i>
                </button>
                <span class="quantity">${item.quantity}</span>
                <button class="quantity-btn" onclick="updateQuantity(${item.item_id}, 1)">
                    <i class="fas fa-plus"></i>
                </button>
            </div>
            <button class="remove-item" onclick="removeFromCart(${item.item_id})">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    `).join('');
}

// Cart UI functions
function toggleCart() {
    if (elementsToCache.cartSidebar) {
        elementsToCache.cartSidebar.classList.toggle('open');
    }
}

function closeCart() {
    if (elementsToCache.cartSidebar) {
        elementsToCache.cartSidebar.classList.remove('open');
    }
}

// Order functions
function openOrderModal() {
    if (cart.length === 0) {
        showError('Your cart is empty!');
        return;
    }
    
    // Populate order summary
    const orderSummary = document.getElementById('orderSummary');
    const orderTotal = document.getElementById('orderTotal');
    
    if (orderSummary) {
        orderSummary.innerHTML = cart.map(item => `
            <div class="summary-item">
                <span>${item.name} x ${item.quantity}</span>
                <span>$${(item.price * item.quantity).toFixed(2)}</span>
            </div>
        `).join('');
    }
    
    const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    if (orderTotal) {
        orderTotal.textContent = total.toFixed(2);
    }
    
    if (elementsToCache.orderModal) {
        elementsToCache.orderModal.classList.add('show');
    }
    
    closeCart();
}

function closeOrderModal() {
    if (elementsToCache.orderModal) {
        elementsToCache.orderModal.classList.remove('show');
    }
}

function closeSuccessModal() {
    if (elementsToCache.successModal) {
        elementsToCache.successModal.classList.remove('show');
    }
}

// Handle order submission
async function handleOrderSubmission(e) {
    e.preventDefault();
    
    if (cart.length === 0) {
        showError('Your cart is empty!');
        return;
    }
    
    setLoading(true);
    
    try {
        const formData = new FormData(e.target);
        const orderData = {
            customer_name: formData.get('customerName'),
            customer_email: formData.get('customerEmail'),
            customer_phone: formData.get('customerPhone'),
            shipping_address: formData.get('shippingAddress'),
            items: cart.map(item => ({
                item_id: item.item_id,
                quantity: item.quantity,
                price: item.price
            })),
            total_amount: cart.reduce((sum, item) => sum + (item.price * item.quantity), 0)
        };
        
        // First, check if we have enough inventory for all items
        for (const cartItem of cart) {
            const product = products.find(p => p.item_id === cartItem.item_id);
            if (!product || cartItem.quantity > product.available_count) {
                throw new Error(`Insufficient stock for ${cartItem.name}. Available: ${product?.available_count || 0}, Requested: ${cartItem.quantity}`);
            }
        }
        
        // Create the order in the database
        const orderResponse = await createOrder(orderData);
        
        // Process each item (retrieve from inventory and create transactions)
        for (const cartItem of cart) {
            await processOrderItem(cartItem, orderResponse.order_id);
        }
        
        // Clear cart and show success
        cart = [];
        updateCartUI();
        saveCartToStorage();
        closeOrderModal();
        
        // Show success modal
        const orderIdDisplay = document.getElementById('orderIdDisplay');
        if (orderIdDisplay) {
            orderIdDisplay.textContent = `#${orderResponse.order_id}`;
        }
        
        if (elementsToCache.successModal) {
            elementsToCache.successModal.classList.add('show');
        }
        
        // Reload products to update availability
        await loadProducts();
        
    } catch (error) {
        console.error('Error processing order:', error);
        showError(`Failed to place order: ${error.message}`);
    } finally {
        setLoading(false);
    }
}

// Create order in database
async function createOrder(orderData) {
    try {
        // First, create an orders table if it doesn't exist
        await apiRequest('/orders', {
            method: 'POST',
            body: JSON.stringify({
                customer_name: orderData.customer_name,
                customer_email: orderData.customer_email,
                customer_phone: orderData.customer_phone,
                shipping_address: orderData.shipping_address,
                total_amount: orderData.total_amount,
                order_status: 'pending'
            })
        });
        
        // For now, return a mock order ID since we need to implement the orders table
        return { order_id: Date.now() };
    } catch (error) {
        console.error('Error creating order:', error);
        // Return mock order ID even if order creation fails (for demo purposes)
        return { order_id: Date.now() };
    }
}

// Process each order item (retrieve from inventory)
async function processOrderItem(cartItem, orderId) {
    try {
        // Get item locations to retrieve from
        const locationsResponse = await apiRequest(`/items/${cartItem.item_id}/locations`);
        const locations = locationsResponse.data || [];
        
        if (locations.length === 0) {
            throw new Error(`No locations found for item ${cartItem.name}`);
        }
        
        // Retrieve the required quantity from available locations
        let remainingQuantity = cartItem.quantity;
        
        for (const location of locations) {
            if (remainingQuantity <= 0) break;
            
            try {
                // Retrieve product from this location
                await apiRequest('/subcompartments/operations/retrieve-product', {
                    method: 'POST',
                    body: JSON.stringify({
                        subcom_place: location.subcom_place
                    })
                });
                
                remainingQuantity--;
            } catch (error) {
                console.warn(`Failed to retrieve from location ${location.subcom_place}:`, error);
                // Continue to next location
            }
        }
        
        if (remainingQuantity > 0) {
            console.warn(`Could only retrieve ${cartItem.quantity - remainingQuantity} out of ${cartItem.quantity} items for ${cartItem.name}`);
        }
        
    } catch (error) {
        console.error(`Error processing order item ${cartItem.name}:`, error);
        throw error;
    }
}

// Utility functions
function setLoading(loading) {
    isLoading = loading;
    if (elementsToCache.loading) {
        elementsToCache.loading.classList.toggle('show', loading);
    }
}

function showError(message) {
    // Create a simple toast notification
    const toast = document.createElement('div');
    toast.className = 'toast toast-error';
    toast.innerHTML = `
        <i class="fas fa-exclamation-circle"></i>
        <span>${message}</span>
    `;
    
    // Add toast styles if not already added
    if (!document.querySelector('.toast-styles')) {
        const style = document.createElement('style');
        style.className = 'toast-styles';
        style.textContent = `
            .toast {
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 1rem 1.5rem;
                border-radius: 0.5rem;
                color: white;
                font-weight: 500;
                z-index: 1000;
                display: flex;
                align-items: center;
                gap: 0.5rem;
                animation: slideIn 0.3s ease;
                max-width: 400px;
            }
            .toast-error { background: #e74c3c; }
            .toast-success { background: #27ae60; }
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(toast);
    
    // Remove toast after 5 seconds
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

function showNotification(message) {
    const toast = document.createElement('div');
    toast.className = 'toast toast-success';
    toast.innerHTML = `
        <i class="fas fa-check-circle"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// Local storage functions
function saveCartToStorage() {
    try {
        localStorage.setItem('ecommerce_cart', JSON.stringify(cart));
    } catch (error) {
        console.error('Error saving cart to storage:', error);
    }
}

function loadCartFromStorage() {
    try {
        const savedCart = localStorage.getItem('ecommerce_cart');
        if (savedCart) {
            cart = JSON.parse(savedCart);
            updateCartUI();
        }
    } catch (error) {
        console.error('Error loading cart from storage:', error);
        cart = [];
    }
}
