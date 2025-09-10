const DailyReportGenerator = require('./generators/dailyReport');
const WeeklyReportGenerator = require('./generators/weeklyReport');
const MonthlyReportGenerator = require('./generators/monthlyReport');
const CSVExporter = require('./exporters/csvExporter');
const PDFExporter = require('./exporters/pdfExporter');
const DateUtils = require('./utils/dateUtils');
const ReportFormatter = require('./utils/reportFormatter');
const ReportQueries = require('./utils/reportQueries');

/**
 * Main Reports Manager - Centralized interface for all reporting functionality
 */
class ReportsManager {
  constructor() {
    this.dailyGenerator = new DailyReportGenerator();
    this.weeklyGenerator = new WeeklyReportGenerator();
    this.monthlyGenerator = new MonthlyReportGenerator();
    this.csvExporter = new CSVExporter();
    this.pdfExporter = new PDFExporter();
  }

  /**
   * Generate all types of reports for current period
   */
  async generateComprehensiveReports(exportFormats = ['csv', 'pdf']) {
    console.log('🚀 Starting comprehensive report generation...');
    
    const results = {
      timestamp: new Date().toISOString(),
      reports: {},
      summary: {
        total: 0,
        successful: 0,
        failed: 0
      }
    };

    try {
      // Generate all reports in parallel
      const reportPromises = [
        this.dailyGenerator.generateReport(null, exportFormats)
          .then(result => ({ type: 'daily', ...result }))
          .catch(error => ({ type: 'daily', success: false, error: error.message })),
        
        this.weeklyGenerator.generateReport(null, exportFormats)
          .then(result => ({ type: 'weekly', ...result }))
          .catch(error => ({ type: 'weekly', success: false, error: error.message })),
        
        this.monthlyGenerator.generateReport(null, exportFormats)
          .then(result => ({ type: 'monthly', ...result }))
          .catch(error => ({ type: 'monthly', success: false, error: error.message }))
      ];

      const reportResults = await Promise.all(reportPromises);

      // Process results
      reportResults.forEach(result => {
        results.reports[result.type] = result;
        results.summary.total++;
        
        if (result.success) {
          results.summary.successful++;
        } else {
          results.summary.failed++;
        }
      });

      console.log(`✅ Comprehensive report generation completed: ${results.summary.successful}/${results.summary.total} successful`);
      
      return results;

    } catch (error) {
      console.error('❌ Comprehensive report generation failed:', error);
      throw error;
    }
  }

  /**
   * Generate custom report with specific parameters
   */
  async generateCustomReport(config) {
    const {
      reportType = 'daily',
      startDate,
      endDate,
      exportFormats = ['csv'],
      includeInsights = true,
      customFilters = {}
    } = config;

    console.log(`🔧 Generating custom ${reportType} report...`);

    try {
      let dateRange;
      
      if (startDate && endDate) {
        dateRange = {
          start: startDate,
          end: endDate,
          label: `${startDate} to ${endDate}`
        };
      } else {
        dateRange = DateUtils.getDateRange(reportType, startDate);
      }

      // Fetch data with custom filters
      const rawData = await this.fetchCustomReportData(dateRange, customFilters);
      
      // Format data
      const formattedData = {
        metadata: ReportFormatter.formatReportMetadata(`Custom ${reportType} Report`, reportType, dateRange),
        summary: rawData.systemSummary,
        inventoryStatus: ReportFormatter.formatInventoryStatus(rawData.inventoryStatus),
        boxUtilization: ReportFormatter.formatBoxUtilization(rawData.boxUtilization),
        transactions: rawData.transactions,
        topActiveItems: rawData.topActiveItems,
        hourlyActivity: rawData.hourlyActivity
      };

      if (includeInsights) {
        formattedData.insights = this.generateCustomInsights(formattedData, customFilters);
      }

      // Export in requested formats
      const exportResults = {};
      
      if (exportFormats.includes('csv')) {
        exportResults.csv = await this.csvExporter.exportInventoryReport(
          formattedData, 
          'custom', 
          reportType
        );
      }
      
      if (exportFormats.includes('pdf')) {
        exportResults.pdf = await this.pdfExporter.exportToPDF(
          formattedData, 
          'custom', 
          reportType
        );
      }

      return {
        success: true,
        reportType: 'custom',
        config: config,
        data: formattedData,
        exports: exportResults
      };

    } catch (error) {
      console.error('❌ Custom report generation failed:', error);
      throw error;
    }
  }

