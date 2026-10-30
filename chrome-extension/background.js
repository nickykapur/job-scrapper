// background.js — Service worker for Job Tracker Auto Apply extension
// Manages the queue polling, session, and coordinates with content scripts.

const API_BASE_KEY = 'apiBase';
const TOKEN_KEY = 'authToken';
const SESSION_KEY = 'isRunning';
const DAILY_LIMIT = 50;
const DAILY_COUNT_KEY = 'dailyApplyCount';
const DAILY_DATE_KEY = 'dailyApplyDate';

// ── Alarm: poll queue every 8 minutes while not running ──────────────────────
chrome.alarms.create('pollQueue', { periodInMinutes: 8 });

chrome.alarms.onAlarm.addListener(async (alarm) => {
  if (alarm.name === 'pollQueue') {
    await maybeStartApplySession();
  }
});

// ── On install: open popup so user can log in ─────────────────────────────────
chrome.runtime.onInstalled.addListener(() => {
  chrome.action.openPopup().catch(() => {});
});

// ── Message handler (from popup and content script) ───────────────────────────
chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg.type === 'START_APPLYING') {
    maybeStartApplySession().then(() => sendResponse({ ok: true }));
    return true;
  }
  if (msg.type === 'GET_STATUS') {
    getStatus().then(sendResponse);
    return true;
  }
  if (msg.type === 'JOB_RESULT') {
    handleJobResult(msg).then(() => sendResponse({ ok: true }));
    return true;
  }
  if (msg.type === 'SAVE_TOKEN') {
    chrome.storage.local.set({ [TOKEN_KEY]: msg.token, [API_BASE_KEY]: msg.apiBase })
      .then(() => sendResponse({ ok: true }));
    return true;
  }
});

async function getStatus() {
  const data = await chrome.storage.local.get([
    SESSION_KEY, DAILY_COUNT_KEY, DAILY_DATE_KEY, TOKEN_KEY, API_BASE_KEY
  ]);
  const today = new Date().toDateString();
  const count = data[DAILY_DATE_KEY] === today ? (data[DAILY_COUNT_KEY] || 0) : 0;
  return {
    isRunning: data[SESSION_KEY] || false,
    dailyCount: count,
    dailyLimit: DAILY_LIMIT,
    hasToken: !!data[TOKEN_KEY],
    apiBase: data[API_BASE_KEY] || '',
  };
}

async function maybeStartApplySession() {
  const data = await chrome.storage.local.get([
    SESSION_KEY, TOKEN_KEY, API_BASE_KEY, DAILY_COUNT_KEY, DAILY_DATE_KEY
  ]);

  if (data[SESSION_KEY]) return; // already running
  if (!data[TOKEN_KEY]) return;  // not logged in

  // Check daily limit
  const today = new Date().toDateString();
  const count = data[DAILY_DATE_KEY] === today ? (data[DAILY_COUNT_KEY] || 0) : 0;
  if (count >= DAILY_LIMIT) return;

  const apiBase = data[API_BASE_KEY];
  const token = data[TOKEN_KEY];

  // Fetch pending queue
  let queue;
  try {
    const res = await fetch(`${apiBase}/api/auto-apply/queue`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (!res.ok) return;
    const body = await res.json();
    queue = (body.items || []).filter(j => j.status === 'pending');
  } catch {
    return;
  }

  if (!queue.length) return;

  // Take up to 10 jobs per session
  const remaining = DAILY_LIMIT - count;
  const batch = queue.slice(0, Math.min(10, remaining));

  await chrome.storage.local.set({ [SESSION_KEY]: true });

  // Process sequentially
  for (const job of batch) {
    await processJob(job, apiBase, token);
    // Random 3–7 min wait between jobs (human-like)
    const waitMs = (3 + Math.random() * 4) * 60 * 1000;
    await sleep(waitMs);
  }

  await chrome.storage.local.set({ [SESSION_KEY]: false });
}

async function processJob(job, apiBase, token) {
  // Fetch user profile + cached answers in parallel
  const [profileRes, answersRes, resumeRes] = await Promise.all([
    fetch(`${apiBase}/api/auto-apply/profile`, { headers: { Authorization: `Bearer ${token}` } }),
    fetch(`${apiBase}/api/auto-apply/answers`, { headers: { Authorization: `Bearer ${token}` } }),
    fetch(`${apiBase}/api/auto-apply/profile/resume`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.ok ? r.json() : null).catch(() => null),
  ]);

  const profile = profileRes.ok ? await profileRes.json() : {};
  const answersBody = answersRes.ok ? await answersRes.json() : { answers: [] };

  // Build local cache map: question_key → answer
  const answerMap = {};
  for (const a of (answersBody.answers || [])) {
    answerMap[a.question_key] = a.answer;
  }

  // Open the job in a new tab
  const tab = await chrome.tabs.create({ url: job.job_url, active: false });

  // Wait for tab to load
  await waitForTabLoad(tab.id);

  // Inject content script with context
  try {
    const result = await chrome.tabs.sendMessage(tab.id, {
      type: 'APPLY_TO_JOB',
      job,
      profile,
      answerMap,
      resume: resumeRes,
      apiBase,
      token,
    });

    await updateDailyCount();
    await updateQueueStatus(job.job_id, result?.status || 'failed', result?.error, apiBase, token);

    if (result?.status === 'applied') {
      chrome.notifications.create({
        type: 'basic',
        iconUrl: 'icons/icon48.png',
        title: 'Applied!',
        message: `Auto-applied to ${job.job_title || 'job'} at ${job.company || 'company'}`,
      });
    }
  } catch (err) {
    await updateQueueStatus(job.job_id, 'failed', err.message, apiBase, token);
  } finally {
    // Close the tab
    chrome.tabs.remove(tab.id).catch(() => {});
  }
}

async function handleJobResult(msg) {
  const data = await chrome.storage.local.get([TOKEN_KEY, API_BASE_KEY]);
  await updateQueueStatus(msg.jobId, msg.status, msg.error, data[API_BASE_KEY], data[TOKEN_KEY]);
  if (msg.status === 'applied') await updateDailyCount();
}

async function updateQueueStatus(jobId, status, error, apiBase, token) {
  try {
    await fetch(`${apiBase}/api/auto-apply/queue/${jobId}/status`, {
      method: 'PATCH',
      headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ status, error_reason: error || null }),
    });
  } catch {}
}

async function updateDailyCount() {
  const data = await chrome.storage.local.get([DAILY_COUNT_KEY, DAILY_DATE_KEY]);
  const today = new Date().toDateString();
  const count = data[DAILY_DATE_KEY] === today ? (data[DAILY_COUNT_KEY] || 0) : 0;
  await chrome.storage.local.set({
    [DAILY_COUNT_KEY]: count + 1,
    [DAILY_DATE_KEY]: today,
  });
}

function waitForTabLoad(tabId) {
  return new Promise((resolve) => {
    const listener = (id, info) => {
      if (id === tabId && info.status === 'complete') {
        chrome.tabs.onUpdated.removeListener(listener);
        // Extra buffer for LinkedIn's JS to hydrate
        setTimeout(resolve, 3000);
      }
    };
    chrome.tabs.onUpdated.addListener(listener);
    // Timeout safety
    setTimeout(resolve, 20000);
  });
}

function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}
