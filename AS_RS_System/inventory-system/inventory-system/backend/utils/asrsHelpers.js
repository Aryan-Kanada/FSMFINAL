// backend/utils/asrsHelpers.js

/**
 * Extracts A1–E7 from a subcom_place code like 'A1a' or 'C3b'
 */
function parseLocation(code) {
  const m = code.match(/^([A-E][1-7])/);
  return m ? m[1] : null;
}

module.exports = { parseLocation };
