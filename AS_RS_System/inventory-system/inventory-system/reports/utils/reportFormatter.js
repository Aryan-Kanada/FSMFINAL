class ReportFormatter {
  static formatInventoryStatus(items) {
    return items.map(item => ({
      item_id: item.item_id || 'N/A',
      item_name: item.name || 'Unknown Item',
      total_quantity: item.total_quantity || 0,
      available_quantity: item.available_quantity || 0,
      occupied_quantity: item.occupied_quantity || 0,
      utilization_rate: item.total_quantity > 0 
        ? ((item.occupied_quantity / item.total_quantity) * 100).toFixed(2) + '%'
        : '0%',
      last_updated: item.last_updated || 'N/A'
    }));
  }

  static formatTransactionSummary(transactions) {
    const summary = {
      total_transactions: transactions.length,
      additions: transactions.filter(t => t.action === 'added').length,
      retrievals: transactions.filter(t => t.action === 'retrieved').length,
      transactions_by_hour: this.groupTransactionsByHour(transactions),
      top_items: this.getTopItemsByActivity(transactions)
    };

    return summary;
  }

  static groupTransactionsByHour(transactions) {
    const hourlyData = {};
    
    for (let hour = 0; hour < 24; hour++) {
      hourlyData[hour] = { added: 0, retrieved: 0 };
    }

    transactions.forEach(transaction => {
      if (transaction.time) {
        const hour = new Date(transaction.time).getHours();
        if (transaction.action === 'added') {
          hourlyData[hour].added++;
        } else if (transaction.action === 'retrieved') {
          hourlyData[hour].retrieved++;
        }
      }
    });

    return hourlyData;
  }

  static getTopItemsByActivity(transactions, limit = 10) {
    const itemActivity = {};

    transactions.forEach(transaction => {
      const itemName = transaction.item_name || 'Unknown Item';
      if (!itemActivity[itemName]) {
        itemActivity[itemName] = { added: 0, retrieved: 0, total: 0 };
      }
      
      if (transaction.action === 'added') {
        itemActivity[itemName].added++;
      } else if (transaction.action === 'retrieved') {
        itemActivity[itemName].retrieved++;
      }
      itemActivity[itemName].total++;
    });

    return Object.entries(itemActivity)
      .sort(([,a], [,b]) => b.total - a.total)
      .slice(0, limit)
      .map(([itemName, activity]) => ({
        item_name: itemName,
        ...activity
      }));
  }

  static formatBoxUtilization(boxes) {
    return boxes.map(box => ({
      box_id: box.box_id || 'N/A',
      location: box.location || 'Unknown Location',
      total_compartments: box.total_compartments || 0,
      occupied_compartments: box.occupied_compartments || 0,
      available_compartments: (box.total_compartments || 0) - (box.occupied_compartments || 0),
      utilization_rate: box.total_compartments > 0
        ? ((box.occupied_compartments / box.total_compartments) * 100).toFixed(2) + '%'
        : '0%',
      status: box.total_compartments === box.occupied_compartments ? 'Full' : 'Available'
    }));
  }

  static formatReportMetadata(reportType, period, dateRange) {
    return {
      report_type: reportType,
      period: period,
      date_range: dateRange.label,
      generated_at: new Date().toISOString(),
      generated_by: 'Inventory Management System'
    };
  }

  static calculateTrends(currentData, previousData, metric) {
    if (!previousData || previousData[metric] === 0) {
      return {
        trend: 'N/A',
        change: 0,
        percentage_change: 'N/A'
      };
    }

    const current = currentData[metric] || 0;
    const previous = previousData[metric] || 0;
    const change = current - previous;
    const percentageChange = ((change / previous) * 100).toFixed(2);

    return {
      trend: change > 0 ? 'up' : change < 0 ? 'down' : 'stable',
      change: change,
      percentage_change: percentageChange + '%'
    };
  }
}

module.exports = ReportFormatter;
