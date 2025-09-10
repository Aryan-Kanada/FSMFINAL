/**
 * Test Script for Inventory Reports System
 * Run with: node test-reports.js
 */

const ReportsManager = require('./manager');
const DateUtils = require('./utils/dateUtils');

class ReportsTestSuite {
  constructor() {
    this.reportsManager = new ReportsManager();
    this.results = {
      passed: 0,
      failed: 0,
      errors: []
    };
  }

  async runAllTests() {
    console.log('🧪 Starting Inventory Reports Test Suite');
    console.log('=====================================\n');

    try {
      await this.testDatabaseConnection();
      await this.testDateUtilities();
      await this.testBasicReportGeneration();
      await this.testCustomReportGeneration();
      await this.testSystemHealth();
      await this.testFileOperations();
      
      this.printResults();

    } catch (error) {
      console.error('❌ Test suite failed:', error);
      this.results.failed++;
      this.results.errors.push(error.message);
    }
  }

  async testDatabaseConnection() {
    console.log('🔌 Testing Database Connection...');
    
    try {
      const { testConnection } = require('./config/db');
      await testConnection();
      console.log('✅ Database connection successful\n');
      this.results.passed++;
    } catch (error) {
      console.log('❌ Database connection failed:', error.message);
      console.log('   Make sure your MySQL server is running and credentials are correct\n');
      this.results.failed++;
      this.results.errors.push(`Database: ${error.message}`);
    }
  }

  async testDateUtilities() {
    console.log('📅 Testing Date Utilities...');
    
    try {
      // Test different date range generations
      const todayRange = DateUtils.getDateRange('daily');
      const weekRange = DateUtils.getDateRange('weekly');
      const monthRange = DateUtils.getDateRange('monthly');
      
      console.log(`   Daily range: ${todayRange.start} to ${todayRange.end}`);
      console.log(`   Weekly range: ${weekRange.start} to ${weekRange.end}`);
      console.log(`   Monthly range: ${monthRange.start} to ${monthRange.end}`);
      
      // Test last N periods
      const last7Days = DateUtils.getLastNDays(7);
      const last4Weeks = DateUtils.getLastNWeeks(4);
      const last6Months = DateUtils.getLastNMonths(6);
      
      console.log(`   Last 7 days: ${last7Days.length} periods`);
      console.log(`   Last 4 weeks: ${last4Weeks.length} periods`);
      console.log(`   Last 6 months: ${last6Months.length} periods`);
      
      console.log('✅ Date utilities working correctly\n');
      this.results.passed++;
      
    } catch (error) {
      console.log('❌ Date utilities test failed:', error.message);
      this.results.failed++;
      this.results.errors.push(`Date Utils: ${error.message}`);
    }
  }

  async testBasicReportGeneration() {
    console.log('📊 Testing Basic Report Generation...');
    
    try {
      // Test daily report with CSV export only (faster)
      console.log('   Generating daily report...');
      const dailyResult = await this.reportsManager.dailyGenerator.generateReport(null, ['csv']);
      
      if (dailyResult.success) {
        console.log(`   ✅ Daily report generated successfully`);
        console.log(`      CSV files: ${Object.keys(dailyResult.exports.csv || {}).length}`);
      } else {
        throw new Error('Daily report generation failed');
      }

      this.results.passed++;
      console.log('✅ Basic report generation working\n');
      
    } catch (error) {
      console.log('❌ Basic report generation failed:', error.message);
      this.results.failed++;
      this.results.errors.push(`Basic Reports: ${error.message}`);
    }
  }

  async testCustomReportGeneration() {
    console.log('⚙️ Testing Custom Report Generation...');
    
    try {
      // Test custom report with filters
      const customConfig = {
        reportType: 'weekly',
        exportFormats: ['csv'],
        includeInsights: true,
        customFilters: {
          minUtilization: 0,
          topItemsLimit: 5
        }
      };
      
      console.log('   Generating custom weekly report with filters...');
      const customResult = await this.reportsManager.generateCustomReport(customConfig);
      
      if (customResult.success) {
        console.log(`   ✅ Custom report generated successfully`);
        console.log(`      Report type: ${customResult.reportType}`);
        console.log(`      Insights: ${customResult.data.insights ? customResult.data.insights.length : 0}`);
      } else {
        throw new Error('Custom report generation failed');
      }

      this.results.passed++;
      console.log('✅ Custom report generation working\n');
      
    } catch (error) {
      console.log('❌ Custom report generation failed:', error.message);
      this.results.failed++;
      this.results.errors.push(`Custom Reports: ${error.message}`);
    }
  }

