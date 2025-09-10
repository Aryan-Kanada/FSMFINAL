# Inventory Report Generator

A comprehensive reporting system for the Inventory Management System that generates structured daily, weekly, and monthly reports exportable in CSV and PDF formats.

## Features

- **📊 Multiple Report Types**: Daily, Weekly, Monthly, and Yearly comparison reports
- **📄 Export Formats**: CSV and PDF export capabilities
- **🔄 Automated Generation**: API endpoints and CLI for automated report generation
- **📈 Analytics**: Transaction trends, box utilization, and performance metrics
- **🎯 Insights**: Automated insights and trend analysis
- **📅 Flexible Periods**: Generate reports for specific dates or periods
- **⚡ Batch Processing**: Generate multiple reports at once

## Project Structure

```
reports/
├── package.json              # Dependencies and scripts
├── index.js                  # Main API server
├── cli.js                    # Command-line interface
├── README.md                 # This file
├── config/
│   └── db.js                 # Database configuration
├── generators/
│   ├── dailyReport.js        # Daily report generator
│   ├── weeklyReport.js       # Weekly report generator
│   └── monthlyReport.js      # Monthly report generator
├── exporters/
│   ├── csvExporter.js        # CSV export functionality
│   └── pdfExporter.js        # PDF export functionality
├── utils/
│   ├── dateUtils.js          # Date handling utilities
│   ├── reportFormatter.js    # Data formatting utilities
│   └── reportQueries.js      # Database queries
├── templates/
│   └── (auto-generated)      # PDF templates
└── output/
    ├── csv/                  # Generated CSV files
    └── pdf/                  # Generated PDF files
```

## Installation

1. Navigate to the reports directory:
```bash
cd reports
```

2. Install dependencies:
```bash
npm install
```

3. Make sure your database configuration is properly set up in the main backend `.env` file.

## Usage

### API Server

Start the reports API server:
```bash
npm start
# or for development with auto-reload:
npm run dev
```

The server will start on port 3002 (or the port specified in `REPORTS_PORT` environment variable).

### API Endpoints

#### Generate Reports
- `POST /api/reports/daily` - Generate daily report
- `POST /api/reports/weekly` - Generate weekly report
- `POST /api/reports/monthly` - Generate monthly report
- `POST /api/reports/yearly` - Generate yearly comparison report
- `POST /api/reports/all` - Generate all current period reports

#### Batch Generation
- `POST /api/reports/daily/multiple` - Generate multiple daily reports
- `POST /api/reports/weekly/multiple` - Generate multiple weekly reports
- `POST /api/reports/monthly/multiple` - Generate multiple monthly reports

#### File Management
- `GET /api/reports/list` - List available report files
- `GET /api/reports/download/:type/:filename` - Download specific report
- `DELETE /api/reports/cleanup` - Clean up old report files

#### System
- `GET /health` - Health check

### Request Examples

Generate a daily report:
```bash
curl -X POST http://localhost:3002/api/reports/daily \
  -H "Content-Type: application/json" \
  -d '{"date": "2024-01-15", "formats": ["csv", "pdf"]}'
```

Generate weekly report:
```bash
curl -X POST http://localhost:3002/api/reports/weekly \
  -H "Content-Type: application/json" \
  -d '{"formats": ["pdf"]}'
```

Generate last 7 daily reports:
```bash
curl -X POST http://localhost:3002/api/reports/daily/multiple \
  -H "Content-Type: application/json" \
  -d '{"days": 7, "formats": ["csv"]}'
```

### Command Line Interface

The CLI provides a convenient way to generate reports from the command line:

```bash
# Generate daily report
node cli.js daily --date 2024-01-15 --format csv,pdf

# Generate weekly report
node cli.js weekly --format pdf

# Generate multiple daily reports
node cli.js daily-multiple --days 14 --format csv

# Generate all current period reports
node cli.js all --format pdf

# Show help
node cli.js help
```

#### CLI Commands

