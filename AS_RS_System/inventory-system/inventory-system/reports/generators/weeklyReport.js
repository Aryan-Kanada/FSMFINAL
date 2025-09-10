const ReportQueries = require('../utils/reportQueries');
const ReportFormatter = require('../utils/reportFormatter');
const DateUtils = require('../utils/dateUtils');
const CSVExporter = require('../exporters/csvExporter');
const PDFExporter = require('../exporters/pdfExporter');

class WeeklyReportGenerator {
  constructor() {
    this.csvExporter = new CSVExporter();
    this.pdfExporter = new PDFExporter();
  }

  async generateReport(targetDate = null, exportFormats = ['csv', 'pdf']) {
    try {
      console.log('🔄 Generating Weekly Inventory Report...');
      
      // Get date range for the week
      const dateRange = DateUtils.getDateRange('weekly', targetDate);
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
          'weekly', 
          'report'
        );
      }
      
      if (exportFormats.includes('pdf')) {
        exportResults.pdf = await this.pdfExporter.exportToPDF(
          formattedData, 
          'weekly', 
          'report'
        );
      }

      console.log('✅ Weekly report generated successfully');
      
      return {
        success: true,
        reportType: 'weekly',
        period: dateRange.label,
        data: formattedData,
        exports: exportResults
      };

    } catch (error) {
      console.error('❌ Error generating weekly report:', error);
      throw new Error(`Weekly report generation failed: ${error.message}`);
    } finally {
      await this.pdfExporter.closeBrowser();
    }
  }

  async fetchReportData(dateRange) {
    console.log('📊 Fetching weekly report data...');
    
    const data = {};
    
    try {
      // Fetch all required data in parallel
      const [
        inventoryStatus,
        transactions,
        boxUtilization,
        topActiveItems,
        systemSummary,
        hourlyActivity,
        dailyBreakdown
      ] = await Promise.all([
        ReportQueries.getInventoryStatusByDateRange(dateRange.start, dateRange.end),
        ReportQueries.getTransactionsByDateRange(dateRange.start, dateRange.end),
        ReportQueries.getBoxUtilizationByDateRange(dateRange.start, dateRange.end),
        ReportQueries.getTopActiveItems(dateRange.start, dateRange.end, 15),
        ReportQueries.getSystemSummary(dateRange.start, dateRange.end),
        ReportQueries.getHourlyActivityDistribution(dateRange.start, dateRange.end),
        this.getDailyBreakdown(dateRange)
      ]);

      data.inventoryStatus = inventoryStatus;
      data.transactions = transactions;
      data.boxUtilization = boxUtilization;
      data.topActiveItems = topActiveItems;
      data.systemSummary = systemSummary;
      data.hourlyActivity = hourlyActivity;
      data.dailyBreakdown = dailyBreakdown;

      console.log(`✅ Weekly data fetched - ${transactions.length} transactions, ${inventoryStatus.length} items`);
      
      return data;

    } catch (error) {
      console.error('Error fetching weekly report data:', error);
      throw error;
    }
  }

  async getDailyBreakdown(dateRange) {
    try {
      const { pool } = require('../config/db');
      const query = `
        SELECT 
          DATE(time) as date,
          COUNT(*) as total_transactions,
          COUNT(CASE WHEN action = 'added' THEN 1 END) as additions,
          COUNT(CASE WHEN action = 'retrieved' THEN 1 END) as retrievals
        FROM Transactions
        WHERE time BETWEEN ? AND ?
        GROUP BY DATE(time)
        ORDER BY date
      `;
      
      const [rows] = await pool.execute(query, [dateRange.start, dateRange.end]);
      return rows;
    } catch (error) {
      console.error('Error fetching daily breakdown:', error);
      return [];
    }
  }

  async formatReportData(rawData, dateRange) {
    console.log('🔧 Formatting weekly report data...');
    
    const formattedData = {
      metadata: ReportFormatter.formatReportMetadata('Weekly Report', 'weekly', dateRange),
      summary: rawData.systemSummary,
      inventoryStatus: ReportFormatter.formatInventoryStatus(rawData.inventoryStatus),
      boxUtilization: ReportFormatter.formatBoxUtilization(rawData.boxUtilization),
      transactions: rawData.transactions,
      topActiveItems: rawData.topActiveItems,
      hourlyActivity: rawData.hourlyActivity,
      dailyBreakdown: rawData.dailyBreakdown,
      transactionSummary: ReportFormatter.formatTransactionSummary(rawData.transactions),
      weeklyTrends: this.calculateWeeklyTrends(rawData.dailyBreakdown)
    };

    // Add weekly-specific insights
    formattedData.insights = this.generateWeeklyInsights(formattedData);
    
    return formattedData;
  }

  calculateWeeklyTrends(dailyBreakdown) {
    if (!dailyBreakdown || dailyBreakdown.length < 2) return null;

    const trends = {
      averageDailyTransactions: 0,
      peakDay: null,
      quietDay: null,
      growthTrend: 'stable',
      weekdayVsWeekend: { weekday: 0, weekend: 0 }
    };

    // Calculate averages
    const totalTransactions = dailyBreakdown.reduce((sum, day) => sum + day.total_transactions, 0);
    trends.averageDailyTransactions = (totalTransactions / dailyBreakdown.length).toFixed(1);

    // Find peak and quiet days
    trends.peakDay = dailyBreakdown.reduce((max, current) => 
      current.total_transactions > max.total_transactions ? current : max
    );
    trends.quietDay = dailyBreakdown.reduce((min, current) => 
      current.total_transactions < min.total_transactions ? current : min
    );

    // Calculate weekday vs weekend
    dailyBreakdown.forEach(day => {
      const dayOfWeek = new Date(day.date).getDay();
      if (dayOfWeek === 0 || dayOfWeek === 6) { // Sunday or Saturday
        trends.weekdayVsWeekend.weekend += day.total_transactions;
      } else {
        trends.weekdayVsWeekend.weekday += day.total_transactions;
      }
    });

    // Determine growth trend (comparing first half vs second half of week)
    const midPoint = Math.floor(dailyBreakdown.length / 2);
    const firstHalf = dailyBreakdown.slice(0, midPoint);
    const secondHalf = dailyBreakdown.slice(midPoint);
    
    const firstHalfAvg = firstHalf.reduce((sum, day) => sum + day.total_transactions, 0) / firstHalf.length;
    const secondHalfAvg = secondHalf.reduce((sum, day) => sum + day.total_transactions, 0) / secondHalf.length;
    
    if (secondHalfAvg > firstHalfAvg * 1.1) {
      trends.growthTrend = 'increasing';
    } else if (secondHalfAvg < firstHalfAvg * 0.9) {
      trends.growthTrend = 'decreasing';
    }

    return trends;
  }

  generateWeeklyInsights(data) {
    const insights = [];
    
    // Weekly trend insight
    if (data.weeklyTrends) {
      const trends = data.weeklyTrends;
      insights.push(`Average daily transactions: ${trends.averageDailyTransactions}`);
      insights.push(`Peak activity day: ${trends.peakDay?.date} with ${trends.peakDay?.total_transactions} transactions`);
      insights.push(`Activity trend: ${trends.growthTrend} throughout the week`);
      
      // Weekday vs weekend comparison
      const totalWeekdayVsWeekend = trends.weekdayVsWeekend.weekday + trends.weekdayVsWeekend.weekend;
      if (totalWeekdayVsWeekend > 0) {
        const weekdayPercentage = ((trends.weekdayVsWeekend.weekday / totalWeekdayVsWeekend) * 100).toFixed(1);
        insights.push(`Weekday vs Weekend activity: ${weekdayPercentage}% weekdays, ${(100 - weekdayPercentage)}% weekends`);
      }
    }

    // Most active item for the week
    if (data.topActiveItems && data.topActiveItems.length > 0) {
      const topItem = data.topActiveItems[0];
      insights.push(`Top item this week: ${topItem.item_name} with ${topItem.total_activities} activities`);
    }

    // Box capacity warnings
    if (data.boxUtilization) {
      const fullBoxes = data.boxUtilization.filter(box => box.status === 'Full').length;
      const highUtilization = data.boxUtilization.filter(box => 
        parseFloat(box.utilization_rate) > 80
      ).length;
      
      if (fullBoxes > 0) {
        insights.push(`Capacity alert: ${fullBoxes} box(es) at full capacity`);
      }
      if (highUtilization > fullBoxes) {
        insights.push(`${highUtilization - fullBoxes} additional box(es) above 80% capacity`);
      }
    }

    // Peak hour analysis
    if (data.hourlyActivity && data.hourlyActivity.length > 0) {
      const peakHours = data.hourlyActivity
        .filter(hour => hour.total_transactions > 0)
        .sort((a, b) => b.total_transactions - a.total_transactions)
        .slice(0, 3);
      
      if (peakHours.length > 0) {
        const topHours = peakHours.map(h => `${h.hour}:00`).join(', ');
        insights.push(`Peak activity hours: ${topHours}`);
      }
    }

    return insights;
  }

  async generateMultipleWeeks(weeks = 4, exportFormats = ['csv', 'pdf']) {
    console.log(`🔄 Generating weekly reports for the last ${weeks} weeks...`);
    
    const results = [];
    const weekRanges = DateUtils.getLastNWeeks(weeks);
    
    for (const weekRange of weekRanges) {
      try {
        console.log(`\n📅 Processing ${weekRange.label}...`);
        const result = await this.generateReport(weekRange.start, exportFormats);
        results.push(result);
      } catch (error) {
        console.error(`❌ Failed to generate report for ${weekRange.label}:`, error.message);
        results.push({
          success: false,
          period: weekRange.label,
          error: error.message
        });
      }
    }
    
    console.log(`\n✅ Completed ${weeks}-week report generation`);
    return results;
  }
}

module.exports = WeeklyReportGenerator;
