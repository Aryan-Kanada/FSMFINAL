// src/utils/api.js

export async function apiFetch(url, options = {}, retries = 3) {
  try {
    const res = await fetch(url, options);
    if (!res.ok && retries > 0) {
      return apiFetch(url, options, retries - 1);
    }
    return res.json();
  } catch (e) {
    if (retries > 0) {
      return apiFetch(url, options, retries - 1);
    }
    throw e;
  }
}
