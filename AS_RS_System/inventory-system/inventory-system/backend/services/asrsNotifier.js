/**
 * Service that forwards inventory events to the Aryan (Python) middle-layer.
 */
const axios = require("axios");
const ARYAN_URL =
  `http://localhost:${process.env.PORT_ARYAN || 5000}/backend-data`;

module.exports.sendEvent = async (payload) => {
  try {
    await axios.post(ARYAN_URL, payload, { timeout: 2000 });
  } catch (err) {
    console.error("Failed to notify Aryan service:", err.message);
  }
};