  async fetchCustomReportData(dateRange, filters = {}) {
    const data = {};
    
    try {
      // Apply filters to queries if specified
      const [
        inventoryStatus,
        transactions,
        boxUtilization,
        topActiveItems,
        systemSummary,
        hourlyActivity
      ] = await Promise.all([
        ReportQueries.getInventoryStatusByDateRange(dateRange.start, dateRange.end),
        ReportQueries.getTransactionsByDateRange(dateRange.start, dateRange.end),
        ReportQueries.getBoxUtilizationByDateRange(dateRange.start, dateRange.end),
        ReportQueries.getTopActiveItems(dateRange.start, dateRange.end, filters.topItemsLimit || 10),
        ReportQueries.getSystemSummary(dateRange.start, dateRange.end),
        ReportQueries.getHourlyActivityDistribution(dateRange.start, dateRange.end)
      ]);

      // Apply additional filters if specified
      data.inventoryStatus = this.applyInventoryFilters(inventoryStatus, filters);
      data.transactions = this.applyTransactionFilters(transactions, filters);
      data.boxUtilization = this.applyBoxFilters(boxUtilization, filters);
      data.topActiveItems = topActiveItems;
      data.systemSummary = systemSummary;
      data.hourlyActivity = hourlyActivity;

      return data;

    } catch (error) {
      console.error('Error fetching custom report data:', error);
      throw error;
    }
  }

  applyInventoryFilters(inventory, filters) {
    let filtered = inventory;

    if (filters.minUtilization) {
      filtered = filtered.filter(item => {
        const utilization = item.total_quantity > 0 ? 
          (item.occupied_quantity / item.total_quantity) * 100 : 0;
        return utilization >= filters.minUtilization;
      });
    }

    if (filters.maxUtilization) {
      filtered = filtered.filter(item => {
        const utilization = item.total_quantity > 0 ? 
          (item.occupied_quantity / item.total_quantity) * 100 : 0;
        return utilization <= filters.maxUtilization;
      });
    }

    if (filters.itemIds && filters.itemIds.length > 0) {
      filtered = filtered.filter(item => filters.itemIds.includes(item.item_id));
    }

    return filtered;
  }

  applyTransactionFilters(transactions, filters) {
    let filtered = transactions;

    if (filters.action) {
      filtered = filtered.filter(transaction => transaction.action === filters.action);
    }

    if (filters.itemIds && filters.itemIds.length > 0) {
      filtered = filtered.filter(transaction => filters.itemIds.includes(transaction.item_id));
    }

    if (filters.minTransactionCount) {
      // Group by item and filter by transaction count
      const itemCounts = {};
      filtered.forEach(transaction => {
        if (!itemCounts[transaction.item_id]) itemCounts[transaction.item_id] = 0;
        itemCounts[transaction.item_id]++;
      });

      const validItems = Object.keys(itemCounts).filter(itemId => 
        itemCounts[itemId] >= filters.minTransactionCount
      );

      filtered = filtered.filter(transaction => validItems.includes(transaction.item_id));
    }

    return filtered;
  }

  applyBoxFilters(boxes, filters) {
    let filtered = boxes;

    if (filters.location) {
      filtered = filtered.filter(box => 
        box.location && box.location.toLowerCase().includes(filters.location.toLowerCase())
      );
    }

    if (filters.minCapacity) {
      filtered = filtered.filter(box => box.total_compartments >= filters.minCapacity);
    }

    if (filters.utilizationThreshold) {
      filtered = filtered.filter(box => {
        const utilization = box.total_compartments > 0 ? 
          (box.occupied_compartments / box.total_compartments) * 100 : 0;
        return utilization >= filters.utilizationThreshold;
      });
    }

    return filtered;
  }

