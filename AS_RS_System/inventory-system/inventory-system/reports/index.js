const express = require('express');
const cors = require('cors');
const path = require('path');
require('dotenv').config();

// Import generators
const DailyReportGenerator = require('./generators/dailyReport');
const WeeklyReportGenerator = require('./generators/weeklyReport');
const MonthlyReportGenerator = require('./generators/monthlyReport');

// Import utilities
const { testConnection } = require('./config/db');
const DateUtils = require('./utils/dateUtils');

const app = express();
const PORT = process.env.REPORTS_PORT || 3002;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'output')));

// Initialize generators
const dailyGenerator = new DailyReportGenerator();
const weeklyGenerator = new WeeklyReportGenerator();
const monthlyGenerator = new MonthlyReportGenerator();

// API Routes

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'Inventory Reports Generator',
    timestamp: new Date().toISOString()
  });
});

// Generate daily report
app.post('/api/reports/daily', async (req, res) => {
  try {
    const { date, formats = ['csv', 'pdf'] } = req.body;
    const result = await dailyGenerator.generateReport(date, formats);
    res.json(result);
  } catch (error) {
    console.error('Error generating daily report:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Generate multiple daily reports
app.post('/api/reports/daily/multiple', async (req, res) => {
  try {
    const { days = 7, formats = ['csv', 'pdf'] } = req.body;
    const result = await dailyGenerator.generateMultipleDays(days, formats);
    res.json({
      success: true,
      message: `Generated ${days} daily reports`,
      results: result
    });
  } catch (error) {
    console.error('Error generating multiple daily reports:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Generate weekly report
app.post('/api/reports/weekly', async (req, res) => {
  try {
    const { date, formats = ['csv', 'pdf'] } = req.body;
    const result = await weeklyGenerator.generateReport(date, formats);
    res.json(result);
  } catch (error) {
    console.error('Error generating weekly report:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Generate multiple weekly reports
app.post('/api/reports/weekly/multiple', async (req, res) => {
  try {
    const { weeks = 4, formats = ['csv', 'pdf'] } = req.body;
    const result = await weeklyGenerator.generateMultipleWeeks(weeks, formats);
    res.json({
      success: true,
      message: `Generated ${weeks} weekly reports`,
      results: result
    });
  } catch (error) {
    console.error('Error generating multiple weekly reports:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Generate monthly report
app.post('/api/reports/monthly', async (req, res) => {
  try {
    const { date, formats = ['csv', 'pdf'] } = req.body;
    const result = await monthlyGenerator.generateReport(date, formats);
    res.json(result);
  } catch (error) {
    console.error('Error generating monthly report:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Generate multiple monthly reports
app.post('/api/reports/monthly/multiple', async (req, res) => {
  try {
    const { months = 6, formats = ['csv', 'pdf'] } = req.body;
    const result = await monthlyGenerator.generateMultipleMonths(months, formats);
    res.json({
      success: true,
      message: `Generated ${months} monthly reports`,
      results: result
    });
  } catch (error) {
    console.error('Error generating multiple monthly reports:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Generate yearly comparison report
app.post('/api/reports/yearly', async (req, res) => {
  try {
    const { year } = req.body;
    const result = await monthlyGenerator.generateYearlyComparison(year);
    res.json(result);
  } catch (error) {
    console.error('Error generating yearly comparison:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Generate all reports (comprehensive)
app.post('/api/reports/all', async (req, res) => {
  try {
    const { formats = ['csv', 'pdf'] } = req.body;
    
    console.log('🚀 Starting comprehensive report generation...');
    
    const results = {
      daily: null,
      weekly: null,
      monthly: null,
      timestamp: new Date().toISOString()
    };

    // Generate all reports in parallel
    const [dailyResult, weeklyResult, monthlyResult] = await Promise.allSettled([
      dailyGenerator.generateReport(null, formats),
      weeklyGenerator.generateReport(null, formats),
      monthlyGenerator.generateReport(null, formats)
    ]);

    results.daily = dailyResult.status === 'fulfilled' ? dailyResult.value : { error: dailyResult.reason.message };
    results.weekly = weeklyResult.status === 'fulfilled' ? weeklyResult.value : { error: weeklyResult.reason.message };
    results.monthly = monthlyResult.status === 'fulfilled' ? monthlyResult.value : { error: monthlyResult.reason.message };

    const successCount = [results.daily, results.weekly, results.monthly].filter(r => r && r.success).length;

    res.json({
      success: successCount > 0,
      message: `Generated ${successCount}/3 reports successfully`,
      results: results
    });

  } catch (error) {
    console.error('Error generating comprehensive reports:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get available reports
app.get('/api/reports/list', async (req, res) => {
  try {
    const fs = require('fs-extra');
    const outputDir = path.join(__dirname, 'output');
    
    const csvDir = path.join(outputDir, 'csv');
    const pdfDir = path.join(outputDir, 'pdf');
    
    const reports = {
      csv: [],
      pdf: []
    };

    // List CSV files
    if (await fs.pathExists(csvDir)) {
      const csvFiles = await fs.readdir(csvDir);
      const csvFileDetails = await Promise.all(
        csvFiles.filter(file => file.endsWith('.csv')).map(async file => {
          const stats = await fs.stat(path.join(csvDir, file));
          return {
            filename: file,
            path: `/csv/${file}`,
            size: stats.size,
            created: stats.birthtime
          };
        })
      );
      reports.csv = csvFileDetails;
    }

    // List PDF files
    if (await fs.pathExists(pdfDir)) {
      const pdfFiles = await fs.readdir(pdfDir);
      const pdfFileDetails = await Promise.all(
        pdfFiles.filter(file => file.endsWith('.pdf')).map(async file => {
          const stats = await fs.stat(path.join(pdfDir, file));
          return {
            filename: file,
            path: `/pdf/${file}`,
            size: stats.size,
            created: stats.birthtime
          };
        })
      );
      reports.pdf = pdfFileDetails;
    }

    res.json({
      success: true,
      reports: reports,
      total: reports.csv.length + reports.pdf.length
    });

  } catch (error) {
    console.error('Error listing reports:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Download report file
app.get('/api/reports/download/:type/:filename', async (req, res) => {
  try {
    const { type, filename } = req.params;
    
    if (!['csv', 'pdf'].includes(type)) {
      return res.status(400).json({ error: 'Invalid file type' });
    }

    const filePath = path.join(__dirname, 'output', type, filename);
    const fs = require('fs-extra');
    
    if (!(await fs.pathExists(filePath))) {
      return res.status(404).json({ error: 'File not found' });
    }

    res.download(filePath, filename);

  } catch (error) {
    console.error('Error downloading report:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Cleanup old reports
app.delete('/api/reports/cleanup', async (req, res) => {
  try {
    const { olderThan = 30 } = req.body; // days
    const fs = require('fs-extra');
    const outputDir = path.join(__dirname, 'output');
    
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - olderThan);
    
    let deletedCount = 0;
    
    for (const subDir of ['csv', 'pdf']) {
      const dirPath = path.join(outputDir, subDir);
      
      if (await fs.pathExists(dirPath)) {
        const files = await fs.readdir(dirPath);
        
        for (const file of files) {
          const filePath = path.join(dirPath, file);
          const stats = await fs.stat(filePath);
          
          if (stats.birthtime < cutoffDate) {
            await fs.remove(filePath);
            deletedCount++;
          }
        }
      }
    }

    res.json({
      success: true,
      message: `Cleaned up ${deletedCount} old report files`,
      deletedCount: deletedCount
    });

  } catch (error) {
    console.error('Error cleaning up reports:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Error handling middleware
app.use((error, req, res, next) => {
  console.error('Unhandled error:', error);
  res.status(500).json({
    success: false,
    error: 'Internal server error',
    message: error.message
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    success: false,
    error: 'Endpoint not found'
  });
});

// Start server
const startServer = async () => {
  try {
    // Test database connection
    await testConnection();
    
    app.listen(PORT, () => {
      console.log('🚀 Inventory Reports Generator Started');
      console.log(`📊 Server running on http://localhost:${PORT}`);
      console.log(`📅 Current date: ${DateUtils.getCurrentDate()}`);
      console.log('📋 Available endpoints:');
      console.log('   POST /api/reports/daily - Generate daily report');
      console.log('   POST /api/reports/weekly - Generate weekly report');
      console.log('   POST /api/reports/monthly - Generate monthly report');
      console.log('   POST /api/reports/all - Generate all reports');
      console.log('   GET  /api/reports/list - List available reports');
      console.log('   GET  /api/reports/download/:type/:filename - Download report');
      console.log('   DELETE /api/reports/cleanup - Cleanup old reports');
      console.log('   GET  /health - Health check');
    });

  } catch (error) {
    console.error('❌ Failed to start server:', error);
    process.exit(1);
  }
};

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('🔄 Shutting down Reports Generator...');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('🔄 Shutting down Reports Generator...');
  process.exit(0);
});

// Start the server
if (require.main === module) {
  startServer();
}

module.exports = app;
