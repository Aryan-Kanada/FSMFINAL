// Simple and working version
const API_BASE_URL = 'http://localhost:5001/api';

let products = [];
let cart = [];

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, starting app...');
    
    // Setup event listeners
    setupEventListeners();
    
    // Load products
    loadProducts();
    
    // Load cart from localStorage
    loadCartFromStorage();
});

function setupEventListeners() {
    // Cart icon
    const cartIcon = document.getElementById('cartIcon');
    if (cartIcon) {
        cartIcon.addEventListener('click', toggleCart);
    }
    
    // Close cart
    const cartClose = document.getElementById('cartClose');
    if (cartClose) {
        cartClose.addEventListener('click', closeCart);
    }
    
    // Checkout button
    const checkoutBtn = document.getElementById('checkoutBtn');
    if (checkoutBtn) {
        checkoutBtn.addEventListener('click', openOrderModal);
    }
    
    // Modal close buttons
    const modalClose = document.getElementById('modalClose');
    const cancelOrder = document.getElementById('cancelOrder');
    const successClose = document.getElementById('successClose');
    
    if (modalClose) modalClose.addEventListener('click', closeOrderModal);
    if (cancelOrder) cancelOrder.addEventListener('click', closeOrderModal);
    if (successClose) successClose.addEventListener('click', closeSuccessModal);
    
    // Order form
    const orderForm = document.getElementById('orderForm');
    if (orderForm) {
        orderForm.addEventListener('submit', handleOrderSubmission);
    }
    
    // Close modals on overlay click
    const orderModal = document.getElementById('orderModal');
    const successModal = document.getElementById('successModal');
    
    if (orderModal) {
        orderModal.addEventListener('click', (e) => {
            if (e.target === orderModal) closeOrderModal();
        });
    }
    
    if (successModal) {
        successModal.addEventListener('click', (e) => {
            if (e.target === successModal) closeSuccessModal();
        });
    }
}

async function loadProducts() {
    console.log('Loading products...');
    setLoading(true);
    
    try {
        // First try to load from API
        const response = await fetch(`${API_BASE_URL}/items`);
        const data = await response.json();
        
        if (data.success && data.data) {
            // Get availability
            const availResponse = await fetch(`${API_BASE_URL}/items/available`);
            const availData = await availResponse.json();
            
            // Create availability map
            const availabilityMap = {};
            if (availData.success && availData.data) {
                availData.data.forEach(item => {
                    availabilityMap[item.item_id] = item.available_count;
                });
            }
            
            // Enhanced products with pricing and availability
            products = data.data.map(item => ({
                ...item,
                available_count: availabilityMap[item.item_id] || 0,
                price: generatePrice(item.item_id),
                icon: getProductIcon(item.name)
            }));
            
        } else {
            throw new Error('No data from API');
        }
        
    } catch (error) {
        console.error('API Error:', error);
                // Use fallback products
        products = [
            {
                item_id: 1,
                name: 'Bearing',
                description: 'Steel ball bearing',
                available_count: 61,
                price: 200,
                icon: 'fas fa-cog'
            },
            {
                item_id: 2,
                name: 'Gear',
                description: '24T spur gear',
                available_count: 63,
                price: 150,
                icon: 'fas fa-cog'
            },
            {
                item_id: 3,
                name: 'Bolt Set',
                description: 'M6 bolts with washers',
                available_count: 66,
                price: 55,
                icon: 'fas fa-wrench'
            }
        ];
        
        showError('Using sample products - backend may be unavailable');
    }
    
    renderProducts();
    setLoading(false);
}

function generatePrice(itemId) {
    // Fixed prices as requested
    const fixedPrices = {
        1: 200,  // Bearing
        2: 150,  // Gear  
        3: 55    // Bolt Set
    };
    
    // Return fixed price if available, otherwise use a default
    return fixedPrices[itemId] || 100;
}

function getProductIcon(name) {
    const iconMap = {
        'bearing': 'fas fa-circle',
        'gear': 'fas fa-cog',
        'bolt': 'fas fa-wrench',
        'widget': 'fas fa-cube',
        'gadget': 'fas fa-mobile-alt',
        'tool': 'fas fa-wrench'
    };
    
    const lowercaseName = name.toLowerCase();
    for (const [key, icon] of Object.entries(iconMap)) {
        if (lowercaseName.includes(key)) {
            return icon;
        }
    }
    return 'fas fa-box';
}