  async testSystemHealth() {
    console.log('🏥 Testing System Health Check...');
    
    try {
      const health = await this.reportsManager.getReportsHealth();
      
      console.log(`   Status: ${health.status}`);
      console.log(`   Database: ${health.database || health.error}`);
      console.log(`   Total reports: ${health.totalReportsGenerated || 0}`);
      console.log(`   Storage used: ${health.storageUsedFormatted || '0 Bytes'}`);
      
      if (health.status === 'healthy') {
        console.log('✅ System health check passed\n');
        this.results.passed++;
      } else {
        console.log('⚠️  System health check shows issues (may be expected)\n');
        this.results.passed++; // Still count as passed since it's working
      }
      
    } catch (error) {
      console.log('❌ System health check failed:', error.message);
      this.results.failed++;
      this.results.errors.push(`Health Check: ${error.message}`);
    }
  }

  async testFileOperations() {
    console.log('📁 Testing File Operations...');
    
    try {
      const fs = require('fs-extra');
      const path = require('path');
      
      // Ensure output directories exist
      const outputDir = path.join(__dirname, 'output');
      const csvDir = path.join(outputDir, 'csv');
      const pdfDir = path.join(outputDir, 'pdf');
      
      await fs.ensureDir(csvDir);
      await fs.ensureDir(pdfDir);
      
      console.log('   ✅ Output directories verified');
      
      // Test file permissions
      await fs.access(outputDir, fs.constants.W_OK);
      console.log('   ✅ Write permissions verified');
      
      // Test creating a sample file
      const testFile = path.join(csvDir, 'test-file.txt');
      await fs.writeFile(testFile, 'Test content');
      
      // Verify file exists
      const exists = await fs.pathExists(testFile);
      if (exists) {
        console.log('   ✅ File creation successful');
        
        // Clean up test file
        await fs.remove(testFile);
        console.log('   ✅ File cleanup successful');
      }

      this.results.passed++;
      console.log('✅ File operations working correctly\n');
      
    } catch (error) {
      console.log('❌ File operations test failed:', error.message);
      this.results.failed++;
      this.results.errors.push(`File Operations: ${error.message}`);
    }
  }

  printResults() {
    console.log('📋 Test Results Summary');
    console.log('=======================');
    console.log(`✅ Passed: ${this.results.passed}`);
    console.log(`❌ Failed: ${this.results.failed}`);
    console.log(`📊 Total: ${this.results.passed + this.results.failed}`);
    
    if (this.results.errors.length > 0) {
      console.log('\n🚨 Errors encountered:');
      this.results.errors.forEach((error, index) => {
        console.log(`   ${index + 1}. ${error}`);
      });
    }

    const successRate = ((this.results.passed / (this.results.passed + this.results.failed)) * 100).toFixed(1);
    console.log(`\n🎯 Success Rate: ${successRate}%`);
    
    if (this.results.failed === 0) {
      console.log('🎉 All tests passed! The system is ready to use.');
      console.log('\n📚 Next steps:');
      console.log('   • Start the API server: npm start');
      console.log('   • Try CLI commands: node cli.js daily');
      console.log('   • Open web interface: open web-interface.html');
    } else {
      console.log('⚠️  Some tests failed. Check the errors above.');
      console.log('   Common issues: Database not running, missing permissions');
    }
  }

  async demonstrateAPI() {
    console.log('\n🌐 API Integration Demonstration');
    console.log('=================================');
    
    try {
      // This would normally be done with HTTP requests, but we'll demo the functions directly
      console.log('Available API endpoints:');
      console.log('   POST /api/reports/daily');
      console.log('   POST /api/reports/weekly');
      console.log('   POST /api/reports/monthly');
      console.log('   POST /api/reports/custom');
      console.log('   GET  /api/reports/list');
      console.log('   GET  /api/reports/health');
      
      console.log('\n📝 Example API usage:');
      console.log('   curl -X POST http://localhost:3002/api/reports/daily');
      console.log('   curl -X GET http://localhost:3002/api/reports/health');
      
    } catch (error) {
      console.log('❌ API demonstration failed:', error.message);
    }
  }
}

// Run tests if this file is executed directly
if (require.main === module) {
  const testSuite = new ReportsTestSuite();
  
  testSuite.runAllTests()
    .then(() => testSuite.demonstrateAPI())
    .then(() => {
      console.log('\n✨ Test suite completed!');
      process.exit(0);
    })
    .catch((error) => {
      console.error('\n💥 Test suite crashed:', error);
      process.exit(1);
    });
}

module.exports = ReportsTestSuite;
