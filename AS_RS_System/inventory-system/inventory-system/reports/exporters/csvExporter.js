const createCsvWriter = require('csv-writer').createObjectCsvWriter;
const path = require('path');
const fs = require('fs-extra');
const DateUtils = require('../utils/dateUtils');

class CSVExporter {
  constructor(outputDir = '../output') {
    this.outputDir = path.resolve(__dirname, outputDir);
    this.ensureOutputDirectory();
  }

  async ensureOutputDirectory() {
    await fs.ensureDir(this.outputDir);
    await fs.ensureDir(path.join(this.outputDir, 'csv'));
  }

  async exportInventoryReport(reportData, reportType, period) {
    try {
      const timestamp = DateUtils.formatDateForFilename();
      const filename = `inventory_${reportType}_${period}_${timestamp}.csv`;
      const filePath = path.join(this.outputDir, 'csv', filename);

      // Inventory Status CSV
      if (reportData.inventoryStatus && reportData.inventoryStatus.length > 0) {
        const inventoryPath = path.join(this.outputDir, 'csv', `inventory_status_${reportType}_${period}_${timestamp}.csv`);
        const inventoryCsvWriter = createCsvWriter({
          path: inventoryPath,
          header: [
            { id: 'item_id', title: 'Item ID' },
            { id: 'item_name', title: 'Item Name' },
            { id: 'total_quantity', title: 'Total Quantity' },
            { id: 'available_quantity', title: 'Available Quantity' },
            { id: 'occupied_quantity', title: 'Occupied Quantity' },
            { id: 'utilization_rate', title: 'Utilization Rate' },
            { id: 'last_updated', title: 'Last Updated' }
          ]
        });

        await inventoryCsvWriter.writeRecords(reportData.inventoryStatus);
        console.log(`✅ Inventory status CSV exported to: ${inventoryPath}`);
      }

      // Transactions CSV
      if (reportData.transactions && reportData.transactions.length > 0) {
        const transactionsPath = path.join(this.outputDir, 'csv', `transactions_${reportType}_${period}_${timestamp}.csv`);
        const transactionsCsvWriter = createCsvWriter({
          path: transactionsPath,
          header: [
            { id: 'tran_id', title: 'Transaction ID' },
            { id: 'item_id', title: 'Item ID' },
            { id: 'item_name', title: 'Item Name' },
            { id: 'subcom_place', title: 'Compartment Location' },
            { id: 'action', title: 'Action' },
            { id: 'time', title: 'Timestamp' }
          ]
        });

        await transactionsCsvWriter.writeRecords(reportData.transactions);
        console.log(`✅ Transactions CSV exported to: ${transactionsPath}`);
      }

      // Box Utilization CSV
      if (reportData.boxUtilization && reportData.boxUtilization.length > 0) {
        const boxPath = path.join(this.outputDir, 'csv', `box_utilization_${reportType}_${period}_${timestamp}.csv`);
        const boxCsvWriter = createCsvWriter({
          path: boxPath,
          header: [
            { id: 'box_id', title: 'Box ID' },
            { id: 'location', title: 'Location' },
            { id: 'total_compartments', title: 'Total Compartments' },
            { id: 'occupied_compartments', title: 'Occupied Compartments' },
            { id: 'available_compartments', title: 'Available Compartments' },
            { id: 'utilization_rate', title: 'Utilization Rate' },
            { id: 'status', title: 'Status' }
          ]
        });

        await boxCsvWriter.writeRecords(reportData.boxUtilization);
        console.log(`✅ Box utilization CSV exported to: ${boxPath}`);
      }

      // Top Active Items CSV
      if (reportData.topActiveItems && reportData.topActiveItems.length > 0) {
        const topItemsPath = path.join(this.outputDir, 'csv', `top_active_items_${reportType}_${period}_${timestamp}.csv`);
        const topItemsCsvWriter = createCsvWriter({
          path: topItemsPath,
          header: [
            { id: 'item_name', title: 'Item Name' },
            { id: 'total_activities', title: 'Total Activities' },
            { id: 'additions', title: 'Additions' },
            { id: 'retrievals', title: 'Retrievals' }
          ]
        });

        await topItemsCsvWriter.writeRecords(reportData.topActiveItems);
        console.log(`✅ Top active items CSV exported to: ${topItemsPath}`);
      }

      // Hourly Activity Distribution CSV
      if (reportData.hourlyActivity && reportData.hourlyActivity.length > 0) {
        const hourlyPath = path.join(this.outputDir, 'csv', `hourly_activity_${reportType}_${period}_${timestamp}.csv`);
        const hourlyCsvWriter = createCsvWriter({
          path: hourlyPath,
          header: [
            { id: 'hour', title: 'Hour' },
            { id: 'total_transactions', title: 'Total Transactions' },
            { id: 'additions', title: 'Additions' },
            { id: 'retrievals', title: 'Retrievals' }
          ]
        });

        await hourlyCsvWriter.writeRecords(reportData.hourlyActivity);
        console.log(`✅ Hourly activity CSV exported to: ${hourlyPath}`);
      }

      // Summary Report CSV
      if (reportData.summary) {
        const summaryPath = path.join(this.outputDir, 'csv', `summary_${reportType}_${period}_${timestamp}.csv`);
        const summaryData = Object.entries(reportData.summary).map(([key, value]) => ({
          metric: key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase()),
          value: value
        }));

        const summaryCsvWriter = createCsvWriter({
          path: summaryPath,
          header: [
            { id: 'metric', title: 'Metric' },
            { id: 'value', title: 'Value' }
          ]
        });

        await summaryCsvWriter.writeRecords(summaryData);
        console.log(`✅ Summary CSV exported to: ${summaryPath}`);
      }

      return {
        success: true,
        message: 'CSV reports exported successfully',
        outputDirectory: path.join(this.outputDir, 'csv')
      };

    } catch (error) {
      console.error('Error exporting CSV reports:', error);
      throw new Error(`CSV export failed: ${error.message}`);
    }
  }

  async exportCustomData(data, filename, headers) {
    try {
      const timestamp = DateUtils.formatDateForFilename();
      const customFilename = `${filename}_${timestamp}.csv`;
      const filePath = path.join(this.outputDir, 'csv', customFilename);

      const csvWriter = createCsvWriter({
        path: filePath,
        header: headers
      });

      await csvWriter.writeRecords(data);
      console.log(`✅ Custom CSV exported to: ${filePath}`);

      return {
        success: true,
        filePath: filePath,
        filename: customFilename
      };

    } catch (error) {
      console.error('Error exporting custom CSV:', error);
      throw new Error(`Custom CSV export failed: ${error.message}`);
    }
  }

  getOutputDirectory() {
    return this.outputDir;
  }
}

module.exports = CSVExporter;