- `daily` - Generate daily report
- `daily-multiple` - Generate multiple daily reports
- `weekly` - Generate weekly report
- `weekly-multiple` - Generate multiple weekly reports
- `monthly` - Generate monthly report
- `monthly-multiple` - Generate multiple monthly reports
- `yearly` - Generate yearly comparison report
- `all` - Generate all current period reports

#### CLI Options

- `--date <YYYY-MM-DD>` - Specific date for report (default: today)
- `--format <csv,pdf>` - Export formats (default: csv,pdf)
- `--days <number>` - Number of days for multiple daily reports (default: 7)
- `--weeks <number>` - Number of weeks for multiple weekly reports (default: 4)
- `--months <number>` - Number of months for multiple monthly reports (default: 6)

## Report Contents

### Daily Reports
- **Inventory Status**: Current stock levels and utilization
- **Transaction Summary**: All transactions for the day
- **Box Utilization**: Storage capacity and usage
- **Peak Activity Hours**: Hourly transaction distribution
- **Top Active Items**: Most frequently accessed items
- **Daily Insights**: Automated analysis and alerts

### Weekly Reports
- **All Daily Report Content** plus:
- **Daily Breakdown**: Day-by-day activity analysis
- **Weekly Trends**: Growth patterns and comparisons
- **Weekday vs Weekend Activity**: Usage pattern analysis
- **Peak Performance Days**: Highest and lowest activity days

### Monthly Reports
- **All Weekly Report Content** plus:
- **Weekly Breakdown**: Week-by-week activity analysis
- **Monthly Trends**: Month-over-month comparisons
- **Performance Metrics**: KPIs and utilization statistics
- **Seasonal Patterns**: Quarterly activity analysis

### Yearly Comparison Reports
- **Monthly Breakdown**: Month-by-month activity for the year
- **Year-over-Year Comparison**: Trends compared to previous year
- **Seasonal Analysis**: Quarterly performance patterns
- **Annual Insights**: Long-term trends and patterns

## Export Formats

### CSV Exports
- Multiple CSV files per report (inventory, transactions, box utilization, etc.)
- Easy to import into spreadsheet applications
- Structured data for further analysis

### PDF Exports
- Professional formatted reports with charts and tables
- Executive summary with key metrics
- Visual representations of data trends
- Print-ready format

## Configuration

### Environment Variables
- `REPORTS_PORT` - Port for the API server (default: 3002)
- `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_DATABASE` - Database connection details

### Output Directory
Reports are saved to the `output/` directory:
- `output/csv/` - CSV export files
- `output/pdf/` - PDF export files

## Automation

### Scheduled Reports
You can set up cron jobs or scheduled tasks to automatically generate reports:

```bash
# Daily report at 6 AM
0 6 * * * cd /path/to/reports && node cli.js daily --format csv,pdf

# Weekly report every Monday at 8 AM
0 8 * * 1 cd /path/to/reports && node cli.js weekly --format pdf

# Monthly report on the 1st of each month at 9 AM
0 9 1 * * cd /path/to/reports && node cli.js monthly --format csv,pdf
```

### Cleanup
Regular cleanup of old reports:
```bash
# Clean up reports older than 30 days every week
0 2 * * 0 curl -X DELETE http://localhost:3002/api/reports/cleanup -H "Content-Type: application/json" -d '{"olderThan": 30}'
```

## Dependencies

- **express** - Web server framework
- **mysql2** - Database connectivity
- **puppeteer** - PDF generation
- **csv-writer** - CSV file generation
- **moment** - Date manipulation
- **handlebars** - Template engine for PDFs
- **fs-extra** - Enhanced file system operations

## Error Handling

The system includes comprehensive error handling:
- Database connection failures
- File system errors
- PDF generation issues
- Invalid date ranges
- Missing data scenarios

## Performance Considerations

- Reports are generated asynchronously
- Large datasets are processed in chunks
- PDF generation uses headless browser efficiently
- Multiple reports can be generated in parallel
- Old reports are automatically cleaned up

## Support

For issues or questions:
1. Check the server logs for error details
2. Verify database connectivity using the health check endpoint
3. Ensure all dependencies are properly installed
4. Check file permissions for the output directory

## License

This project is part of the Inventory Management System and follows the same license terms.
