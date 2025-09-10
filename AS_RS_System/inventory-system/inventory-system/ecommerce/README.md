# E-Commerce Landing Page

This is a professional, minimalist e-commerce landing page that integrates with the existing inventory management system.

## Features

- **Clean, Professional Design**: Minimalist interface with modern styling
- **Product Catalog**: Displays available products from the inventory system
- **Shopping Cart**: Add/remove items, update quantities
- **Order Processing**: Complete order form with customer details
- **Real-time Inventory**: Shows actual stock levels from the database
- **Transaction Recording**: Orders are recorded in the database with transaction history
- **Responsive Design**: Works on desktop and mobile devices

## Tech Stack

- **Frontend**: HTML5, CSS3 (with CSS Grid and Flexbox), Vanilla JavaScript
- **Styling**: Modern CSS with animations and transitions
- **Icons**: Font Awesome
- **Fonts**: Inter (Google Fonts)
- **Backend Integration**: RESTful API calls to the existing Express.js backend

## File Structure

```
ecommerce/
├── index.html          # Main landing page
├── css/
│   └── styles.css      # All styling and responsive design
└── js/
    └── app.js          # Application logic and API integration
```

## Setup Instructions

1. **Database Setup**: First, run the orders table migration:
   ```sql
   mysql -u your_username -p your_database < ../backend/migrations/orders_tables.sql
   ```

2. **Backend Setup**: Make sure the backend server is running:
   ```bash
   cd ../backend
   npm run dev
   ```

3. **Frontend Setup**: Open the landing page:
   ```bash
   # Navigate to the ecommerce directory
   cd ecommerce
   
   # Open index.html in your browser or serve with a local server
   # For example, with Python:
   python3 -m http.server 8000
   
   # Then visit: http://localhost:8000
   ```

## How It Works

### Product Display
- Fetches products from `/api/items` endpoint
- Shows available quantities from `/api/items/available`
- Generates consistent pricing based on item IDs
- Displays product icons based on product names

### Shopping Cart
- Local storage persistence
- Real-time quantity validation against inventory
- Calculates totals automatically

### Order Processing
1. **Order Creation**: Creates order record in the `Orders` table
2. **Inventory Update**: Retrieves items from inventory using existing operations
3. **Transaction Recording**: Each item retrieval creates a transaction record
4. **Stock Updates**: SubCompartment status updated from "Occupied" to "Empty"

### Database Integration

When a user places an order:

1. **Orders Table**: New order record with customer info and totals
2. **OrderItems Table**: Individual line items for the order
3. **Transactions Table**: Records each item retrieval as "retrieved" action
4. **SubCompartments Table**: Status updated to "Empty" for retrieved items

## API Endpoints Used

- `GET /api/items` - Fetch all products
- `GET /api/items/available` - Get products with stock counts
- `GET /api/items/:id/locations` - Get locations of specific items
- `POST /api/orders` - Create new order
- `POST /api/subcompartments/operations/retrieve-product` - Remove item from inventory

## Customization

### Styling
- Modify `css/styles.css` to change colors, fonts, layout
- Uses CSS custom properties for easy theme updates
- Fully responsive with mobile-first approach

### Functionality
- Update `js/app.js` to add new features
- Modify API endpoints in the configuration
- Add new product icons in the `getProductIcon()` function

### Pricing
- Currently uses algorithmic pricing based on item IDs
- Can be modified to use database-stored prices
- Update the `generatePrice()` function as needed

## Browser Support

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## Performance Features

- Lazy loading of product images
- Optimized CSS with minimal dependencies
- Local storage for cart persistence
- Efficient DOM updates
- Error handling and loading states