function renderProducts() {
    console.log('Rendering products:', products.length);
    const productsGrid = document.getElementById('productsGrid');
    
    if (!productsGrid) {
        console.error('Products grid not found!');
        return;
    }
    
    if (products.length === 0) {
        productsGrid.innerHTML = `
            <div class="col-span-full text-center py-8">
                <p class="text-gray-500">No products available</p>
            </div>
        `;
        return;
    }
    
    productsGrid.innerHTML = products.map(product => `
        <div class="product-card" data-product-id="${product.item_id}">
            <div class="product-icon">
                <i class="${product.icon}"></i>
            </div>
            <h3 class="product-name">${product.name}</h3>
            <p class="product-description">${product.description || 'Quality product'}</p>
            <div class="product-price">₹${product.price.toLocaleString('en-IN')}</div>
            <div class="product-availability">
                ${product.available_count > 0 ? 
                    `${product.available_count} available` : 
                    'Out of stock'
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

function addToCart(productId) {
    const product = products.find(p => p.item_id === productId);
    if (!product || product.available_count === 0) {
        showError('Product not available');
        return;
    }
    
    const existingItem = cart.find(item => item.item_id === productId);
    
    if (existingItem) {
        if (existingItem.quantity >= product.available_count) {
            showError('Cannot add more than available stock');
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
    showSuccess('Added to cart!');
}

function updateCartUI() {
    const cartCount = document.getElementById('cartCount');
    const cartItems = document.getElementById('cartItems');
    const cartTotal = document.getElementById('cartTotal');
    
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
    const totalPrice = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    
    if (cartCount) cartCount.textContent = totalItems;
    if (cartTotal) cartTotal.textContent = totalPrice.toLocaleString('en-IN');
    
    if (cartItems) {
        if (cart.length === 0) {
            cartItems.innerHTML = '<p class="empty-cart">Your cart is empty</p>';
        } else {
            cartItems.innerHTML = cart.map(item => `
                <div class="cart-item">
                    <div class="cart-item-info">
                        <h4>${item.name}</h4>
                        <p>₹${item.price.toLocaleString('en-IN')}</p>
                    </div>
                    <div class="cart-item-controls">
                        <button onclick="updateCartQuantity(${item.item_id}, ${item.quantity - 1})">-</button>
                        <span>${item.quantity}</span>
                        <button onclick="updateCartQuantity(${item.item_id}, ${item.quantity + 1})">+</button>
                        <button onclick="removeFromCart(${item.item_id})" class="remove-btn">×</button>
                    </div>
                </div>
            `).join('');
        }
    }
}

function updateCartQuantity(productId, newQuantity) {
    if (newQuantity <= 0) {
        removeFromCart(productId);
        return;
    }
    
    const product = products.find(p => p.item_id === productId);
    if (!product || newQuantity > product.available_count) {
        showError('Invalid quantity');
        return;
    }
    
    const cartItem = cart.find(item => item.item_id === productId);
    if (cartItem) {
        cartItem.quantity = newQuantity;
        updateCartUI();
        saveCartToStorage();
    }
}

function removeFromCart(productId) {
    cart = cart.filter(item => item.item_id !== productId);
    updateCartUI();
    saveCartToStorage();
}

function toggleCart() {
    const cartSidebar = document.getElementById('cartSidebar');
    if (cartSidebar) {
        cartSidebar.classList.toggle('open');
    }
}

function closeCart() {
    const cartSidebar = document.getElementById('cartSidebar');
    if (cartSidebar) {
        cartSidebar.classList.remove('open');
    }
}

function openOrderModal() {
    if (cart.length === 0) {
        showError('Your cart is empty');
        return;
    }
    
    const orderModal = document.getElementById('orderModal');
    const orderSummary = document.getElementById('orderSummary');
    const orderTotal = document.getElementById('orderTotal');
    
    if (orderSummary) {
        orderSummary.innerHTML = cart.map(item => `
            <div class="order-item">
                <span>${item.name} × ${item.quantity}</span>
                <span>₹${(item.price * item.quantity).toLocaleString('en-IN')}</span>
            </div>
        `).join('');
    }
    
    if (orderTotal) {
        const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        orderTotal.textContent = total.toLocaleString('en-IN');
    }
    
    if (orderModal) {
        orderModal.style.display = 'flex';
    }
}

function closeOrderModal() {
    const orderModal = document.getElementById('orderModal');
    if (orderModal) {
        orderModal.style.display = 'none';
    }
}

function closeSuccessModal() {
    const successModal = document.getElementById('successModal');
    if (successModal) {
        successModal.style.display = 'none';
    }
}

async function handleOrderSubmission(e) {
    e.preventDefault();
    
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
        }))
    };
    
    try {
        setLoading(true);
        const response = await fetch(`${API_BASE_URL}/orders`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(orderData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Clear cart
            cart = [];
            updateCartUI();
            saveCartToStorage();
            
            // Refresh products to show updated inventory
            loadProducts();
            
            // Show success modal
            const orderIdDisplay = document.getElementById('orderIdDisplay');
            if (orderIdDisplay) {
                orderIdDisplay.textContent = result.data.order_id;
            }
            
            closeOrderModal();
            const successModal = document.getElementById('successModal');
            if (successModal) {
                successModal.style.display = 'flex';
            }
        } else {
            showError(result.message || 'Order failed');
        }
        
    } catch (error) {
        console.error('Order error:', error);
        showError('Order failed - please try again');
    } finally {
        setLoading(false);
    }
}

function saveCartToStorage() {
    localStorage.setItem('ecommerce-cart', JSON.stringify(cart));
}

function loadCartFromStorage() {
    try {
        const saved = localStorage.getItem('ecommerce-cart');
        if (saved) {
            cart = JSON.parse(saved);
            updateCartUI();
        }
    } catch (error) {
        console.error('Error loading cart from storage:', error);
        cart = [];
    }
}

function setLoading(loading) {
    const loadingEl = document.getElementById('loading');
    if (loadingEl) {
        loadingEl.style.display = loading ? 'flex' : 'none';
    }
}

function showError(message) {
    console.error(message);
    // Simple alert for now
    alert('Error: ' + message);
}

function showSuccess(message) {
    console.log(message);
    // Simple alert for now
    alert(message);
}
