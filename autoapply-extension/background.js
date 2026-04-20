importScripts("config.js");

async function getToken() {
  const { [CONFIG.STORAGE_KEYS.TOKEN]: token } = await chrome.storage.local.get(CONFIG.STORAGE_KEYS.TOKEN);
  return token || null;
}

async function apiFetch(path, { method = "GET", body, auth = true } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (auth) {
    const token = await getToken();
    if (!token) throw new Error("not_authenticated");
    headers["Authorization"] = `Bearer ${token}`;
  }
  const res = await fetch(`${CONFIG.API_BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (res.status === 401) {
    await chrome.storage.local.remove([CONFIG.STORAGE_KEYS.TOKEN, CONFIG.STORAGE_KEYS.USER, CONFIG.STORAGE_KEYS.PROFILE]);
    throw new Error("unauthorized");
  }
  const text = await res.text();
  const data = text ? JSON.parse(text) : {};
  if (!res.ok) throw new Error(data.detail || `http_${res.status}`);
  return data;
}

async function login({ username, password }) {
  const data = await apiFetch("/api/auth/login", {
    method: "POST",
    body: { username, password },
    auth: false,
  });
  await chrome.storage.local.set({
    [CONFIG.STORAGE_KEYS.TOKEN]: data.access_token,
    [CONFIG.STORAGE_KEYS.USER]: data.user,
  });
  return data.user;
}

async function logout() {
  await chrome.storage.local.remove([
    CONFIG.STORAGE_KEYS.TOKEN,
    CONFIG.STORAGE_KEYS.USER,
    CONFIG.STORAGE_KEYS.PROFILE,
    CONFIG.STORAGE_KEYS.PROFILE_FETCHED_AT,
  ]);
}

async function getProfile({ force = false } = {}) {
  if (!force) {
    const cached = await chrome.storage.local.get([
      CONFIG.STORAGE_KEYS.PROFILE,
      CONFIG.STORAGE_KEYS.PROFILE_FETCHED_AT,
    ]);
    const fetchedAt = cached[CONFIG.STORAGE_KEYS.PROFILE_FETCHED_AT] || 0;
    if (cached[CONFIG.STORAGE_KEYS.PROFILE] && Date.now() - fetchedAt < CONFIG.PROFILE_TTL_MS) {
      return cached[CONFIG.STORAGE_KEYS.PROFILE];
    }
  }
  const profile = await apiFetch("/api/cv/profile");
  await chrome.storage.local.set({
    [CONFIG.STORAGE_KEYS.PROFILE]: profile,
    [CONFIG.STORAGE_KEYS.PROFILE_FETCHED_AT]: Date.now(),
  });
  return profile;
}

async function mapFields({ fields, jobContext }) {
  return apiFetch("/api/autoapply/map-fields", {
    method: "POST",
    body: { fields, job_context: jobContext || null },
  });
}

const handlers = { login, logout, getProfile, mapFields };

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  const fn = handlers[msg?.type];
  if (!fn) {
    sendResponse({ ok: false, error: "unknown_message" });
    return false;
  }
  Promise.resolve(fn(msg.payload || {}))
    .then(data => sendResponse({ ok: true, data }))
    .catch(err => sendResponse({ ok: false, error: err.message || String(err) }));
  return true;
});
