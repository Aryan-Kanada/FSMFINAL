const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const rateLimit = require('express-rate-limit');
const winston = require('winston');

// Load environment variables
dotenv.config();

// Configure Winston logger
const logger = winston.createLogger({
  level: process.env.NODE_ENV === 'development' ? 'debug' : 'info',
  transports: [new winston.transports.Console({ format: winston.format.simple() })]
});

// Import routes
const boxRoutes = require('./routes/boxRoutes');
const itemRoutes = require('./routes/itemRoutes');
const subCompartmentRoutes = require('./routes/subCompartmentRoutes');
const transactionRoutes = require('./routes/transactionRoutes');
const orderRoutes = require('./routes/orderRoutes');

// Initialize app
const app = express();

// CORS restricted to frontend origin
app.use(cors({ origin: `http://localhost:${process.env.PORT_FRONTEND}` }));

// Body parsing
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Rate limiter for incoming requests
const limiter = rateLimit({
  windowMs: 60 * 1000, // 1 minute
  max: 100
});
app.use(limiter);

// Mount routes
app.use('/api/boxes', boxRoutes);
app.use('/api/items', itemRoutes);
app.use('/api/subcompartments', subCompartmentRoutes);
app.use('/api/transactions', transactionRoutes);
app.use('/api/orders', orderRoutes);

// Root route
app.get('/', (req, res) => {
  res.send('Inventory Management System API');
});

// Error handling
app.use((err, req, res, next) => {
  logger.error(err.stack);
  res.status(500).json({
    success: false,
    error: 'Server Error',
    message:
      process.env.NODE_ENV === 'development' ? err.message : 'Something went wrong'
  });
});

// Start server
const PORT = process.env.PORT_BACKEND || 4000;
app.listen(PORT, () => {
  logger.info(`Server running in ${process.env.NODE_ENV} on port ${PORT}`);
});
