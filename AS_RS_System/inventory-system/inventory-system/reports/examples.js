#!/usr/bin/env node

/**
 * Example script demonstrating how to use the Inventory Reports Generator
 * This script shows various ways to generate and export reports
 */

const DailyReportGenerator = require('./generators/dailyReport');
const WeeklyReportGenerator = require('./generators/weeklyReport');
const MonthlyReportGenerator = require('./generators/monthlyReport');
const { testConnection } = require('./config/db');
const DateUtils = require('./utils/dateUtils');

async function runExamples() {
  console.log('🚀 Inventory Reports Generator - Usage Examples\n');

  try {
    // Test database connection
    console.log('1️⃣ Testing database connection...');
    await testConnection();
    console.log('   ✅ Database connected\n');

    // Initialize generators
    const dailyGenerator = new DailyReportGenerator();
    const weeklyGenerator = new WeeklyReportGenerator();
    const monthlyGenerator = new MonthlyReportGenerator();

    console.log('2️⃣ Example 1: Generate today\'s daily report (CSV only)');
    try {
      const dailyResult = await dailyGenerator.generateReport(null, ['csv']);
      console.log(`   ✅ Success: ${dailyResult.period}`);
      console.log(`   📊 Transactions: ${dailyResult.data?.summary?.transactionsInPeriod || 0}`);
      console.log(`   💡 Insights: ${dailyResult.data?.insights?.length || 0} generated\n`);
    } catch (error) {
      console.log(`   ❌ Failed: ${error.message}\n`);
    }

    console.log('3️⃣ Example 2: Generate this week\'s report (CSV + PDF)');
    try {
      const weeklyResult = await weeklyGenerator.generateReport(null, ['csv', 'pdf']);
      console.log(`   ✅ Success: ${weeklyResult.period}`);
      console.log(`   📊 Total Items: ${weeklyResult.data?.summary?.totalItems || 0}`);
      console.log(`   📦 Total Boxes: ${weeklyResult.data?.summary?.totalBoxes || 0}\n`);
    } catch (error) {
      console.log(`   ❌ Failed: ${error.message}\n`);
    }

    console.log('4️⃣ Example 3: Generate current month report (PDF only)');
    try {
      const monthlyResult = await monthlyGenerator.generateReport(null, ['pdf']);
      console.log(`   ✅ Success: ${monthlyResult.period}`);
      console.log(`   🔄 Utilization: ${monthlyResult.data?.summary?.overallUtilization || '0%'}\n`);
    } catch (error) {
      console.log(`   ❌ Failed: ${error.message}\n`);
    }

    console.log('5️⃣ Example 4: Generate specific date report');
    try {
      const specificDate = '2024-08-25'; // Example date
      const specificResult = await dailyGenerator.generateReport(specificDate, ['csv']);
      console.log(`   ✅ Success: Report for ${specificDate}`);
      console.log(`   📈 Data available: ${specificResult.data ? 'Yes' : 'No'}\n`);
    } catch (error) {
      console.log(`   ❌ Failed: ${error.message}\n`);
    }

    console.log('6️⃣ Example 5: Generate last 3 days reports');
    try {
      const multipleDailyResult = await dailyGenerator.generateMultipleDays(3, ['csv']);
      const successful = multipleDailyResult.filter(r => r.success).length;
      console.log(`   ✅ Generated ${successful}/3 daily reports\n`);
    } catch (error) {
      console.log(`   ❌ Failed: ${error.message}\n`);
    }

    console.log('📊 Summary of available features:');
    console.log('   • Daily Reports: Individual day analysis with hourly breakdown');
    console.log('   • Weekly Reports: 7-day analysis with daily trends');
    console.log('   • Monthly Reports: Full month with weekly breakdown');
    console.log('   • Batch Generation: Multiple periods at once');
    console.log('   • Export Formats: CSV for data analysis, PDF for presentations');
    console.log('   • API Endpoints: RESTful API for integration');
    console.log('   • CLI Commands: Command-line interface for automation\n');

    console.log('🎯 Next steps:');
    console.log('   • Start API server: npm start');
    console.log('   • Generate specific reports: node cli.js <command>');
    console.log('   • Check output folder for generated files');
    console.log('   • Set up automated generation with cron jobs\n');

    console.log('✅ Examples completed successfully!');

  } catch (error) {
    console.error('❌ Examples failed:', error.message);
    console.error('\n🔧 Troubleshooting tips:');
    console.error('   • Ensure the main inventory database is running');
    console.error('   • Check database connection settings');
    console.error('   • Verify there is some data in the database for meaningful reports');
    console.error('   • Make sure all dependencies are installed');
  }
}

// Handle graceful shutdown
process.on('SIGINT', () => {
  console.log('\n🔄 Examples interrupted by user');
  process.exit(0);
});

if (require.main === module) {
  runExamples();
}

module.exports = runExamples;
