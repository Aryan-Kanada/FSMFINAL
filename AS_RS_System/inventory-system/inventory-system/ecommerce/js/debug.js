// Simplified version to debug the issue
console.log('Script loaded');

let products = [];

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded');
    
    // Check if elements exist
    const productsGrid = document.getElementById('productsGrid');
    console.log('Products grid found:', !!productsGrid);
    
    if (!productsGrid) {
        console.error('Products grid not found!');
        return;
    }
    
    // Test with dummy products first
    showDummyProducts();
    
    // Then try to load from API
    setTimeout(loadProductsFromAPI, 1000);
});

function showDummyProducts() {
    console.log('Showing dummy products');
    const productsGrid = document.getElementById('productsGrid');
    
    if (!productsGrid) {
        console.error('Products grid still not found!');
        return;
    }
    
    const dummyProducts = [
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
        }
    ];
    
    const html = dummyProducts.map(product => `
        <div class="product-card" data-product-id="${product.item_id}">
            <div class="product-icon">
                <i class="${product.icon}"></i>
            </div>
            <h3 class="product-name">${product.name}</h3>
            <p class="product-description">${product.description}</p>
            <div class="product-price">$${product.price.toFixed(2)}</div>
            <div class="product-availability">${product.available_count} available</div>
            <button class="add-to-cart" onclick="alert('Added to cart!')">
                <i class="fas fa-shopping-cart"></i>
                Add to Cart
            </button>
        </div>
    `).join('');
    
    productsGrid.innerHTML = html;
    console.log('Dummy products inserted');
}

function loadProductsFromAPI() {
    console.log('Attempting to load from API...');
    
    fetch('http://localhost:5001/api/items')
        .then(response => {
            console.log('API response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('API data received:', data);
            if (data.data && data.data.length > 0) {
                displayAPIProducts(data.data);
            }
        })
        .catch(error => {
            console.error('API error:', error);
        });
}

function displayAPIProducts(items) {
    console.log('Displaying API products:', items);
    const productsGrid = document.getElementById('productsGrid');
    
    if (!productsGrid) {
        console.error('Products grid not found when displaying API products!');
        return;
    }
    
    const html = items.map(item => `
        <div class="product-card" data-product-id="${item.item_id}">
            <div class="product-icon">
                <i class="fas fa-box"></i>
            </div>
            <h3 class="product-name">${item.name}</h3>
            <p class="product-description">${item.description || 'Quality product'}</p>
            <div class="product-price">$${(Math.random() * 100 + 20).toFixed(2)}</div>
            <div class="product-availability">In Stock</div>
            <button class="add-to-cart" onclick="alert('Added ${item.name} to cart!')">
                <i class="fas fa-shopping-cart"></i>
                Add to Cart
            </button>
        </div>
    `).join('');
    
    productsGrid.innerHTML = html;
    console.log('API products displayed');
}
