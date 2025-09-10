const puppeteer = require('puppeteer');
const handlebars = require('handlebars');
const fs = require('fs-extra');
const path = require('path');
const DateUtils = require('../utils/dateUtils');

class PDFExporter {
  constructor(outputDir = '../output', templatesDir = '../templates') {
    this.outputDir = path.resolve(__dirname, outputDir);
    this.templatesDir = path.resolve(__dirname, templatesDir);
    this.browser = null;
    this.ensureDirectories();
  }

  async ensureDirectories() {
    await fs.ensureDir(this.outputDir);
    await fs.ensureDir(path.join(this.outputDir, 'pdf'));
    await fs.ensureDir(this.templatesDir);
  }

  async initBrowser() {
    if (!this.browser) {
      this.browser = await puppeteer.launch({
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox']
      });
    }
    return this.browser;
  }

  async closeBrowser() {
    if (this.browser) {
      await this.browser.close();
      this.browser = null;
    }
  }

  async generateTemplate() {
    const templatePath = path.join(this.templatesDir, 'inventory-report-template.html');
    
    const templateContent = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Inventory Report</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 12px; line-height: 1.6; color: #333; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; margin-bottom: 30px; }
        .header h1 { font-size: 28px; margin-bottom: 10px; }
        .header .subtitle { font-size: 16px; opacity: 0.9; }
        .meta-info { display: flex; justify-content: space-between; margin-bottom: 30px; }
        .meta-card { background: #f8f9fa; padding: 20px; border-radius: 8px; flex: 1; margin: 0 10px; }
        .meta-card h3 { color: #495057; margin-bottom: 10px; font-size: 14px; }
        .section { margin-bottom: 40px; }
        .section-title { color: #495057; font-size: 18px; margin-bottom: 20px; border-bottom: 2px solid #e9ecef; padding-bottom: 5px; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #e9ecef; }
        th { background-color: #f8f9fa; font-weight: 600; color: #495057; }
        tr:hover { background-color: #f8f9fa; }
        .summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .summary-card { background: white; border: 1px solid #e9ecef; border-radius: 8px; padding: 20px; }
        .summary-card h4 { color: #6c757d; font-size: 14px; margin-bottom: 5px; }
        .summary-card .value { font-size: 24px; font-weight: bold; color: #495057; }
        .chart-container { margin: 20px 0; }
        .bar-chart { display: flex; align-items: end; height: 200px; gap: 2px; }
        .bar { background: linear-gradient(to top, #667eea, #764ba2); min-width: 20px; display: flex; align-items: end; justify-content: center; color: white; font-size: 10px; padding: 2px; }
        .status-badge { padding: 4px 8px; border-radius: 12px; font-size: 10px; font-weight: bold; }
        .status-available { background-color: #d4edda; color: #155724; }
        .status-full { background-color: #f8d7da; color: #721c24; }
        .footer { margin-top: 50px; padding-top: 20px; border-top: 1px solid #e9ecef; text-align: center; color: #6c757d; font-size: 10px; }
        @media print {
            .section { page-break-inside: avoid; }
            .header { page-break-after: avoid; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{reportTitle}}</h1>
        <div class="subtitle">{{reportSubtitle}}</div>
    </div>

    <div class="meta-info">
        <div class="meta-card">
            <h3>Report Period</h3>
            <div>{{metadata.date_range}}</div>
        </div>
        <div class="meta-card">
            <h3>Generated</h3>
            <div>{{metadata.generated_at}}</div>
        </div>
        <div class="meta-card">
            <h3>Report Type</h3>
            <div>{{metadata.report_type}} - {{metadata.period}}</div>
        </div>
    </div>

    {{#if summary}}
    <div class="section">
        <h2 class="section-title">Executive Summary</h2>
        <div class="summary-grid">
            <div class="summary-card">
                <h4>Total Items</h4>
                <div class="value">{{summary.totalItems}}</div>
            </div>
            <div class="summary-card">
                <h4>Total Boxes</h4>
                <div class="value">{{summary.totalBoxes}}</div>
            </div>
            <div class="summary-card">
                <h4>Overall Utilization</h4>
                <div class="value">{{summary.overallUtilization}}</div>
            </div>
            <div class="summary-card">
                <h4>Transactions (Period)</h4>
                <div class="value">{{summary.transactionsInPeriod}}</div>
            </div>
        </div>
    </div>
    {{/if}}

    {{#if inventoryStatus}}
    <div class="section">
        <h2 class="section-title">Inventory Status</h2>
        <table>
            <thead>
                <tr>
                    <th>Item ID</th>
                    <th>Item Name</th>
                    <th>Total Qty</th>
                    <th>Available</th>
                    <th>Occupied</th>
                    <th>Utilization</th>
                    <th>Last Updated</th>
                </tr>
            </thead>
            <tbody>
                {{#each inventoryStatus}}
                <tr>
                    <td>{{this.item_id}}</td>
                    <td>{{this.item_name}}</td>
                    <td>{{this.total_quantity}}</td>
                    <td>{{this.available_quantity}}</td>
                    <td>{{this.occupied_quantity}}</td>
                    <td>{{this.utilization_rate}}</td>
                    <td>{{this.last_updated}}</td>
                </tr>
                {{/each}}
            </tbody>
        </table>
    </div>
    {{/if}}

    {{#if boxUtilization}}
    <div class="section">
        <h2 class="section-title">Box Utilization</h2>
        <table>
            <thead>
                <tr>
                    <th>Box ID</th>
                    <th>Location</th>
                    <th>Total Compartments</th>
                    <th>Occupied</th>
                    <th>Available</th>
                    <th>Utilization</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {{#each boxUtilization}}
                <tr>
                    <td>{{this.box_id}}</td>
                    <td>{{this.location}}</td>
                    <td>{{this.total_compartments}}</td>
                    <td>{{this.occupied_compartments}}</td>
                    <td>{{this.available_compartments}}</td>
                    <td>{{this.utilization_rate}}</td>
                    <td><span class="status-badge {{#if (eq this.status 'Full')}}status-full{{else}}status-available{{/if}}">{{this.status}}</span></td>
                </tr>
                {{/each}}
            </tbody>
        </table>
    </div>
    {{/if}}

    {{#if topActiveItems}}
    <div class="section">
        <h2 class="section-title">Most Active Items</h2>
        <table>
            <thead>
                <tr>
                    <th>Item Name</th>
                    <th>Total Activities</th>
                    <th>Additions</th>
                    <th>Retrievals</th>
                </tr>
            </thead>
            <tbody>
                {{#each topActiveItems}}
                <tr>
                    <td>{{this.item_name}}</td>
                    <td>{{this.total_activities}}</td>
                    <td>{{this.additions}}</td>
                    <td>{{this.retrievals}}</td>
                </tr>
                {{/each}}
            </tbody>
        </table>
    </div>
    {{/if}}

    {{#if hourlyActivity}}
    <div class="section">
        <h2 class="section-title">Activity Distribution by Hour</h2>
        <div class="chart-container">
            <div class="bar-chart">
                {{#each hourlyActivity}}
                <div class="bar" style="height: {{this.percentage}}%;" title="Hour {{this.hour}}: {{this.total_transactions}} transactions">
                    {{this.hour}}h
                </div>
                {{/each}}
            </div>
        </div>
        <table>
            <thead>
                <tr>
                    <th>Hour</th>
                    <th>Total Transactions</th>
                    <th>Additions</th>
                    <th>Retrievals</th>
                </tr>
            </thead>
            <tbody>
                {{#each hourlyActivity}}
                <tr>
                    <td>{{this.hour}}:00</td>
                    <td>{{this.total_transactions}}</td>
                    <td>{{this.additions}}</td>
                    <td>{{this.retrievals}}</td>
                </tr>
                {{/each}}
            </tbody>
        </table>
    </div>
    {{/if}}

    <div class="footer">
        <p>Generated by Inventory Management System | {{metadata.generated_at}}</p>
    </div>
</body>
</html>
    `;

    await fs.writeFile(templatePath, templateContent);
    return templatePath;
  }

  async exportToPDF(reportData, reportType, period) {
    try {
      await this.initBrowser();
      await this.generateTemplate();

      const timestamp = DateUtils.formatDateForFilename();
      const filename = `inventory_${reportType}_${period}_${timestamp}.pdf`;
      const outputPath = path.join(this.outputDir, 'pdf', filename);

      // Prepare template data
      const templateData = {
        reportTitle: `Inventory ${reportType.charAt(0).toUpperCase() + reportType.slice(1)} Report`,
        reportSubtitle: `${period.charAt(0).toUpperCase() + period.slice(1)} Analysis - ${reportData.metadata.date_range}`,
        metadata: reportData.metadata,
        summary: reportData.summary,
        inventoryStatus: reportData.inventoryStatus,
        boxUtilization: reportData.boxUtilization,
        topActiveItems: reportData.topActiveItems,
        hourlyActivity: this.prepareHourlyActivityForChart(reportData.hourlyActivity)
      };

      // Register Handlebars helpers
      handlebars.registerHelper('eq', function(a, b) {
        return a === b;
      });

      // Load and compile template
      const templatePath = path.join(this.templatesDir, 'inventory-report-template.html');
      const templateSource = await fs.readFile(templatePath, 'utf8');
      const template = handlebars.compile(templateSource);
      const html = template(templateData);

      // Generate PDF
      const page = await this.browser.newPage();
      await page.setContent(html, { waitUntil: 'networkidle0' });
      
      await page.pdf({
        path: outputPath,
        format: 'A4',
        printBackground: true,
        margin: {
          top: '20mm',
          right: '20mm',
          bottom: '20mm',
          left: '20mm'
        }
      });

      await page.close();

      console.log(`✅ PDF report exported to: ${outputPath}`);

      return {
        success: true,
        filePath: outputPath,
        filename: filename
      };

    } catch (error) {
      console.error('Error exporting PDF report:', error);
      throw new Error(`PDF export failed: ${error.message}`);
    }
  }

  prepareHourlyActivityForChart(hourlyData) {
    if (!hourlyData || hourlyData.length === 0) return [];

    const maxTransactions = Math.max(...hourlyData.map(h => h.total_transactions));
    
    return hourlyData.map(hourData => ({
      ...hourData,
      percentage: maxTransactions > 0 ? (hourData.total_transactions / maxTransactions) * 100 : 0
    }));
  }

  async exportCustomPDF(data, templateName, outputFilename) {
    try {
      await this.initBrowser();

      const timestamp = DateUtils.formatDateForFilename();
      const filename = `${outputFilename}_${timestamp}.pdf`;
      const outputPath = path.join(this.outputDir, 'pdf', filename);

      const templatePath = path.join(this.templatesDir, `${templateName}.html`);
      
      if (!(await fs.pathExists(templatePath))) {
        throw new Error(`Template ${templateName}.html not found`);
      }

      const templateSource = await fs.readFile(templatePath, 'utf8');
      const template = handlebars.compile(templateSource);
      const html = template(data);

      const page = await this.browser.newPage();
      await page.setContent(html, { waitUntil: 'networkidle0' });
      
      await page.pdf({
        path: outputPath,
        format: 'A4',
        printBackground: true,
        margin: {
          top: '20mm',
          right: '20mm',
          bottom: '20mm',
          left: '20mm'
        }
      });

      await page.close();

      console.log(`✅ Custom PDF exported to: ${outputPath}`);

      return {
        success: true,
        filePath: outputPath,
        filename: filename
      };

    } catch (error) {
      console.error('Error exporting custom PDF:', error);
      throw new Error(`Custom PDF export failed: ${error.message}`);
    }
  }

  getOutputDirectory() {
    return this.outputDir;
  }
}

module.exports = PDFExporter;
