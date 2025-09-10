# Inventory Management System

This project is a full-stack Inventory Management System with a React + Vite frontend and an Express.js backend.

## Project Structure

```
inventory-system/
├── backend/           # Express.js backend
│   ├── config/        # Configuration files
│   ├── controllers/   # Request handlers
│   ├── models/        # Database models
│   ├── routes/        # API routes
│   └── server.js      # Server entry point
├── frontend/          # React + Vite frontend
│   ├── public/        # Static files
│   └── src/
│       ├── components/   # Reusable components
│       ├── pages/        # Page components
│       └── services/     # API services
└── schema.sql        # Database schema
```

## Quick Start

### Setup Database

1. Create the MySQL database:
   ```bash
   mysql -u your_username -p < schema.sql
   ```

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd inventory-system/backend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env` file (use `.env.example` as a template):
   ```bash
   cp .env.example .env
   # Edit .env file with your database credentials
   ```

4. Start the server:
   ```bash
   npm run dev
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd inventory-system/frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env` file (use `.env.example` as a template):
   ```bash
   cp .env.example .env
   ```

4. Start the development server:
   ```bash
   npm run dev
   ```

## Features

- Box management (add, view, delete)
- Item management (add, view, delete)
- SubCompartment management (add, view, update status)
- Transaction tracking
- Operations (add product, retrieve product, view item locations)

## API Endpoints

### Boxes
- GET `/api/boxes` - Get all boxes
- GET `/api/boxes/:id` - Get a specific box
- POST `/api/boxes` - Create a new box
- DELETE `/api/boxes/:id` - Delete a box

### Items
- GET `/api/items` - Get all items
- GET `/api/items/available` - Get available items with count
- GET `/api/items/:id` - Get a specific item
- GET `/api/items/:id/locations` - Get item locations
- POST `/api/items` - Create a new item
- DELETE `/api/items/:id` - Delete an item

### SubCompartments
- GET `/api/subcompartments` - Get all subcompartments
- GET `/api/subcompartments/:place` - Get a specific subcompartment
- POST `/api/subcompartments` - Create a new subcompartment
- PATCH `/api/subcompartments/:place/status` - Update subcompartment status
- DELETE `/api/subcompartments/:place` - Delete a subcompartment
- POST `/api/subcompartments/operations/add-product` - Add product
- POST `/api/subcompartments/operations/retrieve-product` - Retrieve product

### Transactions
- GET `/api/transactions` - Get all transactions (with sorting options)
- GET `/api/transactions/:id` - Get a specific transaction
- GET `/api/transactions/item/:itemId` - Get transactions by item

## License

This project is licensed under the MIT License.
