const moment = require('moment');

class DateUtils {
  static getCurrentDate() {
    return moment().format('YYYY-MM-DD');
  }

  static getCurrentDateTime() {
    return moment().format('YYYY-MM-DD HH:mm:ss');
  }

  static getDateRange(period, customDate = null) {
    const baseDate = customDate ? moment(customDate) : moment();
    
    switch (period) {
      case 'daily':
        return {
          start: baseDate.startOf('day').format('YYYY-MM-DD HH:mm:ss'),
          end: baseDate.endOf('day').format('YYYY-MM-DD HH:mm:ss'),
          label: baseDate.format('YYYY-MM-DD')
        };
      
      case 'weekly':
        return {
          start: baseDate.startOf('week').format('YYYY-MM-DD HH:mm:ss'),
          end: baseDate.endOf('week').format('YYYY-MM-DD HH:mm:ss'),
          label: `${baseDate.startOf('week').format('YYYY-MM-DD')} to ${baseDate.endOf('week').format('YYYY-MM-DD')}`
        };
      
      case 'monthly':
        return {
          start: baseDate.startOf('month').format('YYYY-MM-DD HH:mm:ss'),
          end: baseDate.endOf('month').format('YYYY-MM-DD HH:mm:ss'),
          label: baseDate.format('YYYY-MM')
        };
      
      default:
        throw new Error('Invalid period. Use daily, weekly, or monthly');
    }
  }

  static formatDateForFilename(date = null) {
    const targetDate = date ? moment(date) : moment();
    return targetDate.format('YYYYMMDD_HHmmss');
  }

  static formatDateForDisplay(date) {
    return moment(date).format('YYYY-MM-DD HH:mm:ss');
  }

  static getLastNDays(days) {
    const dates = [];
    for (let i = days - 1; i >= 0; i--) {
      dates.push(moment().subtract(i, 'days').format('YYYY-MM-DD'));
    }
    return dates;
  }

  static getLastNWeeks(weeks) {
    const ranges = [];
    for (let i = weeks - 1; i >= 0; i--) {
      const weekStart = moment().subtract(i, 'weeks').startOf('week');
      const weekEnd = moment().subtract(i, 'weeks').endOf('week');
      ranges.push({
        start: weekStart.format('YYYY-MM-DD'),
        end: weekEnd.format('YYYY-MM-DD'),
        label: `Week ${weekStart.format('YYYY-MM-DD')} to ${weekEnd.format('YYYY-MM-DD')}`
      });
    }
    return ranges;
  }

  static getLastNMonths(months) {
    const ranges = [];
    for (let i = months - 1; i >= 0; i--) {
      const monthStart = moment().subtract(i, 'months').startOf('month');
      const monthEnd = moment().subtract(i, 'months').endOf('month');
      ranges.push({
        start: monthStart.format('YYYY-MM-DD'),
        end: monthEnd.format('YYYY-MM-DD'),
        label: monthStart.format('YYYY-MM')
      });
    }
    return ranges;
  }
}

module.exports = DateUtils;
