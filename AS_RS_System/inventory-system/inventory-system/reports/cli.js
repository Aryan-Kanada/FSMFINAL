#!/usr/bin/env node

const DailyReportGenerator = require('./generators/dailyReport');
const WeeklyReportGenerator = require('./generators/weeklyReport');
const MonthlyReportGenerator = require('./generators/monthlyReport');
const { testConnection } = require('./config/db');

const args = process.argv.slice(2);
const command = args[0];
const options = parseOptions(args.slice(1));

function parseOptions(args) {
  const options = {
    date: null,
    format: ['csv', 'pdf'],
    days: 7,
    weeks: 4,
    months: 6
  };

  for (let i = 0; i < args.length; i += 2) {
    const key = args[i]?.replace('--', '');
    const value = args[i + 1];

    switch (key) {
      case 'date':
        options.date = value;
        break;
      case 'format':
        options.format = value.split(',');
        break;
      case 'days':
        options.days = parseInt(value);
        break;
      case 'weeks':
        options.weeks = parseInt(value);
        break;
      case 'months':
        options.months = parseInt(value);
        break;
    }
  }

  return options;
}

function showHelp() {
  console.log(`
🏗️  Inventory Reports Generator CLI

Usage: node cli.js <command> [options]

Commands:
  daily                Generate daily report
  daily-multiple       Generate multiple daily reports
  weekly               Generate weekly report
  weekly-multiple      Generate multiple weekly reports
  monthly              Generate monthly report
  monthly-multiple     Generate multiple monthly reports
  yearly               Generate yearly comparison report
  all                  Generate all current period reports

Options:
  --date <YYYY-MM-DD>   Specific date for report (default: today)
  --format <csv,pdf>    Export formats (default: csv,pdf)
  --days <number>       Number of days for multiple daily reports (default: 7)
  --weeks <number>      Number of weeks for multiple weekly reports (default: 4)
  --months <number>     Number of months for multiple monthly reports (default: 6)

Examples:
  node cli.js daily --date 2024-01-15 --format csv
  node cli.js weekly --format pdf
  node cli.js daily-multiple --days 14 --format csv,pdf
  node cli.js all --format pdf
  `);
}

async function main() {
  try {
    // Test database connection first
    await testConnection();

    const dailyGenerator = new DailyReportGenerator();
    const weeklyGenerator = new WeeklyReportGenerator();
    const monthlyGenerator = new MonthlyReportGenerator();

    switch (command) {
      case 'daily':
        console.log('📊 Generating daily report...');
        const dailyResult = await dailyGenerator.generateReport(options.date, options.format);
        console.log('✅ Daily report completed:', dailyResult.success ? 'Success' : 'Failed');
        break;

      case 'daily-multiple':
        console.log(`📊 Generating ${options.days} daily reports...`);
        const multipleDailyResult = await dailyGenerator.generateMultipleDays(options.days, options.format);
        const successfulDaily = multipleDailyResult.filter(r => r.success).length;
        console.log(`✅ Daily reports completed: ${successfulDaily}/${options.days} successful`);
        break;

      case 'weekly':
        console.log('📊 Generating weekly report...');
        const weeklyResult = await weeklyGenerator.generateReport(options.date, options.format);
        console.log('✅ Weekly report completed:', weeklyResult.success ? 'Success' : 'Failed');
        break;

      case 'weekly-multiple':
        console.log(`📊 Generating ${options.weeks} weekly reports...`);
        const multipleWeeklyResult = await weeklyGenerator.generateMultipleWeeks(options.weeks, options.format);
        const successfulWeekly = multipleWeeklyResult.filter(r => r.success).length;
        console.log(`✅ Weekly reports completed: ${successfulWeekly}/${options.weeks} successful`);
        break;

      case 'monthly':
        console.log('📊 Generating monthly report...');
        const monthlyResult = await monthlyGenerator.generateReport(options.date, options.format);
        console.log('✅ Monthly report completed:', monthlyResult.success ? 'Success' : 'Failed');
        break;

      case 'monthly-multiple':
        console.log(`📊 Generating ${options.months} monthly reports...`);
        const multipleMonthlyResult = await monthlyGenerator.generateMultipleMonths(options.months, options.format);
        const successfulMonthly = multipleMonthlyResult.filter(r => r.success).length;
        console.log(`✅ Monthly reports completed: ${successfulMonthly}/${options.months} successful`);
        break;

      case 'yearly':
        console.log('📊 Generating yearly comparison report...');
        const year = options.date ? new Date(options.date).getFullYear() : new Date().getFullYear();
        const yearlyResult = await monthlyGenerator.generateYearlyComparison(year);
        console.log('✅ Yearly comparison completed:', yearlyResult.success ? 'Success' : 'Failed');
        break;

      case 'all':
        console.log('📊 Generating all current period reports...');
        const [allDaily, allWeekly, allMonthly] = await Promise.allSettled([
          dailyGenerator.generateReport(options.date, options.format),
          weeklyGenerator.generateReport(options.date, options.format),
          monthlyGenerator.generateReport(options.date, options.format)
        ]);

        const allResults = [allDaily, allWeekly, allMonthly];
        const successfulAll = allResults.filter(r => r.status === 'fulfilled' && r.value.success).length;
        console.log(`✅ All reports completed: ${successfulAll}/3 successful`);
        break;

      case 'help':
      case '--help':
      case '-h':
        showHelp();
        break;

      default:
        console.log('❌ Unknown command. Use "help" for usage information.');
        showHelp();
        process.exit(1);
    }

    console.log('🎉 CLI operation completed successfully!');
    process.exit(0);

  } catch (error) {
    console.error('❌ CLI operation failed:', error.message);
    process.exit(1);
  }
}

// Handle interruption gracefully
process.on('SIGINT', () => {
  console.log('\n🔄 Operation cancelled by user');
  process.exit(0);
});

if (require.main === module) {
  main();
}

module.exports = { main, parseOptions };
