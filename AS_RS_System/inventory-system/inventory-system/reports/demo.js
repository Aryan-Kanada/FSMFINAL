#!/usr/bin/env node

const DailyReportGenerator = require('./generators/dailyReport');
const { testConnection } = require('./config/db');

async function demo() {
  console.log('🚀 Starting Inventory Reports Generator Demo\n');

  try {
    // Test database connection
    console.log('1️⃣ Testing database connection...');
    await testConnection();
    console.log('   ✅ Database connected successfully\n');

    // Initialize generators
    console.log('2️⃣ Initializing report generator...');
    const dailyGenerator = new DailyReportGenerator();
    console.log('   ✅ Daily report generator initialized\n');

    // Generate a sample daily report (CSV only for speed)
    console.log('3️⃣ Generating sample daily report...');
    console.log('   📊 Creating daily report for today (CSV format)...');
    
    const result = await dailyGenerator.generateReport(null, ['csv']);
    
    if (result.success) {
      console.log('   ✅ Daily report generated successfully!');
      console.log(`   📅 Report period: ${result.period}`);
      console.log(`   📁 Report data summary:`);
      
      if (result.data.summary) {
        console.log(`      • Total Items: ${result.data.summary.totalItems || 'N/A'}`);
        console.log(`      • Total Boxes: ${result.data.summary.totalBoxes || 'N/A'}`);
        console.log(`      • Transactions Today: ${result.data.summary.transactionsInPeriod || 'N/A'}`);
        console.log(`      • Overall Utilization: ${result.data.summary.overallUtilization || 'N/A'}`);
      }
      
      if (result.data.insights && result.data.insights.length > 0) {
        console.log(`   💡 Key insights:`);
        result.data.insights.forEach((insight, index) => {
          console.log(`      ${index + 1}. ${insight}`);
        });
      }
      
      if (result.exports && result.exports.csv) {
        console.log(`   📂 CSV files exported to: ${result.exports.csv.outputDirectory}`);
      }
      
    } else {
      console.log('   ❌ Failed to generate daily report');
    }

    console.log('\n4️⃣ Demo completed successfully! 🎉');
    console.log('\n📋 Next steps:');
    console.log('   • Run "npm start" to start the API server');
    console.log('   • Use "node cli.js help" for command-line options');
    console.log('   • Check the output/ directory for generated reports');
    console.log('   • Visit http://localhost:3002/health when server is running');

  } catch (error) {
    console.error('\n❌ Demo failed:', error.message);
    console.error('\n🔧 Troubleshooting:');
    console.error('   • Make sure the main backend database is running');
    console.error('   • Check database connection settings');
    console.error('   • Ensure all dependencies are installed (npm install)');
    console.error('   • Verify there is some data in the database');
  }
}

if (require.main === module) {
  demo();
}

module.exports = demo;
