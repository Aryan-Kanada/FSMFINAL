const ReportQueries = require('../utils/reportQueries');
const ReportFormatter = require('../utils/reportFormatter');
const DateUtils = require('../utils/dateUtils');
const CSVExporter = require('../exporters/csvExporter');
const PDFExporter = require('../exporters/pdfExporter');

class DailyReportGenerator {
  constructor() {
    this.csvExporter = new CSVExporter();
    this.pdfExporter = new PDFExporter();
  }

  async generateReport(targetDate = null, exportFormats = ['csv', 'pdf']) {
    try {
      console.log('🔄 Generating Daily Inventory Report...');
      
      // Get date range for the day
      const dateRange = DateUtils.getDateRange('daily', targetDate);
      console.log(`📅 Report period: ${dateRange.label}`);

      // Fetch data from database
      const rawData = await this.fetchReportData(dateRange);
      
      // Format data for report
      const formattedData = await this.formatReportData(rawData, dateRange);
      
      // Export in requested formats
      const exportResults = {};
      
      if (exportFormats.includes('csv')) {
        exportResults.csv = await this.csvExporter.exportInventoryReport(
          formattedData, 
          'daily', 
          'report'
        );
      }
      
      if (exportFormats.includes('pdf')) {
        exportResults.pdf = await this.pdfExporter.exportToPDF(
          formattedData, 
          'daily', 
          'report'
        );
      }

      console.log('✅ Daily report generated successfully');
      
      return {
        success: true,
        reportType: 'daily',
        period: dateRange.label,
        data: formattedData,
        exports: exportResults
      };

    } catch (error) {
      console.error('❌ Error generating daily report:', error);
      throw new Error(`Daily report generation failed: ${error.message}`);
    } finally {
      await this.pdfExporter.closeBrowser();
    }
  }

  async fetchReportData(dateRange) {
    console.log('📊 Fetching report data...');
    
    const data = {};
    
    try {
      // Fetch all required data in parallel
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
        ReportQueries.getTopActiveItems(dateRange.start, dateRange.end, 10),
        ReportQueries.getSystemSummary(dateRange.start, dateRange.end),
        ReportQueries.getHourlyActivityDistribution(dateRange.start, dateRange.end)
      ]);

      data.inventoryStatus = inventoryStatus;
      data.transactions = transactions;
      data.boxUtilization = boxUtilization;
      data.topActiveItems = topActiveItems;
      data.systemSummary = systemSummary;
      data.hourlyActivity = hourlyActivity;

      console.log(`✅ Data fetched - ${transactions.length} transactions, ${inventoryStatus.length} items`);
      
      return data;

    } catch (error) {
      console.error('Error fetching report data:', error);
      throw error;
    }
  }

  async formatReportData(rawData, dateRange) {
    console.log('🔧 Formatting report data...');
    
    const formattedData = {
      metadata: ReportFormatter.formatReportMetadata('Daily Report', 'daily', dateRange),
      summary: rawData.systemSummary,
      inventoryStatus: ReportFormatter.formatInventoryStatus(rawData.inventoryStatus),
      boxUtilization: ReportFormatter.formatBoxUtilization(rawData.boxUtilization),
      transactions: rawData.transactions,
      topActiveItems: rawData.topActiveItems,
      hourlyActivity: rawData.hourlyActivity,
      transactionSummary: ReportFormatter.formatTransactionSummary(rawData.transactions)
    };

    // Add daily-specific insights
    formattedData.insights = this.generateDailyInsights(formattedData);
    
    return formattedData;
  }

  generateDailyInsights(data) {
    const insights = [];
    
    // Peak activity hour
    if (data.hourlyActivity && data.hourlyActivity.length > 0) {
      const peakHour = data.hourlyActivity.reduce((max, current) => 
        current.total_transactions > max.total_transactions ? current : max
      );
      insights.push(`Peak activity hour: ${peakHour.hour}:00 with ${peakHour.total_transactions} transactions`);
    }

    // Most active item
    if (data.topActiveItems && data.topActiveItems.length > 0) {
      const topItem = data.topActiveItems[0];
      insights.push(`Most active item: ${topItem.item_name} with ${topItem.total_activities} activities`);
    }

    // Box utilization alert
    if (data.boxUtilization) {
      const fullBoxes = data.boxUtilization.filter(box => box.status === 'Full').length;
      if (fullBoxes > 0) {
        insights.push(`Alert: ${fullBoxes} box(es) are at full capacity`);
      }
    }

    // Transaction pattern
    const totalTransactions = data.summary?.transactionsInPeriod || 0;
    const additions = data.summary?.additionsInPeriod || 0;
    const retrievals = data.summary?.retrievalsInPeriod || 0;
    
    if (totalTransactions > 0) {
      const additionPercentage = ((additions / totalTransactions) * 100).toFixed(1);
      insights.push(`Activity split: ${additionPercentage}% additions, ${(100 - additionPercentage)}% retrievals`);
    }

    return insights;
  }

  async generateMultipleDays(days = 7, exportFormats = ['csv', 'pdf']) {
    console.log(`🔄 Generating daily reports for the last ${days} days...`);
    
    const results = [];
    const dates = DateUtils.getLastNDays(days);
    
    for (const date of dates) {
      try {
        console.log(`\n📅 Processing ${date}...`);
        const result = await this.generateReport(date, exportFormats);
        results.push(result);
      } catch (error) {
        console.error(`❌ Failed to generate report for ${date}:`, error.message);
        results.push({
          success: false,
          date: date,
          error: error.message
        });
      }
    }
    
    console.log(`\n✅ Completed ${days}-day report generation`);
    return results;
  }
}

module.exports = DailyReportGenerator;
