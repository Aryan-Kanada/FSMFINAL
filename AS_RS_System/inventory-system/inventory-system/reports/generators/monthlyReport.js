const ReportQueries = require('../utils/reportQueries');
const ReportFormatter = require('../utils/reportFormatter');
const DateUtils = require('../utils/dateUtils');
const CSVExporter = require('../exporters/csvExporter');
const PDFExporter = require('../exporters/pdfExporter');

class MonthlyReportGenerator {
  constructor() {
    this.csvExporter = new CSVExporter();
    this.pdfExporter = new PDFExporter();
  }

  async generateReport(targetDate = null, exportFormats = ['csv', 'pdf']) {
    try {
      console.log('🔄 Generating Monthly Inventory Report...');
      
      // Get date range for the month
      const dateRange = DateUtils.getDateRange('monthly', targetDate);
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
          'monthly', 
          'report'
        );
      }
      
      if (exportFormats.includes('pdf')) {
        exportResults.pdf = await this.pdfExporter.exportToPDF(
          formattedData, 
          'monthly', 
          'report'
        );
      }

      console.log('✅ Monthly report generated successfully');
      
      return {
        success: true,
        reportType: 'monthly',
        period: dateRange.label,
        data: formattedData,
        exports: exportResults
      };

    } catch (error) {
      console.error('❌ Error generating monthly report:', error);
      throw new Error(`Monthly report generation failed: ${error.message}`);
    } finally {
      await this.pdfExporter.closeBrowser();
    }
  }

  async fetchReportData(dateRange) {
    console.log('📊 Fetching monthly report data...');
    
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
        weeklyBreakdown,
        monthlyTrends
      ] = await Promise.all([
        ReportQueries.getInventoryStatusByDateRange(dateRange.start, dateRange.end),
        ReportQueries.getTransactionsByDateRange(dateRange.start, dateRange.end),
        ReportQueries.getBoxUtilizationByDateRange(dateRange.start, dateRange.end),
        ReportQueries.getTopActiveItems(dateRange.start, dateRange.end, 20),
        ReportQueries.getSystemSummary(dateRange.start, dateRange.end),
        ReportQueries.getHourlyActivityDistribution(dateRange.start, dateRange.end),
        this.getWeeklyBreakdown(dateRange),
        this.getMonthlyTrends(dateRange)
      ]);

      data.inventoryStatus = inventoryStatus;
      data.transactions = transactions;
      data.boxUtilization = boxUtilization;
      data.topActiveItems = topActiveItems;
      data.systemSummary = systemSummary;
      data.hourlyActivity = hourlyActivity;
      data.weeklyBreakdown = weeklyBreakdown;
      data.monthlyTrends = monthlyTrends;

      console.log(`✅ Monthly data fetched - ${transactions.length} transactions, ${inventoryStatus.length} items`);
      
      return data;

    } catch (error) {
      console.error('Error fetching monthly report data:', error);
      throw error;
    }
  }

  async getWeeklyBreakdown(dateRange) {
    try {
      const { pool } = require('../config/db');
      const query = `
        SELECT 
          YEAR(time) as year,
          WEEK(time) as week,
          COUNT(*) as total_transactions,
          COUNT(CASE WHEN action = 'added' THEN 1 END) as additions,
          COUNT(CASE WHEN action = 'retrieved' THEN 1 END) as retrievals,
          MIN(DATE(time)) as week_start,
          MAX(DATE(time)) as week_end
        FROM Transactions
        WHERE time BETWEEN ? AND ?
        GROUP BY YEAR(time), WEEK(time)
        ORDER BY year, week
      `;
      
      const [rows] = await pool.execute(query, [dateRange.start, dateRange.end]);
      return rows;
    } catch (error) {
      console.error('Error fetching weekly breakdown:', error);
      return [];
    }
  }

  async getMonthlyTrends(currentDateRange) {
    try {
      const { pool } = require('../config/db');
      
      // Get previous month for comparison
      const currentMonth = new Date(currentDateRange.start);
      const previousMonth = new Date(currentMonth);
      previousMonth.setMonth(previousMonth.getMonth() - 1);
      
      const prevDateRange = DateUtils.getDateRange('monthly', previousMonth);
      
      // Fetch current and previous month summaries
      const [currentSummary, previousSummary] = await Promise.all([
        ReportQueries.getSystemSummary(currentDateRange.start, currentDateRange.end),
        ReportQueries.getSystemSummary(prevDateRange.start, prevDateRange.end)
      ]);

      // Calculate trends
      const trends = {
        transactions: ReportFormatter.calculateTrends(currentSummary, previousSummary, 'transactionsInPeriod'),
        additions: ReportFormatter.calculateTrends(currentSummary, previousSummary, 'additionsInPeriod'),
        retrievals: ReportFormatter.calculateTrends(currentSummary, previousSummary, 'retrievalsInPeriod'),
        utilization: ReportFormatter.calculateTrends(
          { utilization: parseFloat(currentSummary.overallUtilization) },
          { utilization: parseFloat(previousSummary.overallUtilization) },
          'utilization'
        )
      };

      return {
        current: currentSummary,
        previous: previousSummary,
        trends: trends,
        comparisonPeriod: prevDateRange.label
      };

    } catch (error) {
      console.error('Error calculating monthly trends:', error);
      return null;
    }
  }

  async formatReportData(rawData, dateRange) {
    console.log('🔧 Formatting monthly report data...');
    
    const formattedData = {
      metadata: ReportFormatter.formatReportMetadata('Monthly Report', 'monthly', dateRange),
      summary: rawData.systemSummary,
      inventoryStatus: ReportFormatter.formatInventoryStatus(rawData.inventoryStatus),
      boxUtilization: ReportFormatter.formatBoxUtilization(rawData.boxUtilization),
      transactions: rawData.transactions,
      topActiveItems: rawData.topActiveItems,
      hourlyActivity: rawData.hourlyActivity,
      weeklyBreakdown: rawData.weeklyBreakdown,
      monthlyTrends: rawData.monthlyTrends,
      transactionSummary: ReportFormatter.formatTransactionSummary(rawData.transactions),
      performanceMetrics: this.calculatePerformanceMetrics(rawData)
    };

    // Add monthly-specific insights
    formattedData.insights = this.generateMonthlyInsights(formattedData);
    
    return formattedData;
  }

  calculatePerformanceMetrics(rawData) {
    const metrics = {};
    
    // Calculate average daily transactions
    if (rawData.weeklyBreakdown && rawData.weeklyBreakdown.length > 0) {
      const totalTransactions = rawData.weeklyBreakdown.reduce((sum, week) => sum + week.total_transactions, 0);
      const totalDays = rawData.weeklyBreakdown.reduce((sum, week) => {
        const start = new Date(week.week_start);
        const end = new Date(week.week_end);
        return sum + Math.ceil((end - start) / (1000 * 60 * 60 * 24)) + 1;
      }, 0);
      
      metrics.averageDailyTransactions = totalDays > 0 ? (totalTransactions / totalDays).toFixed(1) : 0;
      metrics.averageWeeklyTransactions = rawData.weeklyBreakdown.length > 0 ? 
        (totalTransactions / rawData.weeklyBreakdown.length).toFixed(1) : 0;
    }

    // Calculate peak performance metrics
    if (rawData.hourlyActivity && rawData.hourlyActivity.length > 0) {
      const totalHourlyTransactions = rawData.hourlyActivity.reduce((sum, hour) => sum + hour.total_transactions, 0);
      const activeHours = rawData.hourlyActivity.filter(hour => hour.total_transactions > 0).length;
      
      metrics.peakHourActivity = Math.max(...rawData.hourlyActivity.map(h => h.total_transactions));
      metrics.averageHourlyActivity = activeHours > 0 ? (totalHourlyTransactions / activeHours).toFixed(1) : 0;
    }

    // Calculate inventory turnover metrics
    if (rawData.inventoryStatus && rawData.inventoryStatus.length > 0) {
      const totalItems = rawData.inventoryStatus.reduce((sum, item) => sum + (item.total_quantity || 0), 0);
      const occupiedItems = rawData.inventoryStatus.reduce((sum, item) => sum + (item.occupied_quantity || 0), 0);
      
      metrics.inventoryTurnover = totalItems > 0 ? ((occupiedItems / totalItems) * 100).toFixed(1) + '%' : '0%';
      
      const highUtilizationItems = rawData.inventoryStatus.filter(item => 
        item.total_quantity > 0 && (item.occupied_quantity / item.total_quantity) > 0.8
      ).length;
      
      metrics.highUtilizationItems = highUtilizationItems;
      metrics.highUtilizationPercentage = rawData.inventoryStatus.length > 0 ? 
        ((highUtilizationItems / rawData.inventoryStatus.length) * 100).toFixed(1) + '%' : '0%';
    }

    return metrics;
  }

  generateMonthlyInsights(data) {
    const insights = [];
    
    // Monthly trend insights
    if (data.monthlyTrends && data.monthlyTrends.trends) {
      const trends = data.monthlyTrends.trends;
      
      insights.push(`Transaction trend: ${trends.transactions.trend} by ${Math.abs(trends.transactions.change)} transactions (${trends.transactions.percentage_change}) vs last month`);
      
      if (trends.utilization.trend !== 'stable') {
        insights.push(`Storage utilization ${trends.utilization.trend} by ${trends.utilization.percentage_change} compared to last month`);
      }
    }

    // Performance insights
    if (data.performanceMetrics) {
      const metrics = data.performanceMetrics;
      insights.push(`Average daily activity: ${metrics.averageDailyTransactions} transactions`);
      
      if (metrics.highUtilizationItems > 0) {
        insights.push(`${metrics.highUtilizationItems} items (${metrics.highUtilizationPercentage}) are running high utilization (>80%)`);
      }
    }

    // Weekly pattern insights
    if (data.weeklyBreakdown && data.weeklyBreakdown.length > 0) {
      const weeks = data.weeklyBreakdown;
      const bestWeek = weeks.reduce((max, current) => 
        current.total_transactions > max.total_transactions ? current : max
      );
      const quietWeek = weeks.reduce((min, current) => 
        current.total_transactions < min.total_transactions ? current : min
      );
      
      insights.push(`Peak week: ${bestWeek.week_start} to ${bestWeek.week_end} with ${bestWeek.total_transactions} transactions`);
      
      if (bestWeek.total_transactions !== quietWeek.total_transactions) {
        insights.push(`Quietest week: ${quietWeek.week_start} to ${quietWeek.week_end} with ${quietWeek.total_transactions} transactions`);
      }
    }

    // Top performers insight
    if (data.topActiveItems && data.topActiveItems.length > 0) {
      const topThree = data.topActiveItems.slice(0, 3);
      const topItemsText = topThree.map(item => `${item.item_name} (${item.total_activities})`).join(', ');
      insights.push(`Top active items: ${topItemsText}`);
    }

    // Capacity management insight
    if (data.boxUtilization) {
      const totalBoxes = data.boxUtilization.length;
      const fullBoxes = data.boxUtilization.filter(box => box.status === 'Full').length;
      const highCapacityBoxes = data.boxUtilization.filter(box => 
        parseFloat(box.utilization_rate) > 90
      ).length;
      
      if (fullBoxes > 0 || highCapacityBoxes > 0) {
        insights.push(`Capacity management: ${fullBoxes} full boxes, ${highCapacityBoxes} boxes >90% capacity of ${totalBoxes} total`);
      }
    }

    return insights;
  }

  async generateMultipleMonths(months = 6, exportFormats = ['csv', 'pdf']) {
    console.log(`🔄 Generating monthly reports for the last ${months} months...`);
    
    const results = [];
    const monthRanges = DateUtils.getLastNMonths(months);
    
    for (const monthRange of monthRanges) {
      try {
        console.log(`\n📅 Processing ${monthRange.label}...`);
        const result = await this.generateReport(monthRange.start, exportFormats);
        results.push(result);
      } catch (error) {
        console.error(`❌ Failed to generate report for ${monthRange.label}:`, error.message);
        results.push({
          success: false,
          period: monthRange.label,
          error: error.message
        });
      }
    }
    
    console.log(`\n✅ Completed ${months}-month report generation`);
    return results;
  }

  async generateYearlyComparison(year = null) {
    try {
      const targetYear = year || new Date().getFullYear();
      console.log(`🔄 Generating yearly comparison report for ${targetYear}...`);
      
      const yearlyData = await this.getYearlyData(targetYear);
      const comparison = await this.compareWithPreviousYear(targetYear);
      
      const formattedData = {
        metadata: {
          report_type: 'Yearly Comparison Report',
          year: targetYear,
          generated_at: new Date().toISOString()
        },
        yearlyData: yearlyData,
        comparison: comparison,
        insights: this.generateYearlyInsights(yearlyData, comparison)
      };

      // Export yearly comparison
      const exportResults = {};
      exportResults.csv = await this.csvExporter.exportCustomData(
        yearlyData.monthlyBreakdown,
        `yearly_comparison_${targetYear}`,
        [
          { id: 'month', title: 'Month' },
          { id: 'total_transactions', title: 'Total Transactions' },
          { id: 'additions', title: 'Additions' },
          { id: 'retrievals', title: 'Retrievals' },
          { id: 'avg_daily_transactions', title: 'Avg Daily Transactions' }
        ]
      );

      return {
        success: true,
        reportType: 'yearly_comparison',
        year: targetYear,
        data: formattedData,
        exports: exportResults
      };

    } catch (error) {
      console.error('❌ Error generating yearly comparison:', error);
      throw new Error(`Yearly comparison generation failed: ${error.message}`);
    }
  }

  async getYearlyData(year) {
    const { pool } = require('../config/db');
    
    const query = `
      SELECT 
        YEAR(time) as year,
        MONTH(time) as month,
        COUNT(*) as total_transactions,
        COUNT(CASE WHEN action = 'added' THEN 1 END) as additions,
        COUNT(CASE WHEN action = 'retrieved' THEN 1 END) as retrievals,
        COUNT(*) / DAY(LAST_DAY(DATE(time))) as avg_daily_transactions
      FROM Transactions
      WHERE YEAR(time) = ?
      GROUP BY YEAR(time), MONTH(time)
      ORDER BY month
    `;
    
    const [rows] = await pool.execute(query, [year]);
    
    // Fill in missing months with zero values
    const monthlyData = [];
    for (let month = 1; month <= 12; month++) {
      const existingData = rows.find(row => row.month === month);
      monthlyData.push({
        month: month,
        month_name: new Date(year, month - 1).toLocaleString('default', { month: 'long' }),
        total_transactions: existingData ? existingData.total_transactions : 0,
        additions: existingData ? existingData.additions : 0,
        retrievals: existingData ? existingData.retrievals : 0,
        avg_daily_transactions: existingData ? parseFloat(existingData.avg_daily_transactions).toFixed(1) : 0
      });
    }
    
    return {
      year: year,
      monthlyBreakdown: monthlyData,
      totalTransactions: monthlyData.reduce((sum, month) => sum + month.total_transactions, 0),
      totalAdditions: monthlyData.reduce((sum, month) => sum + month.additions, 0),
      totalRetrievals: monthlyData.reduce((sum, month) => sum + month.retrievals, 0)
    };
  }

  async compareWithPreviousYear(currentYear) {
    const previousYear = currentYear - 1;
    
    try {
      const [currentYearData, previousYearData] = await Promise.all([
        this.getYearlyData(currentYear),
        this.getYearlyData(previousYear)
      ]);

      const comparison = {
        transactions: ReportFormatter.calculateTrends(
          { transactionsInPeriod: currentYearData.totalTransactions },
          { transactionsInPeriod: previousYearData.totalTransactions },
          'transactionsInPeriod'
        ),
        additions: ReportFormatter.calculateTrends(
          { additionsInPeriod: currentYearData.totalAdditions },
          { additionsInPeriod: previousYearData.totalAdditions },
          'additionsInPeriod'
        ),
        retrievals: ReportFormatter.calculateTrends(
          { retrievalsInPeriod: currentYearData.totalRetrievals },
          { retrievalsInPeriod: previousYearData.totalRetrievals },
          'retrievalsInPeriod'
        )
      };

      return {
        currentYear: currentYearData,
        previousYear: previousYearData,
        trends: comparison
      };

    } catch (error) {
      console.error('Error comparing with previous year:', error);
      return null;
    }
  }

  generateYearlyInsights(yearlyData, comparison) {
    const insights = [];
    
    if (comparison && comparison.trends) {
      const trends = comparison.trends;
      insights.push(`Year-over-year transaction change: ${trends.transactions.trend} by ${trends.transactions.percentage_change}`);
    }

    // Peak month analysis
    const peakMonth = yearlyData.monthlyBreakdown.reduce((max, current) => 
      current.total_transactions > max.total_transactions ? current : max
    );
    insights.push(`Peak activity month: ${peakMonth.month_name} with ${peakMonth.total_transactions} transactions`);

    // Seasonal patterns
    const quarters = {
      Q1: yearlyData.monthlyBreakdown.slice(0, 3).reduce((sum, month) => sum + month.total_transactions, 0),
      Q2: yearlyData.monthlyBreakdown.slice(3, 6).reduce((sum, month) => sum + month.total_transactions, 0),
      Q3: yearlyData.monthlyBreakdown.slice(6, 9).reduce((sum, month) => sum + month.total_transactions, 0),
      Q4: yearlyData.monthlyBreakdown.slice(9, 12).reduce((sum, month) => sum + month.total_transactions, 0)
    };

    const peakQuarter = Object.entries(quarters).reduce((max, current) => 
      current[1] > max[1] ? current : max
    );
    insights.push(`Peak quarter: ${peakQuarter[0]} with ${peakQuarter[1]} transactions`);

    return insights;
  }
}

module.exports = MonthlyReportGenerator;