  generateCustomInsights(data, filters) {
    const insights = [];

    // Filter-specific insights
    if (filters.minUtilization || filters.maxUtilization) {
      const count = data.inventoryStatus ? data.inventoryStatus.length : 0;
      insights.push(`Filtered inventory: ${count} items meet utilization criteria`);
    }

    if (filters.action) {
      const count = data.transactions ? data.transactions.length : 0;
      insights.push(`Filtered transactions: ${count} ${filters.action} actions in period`);
    }

    if (filters.location) {
      const count = data.boxUtilization ? data.boxUtilization.length : 0;
      insights.push(`Location filter: ${count} boxes in "${filters.location}" area`);
    }

    // General insights
    if (data.topActiveItems && data.topActiveItems.length > 0) {
      const topItem = data.topActiveItems[0];
      insights.push(`Most active item: ${topItem.item_name} with ${topItem.total_activities} activities`);
    }

    return insights;
  }

  /**
   * Get reports statistics and health information
   */
  async getReportsHealth() {
    try {
      const { testConnection } = require('./config/db');
      await testConnection();

      const fs = require('fs-extra');
      const path = require('path');
      const outputDir = path.join(__dirname, 'output');

      let totalFiles = 0;
      let totalSize = 0;

      // Count CSV files
      const csvDir = path.join(outputDir, 'csv');
      if (await fs.pathExists(csvDir)) {
        const csvFiles = await fs.readdir(csvDir);
        totalFiles += csvFiles.length;
        
        for (const file of csvFiles) {
          const stats = await fs.stat(path.join(csvDir, file));
          totalSize += stats.size;
        }
      }

      // Count PDF files
      const pdfDir = path.join(outputDir, 'pdf');
      if (await fs.pathExists(pdfDir)) {
        const pdfFiles = await fs.readdir(pdfDir);
        totalFiles += pdfFiles.length;
        
        for (const file of pdfFiles) {
          const stats = await fs.stat(path.join(pdfDir, file));
          totalSize += stats.size;
        }
      }

      return {
        status: 'healthy',
        database: 'connected',
        totalReportsGenerated: totalFiles,
        totalStorageUsed: totalSize,
        storageUsedFormatted: this.formatFileSize(totalSize),
        outputDirectory: outputDir,
        lastChecked: new Date().toISOString()
      };

    } catch (error) {
      return {
        status: 'unhealthy',
        error: error.message,
        lastChecked: new Date().toISOString()
      };
    }
  }

  formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  /**
   * Cleanup old reports
   */
  async cleanupReports(olderThanDays = 30) {
    try {
      const fs = require('fs-extra');
      const path = require('path');
      const outputDir = path.join(__dirname, 'output');
      
      const cutoffDate = new Date();
      cutoffDate.setDate(cutoffDate.getDate() - olderThanDays);
      
      let deletedCount = 0;
      let freedSpace = 0;
      
      for (const subDir of ['csv', 'pdf']) {
        const dirPath = path.join(outputDir, subDir);
        
        if (await fs.pathExists(dirPath)) {
          const files = await fs.readdir(dirPath);
          
          for (const file of files) {
            const filePath = path.join(dirPath, file);
            const stats = await fs.stat(filePath);
            
            if (stats.birthtime < cutoffDate) {
              freedSpace += stats.size;
              await fs.remove(filePath);
              deletedCount++;
            }
          }
        }
      }

      console.log(`🧹 Cleanup completed: ${deletedCount} files deleted, ${this.formatFileSize(freedSpace)} freed`);

      return {
        success: true,
        deletedFiles: deletedCount,
        freedSpace: freedSpace,
        freedSpaceFormatted: this.formatFileSize(freedSpace),
        cutoffDate: cutoffDate.toISOString()
      };

    } catch (error) {
      console.error('❌ Cleanup failed:', error);
      throw error;
    }
  }
}

module.exports = ReportsManager;
