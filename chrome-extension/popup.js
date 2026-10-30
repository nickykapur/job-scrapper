// popup.js

const $ = id => document.getElementById(id);

async function init() {
  const data = await chrome.storage.local.get(['authToken', 'apiBase']);

  if (!data.authToken) {
    $('loginView').style.display = 'block';
    $('mainView').style.display  = 'none';
    setupLogin();
  } else {
    $('loginView').style.display = 'none';
    $('mainView').style.display  = 'block';
    await loadMainView(data.apiBase, data.authToken);
    setupMainActions(data.apiBase, data.authToken);
  }
}

function setupLogin() {
  $('loginBtn').addEventListener('click', async () => {
    const apiBase = $('apiBaseInput').value.trim().replace(/\/$/, '');
    const token   = $('tokenInput').value.trim();
    if (!apiBase || !token) return;

    // Verify token works
    try {
      const res = await fetch(`${apiBase}/api/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error('Invalid token');
      await chrome.runtime.sendMessage({ type: 'SAVE_TOKEN', token, apiBase });
      location.reload();
    } catch {
      alert('Could not connect. Check your URL and token.');
    }
  });
}

async function loadMainView(apiBase, token) {
  // Get background status
  const status = await chrome.runtime.sendMessage({ type: 'GET_STATUS' });

  // Update status dot + text
  const dot  = $('statusDot');
  const text = $('statusText');
  if (status.isRunning) {
    dot.className = 'status-dot running';
    text.textContent = 'Applying...';
  } else {
    dot.className = 'status-dot idle';
    text.textContent = 'Idle';
  }

  // Daily progress
  const pct = Math.round((status.dailyCount / status.dailyLimit) * 100);
  $('progressFill').style.width = pct + '%';
  $('progressLabel').textContent = `${status.dailyCount} / ${status.dailyLimit} today`;

  // Queue data from API
  try {
    const res = await fetch(`${apiBase}/api/auto-apply/queue`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (!res.ok) return;
    const data = await res.json();

    const counts = data.counts || {};
    $('pendingCount').textContent = counts.pending || 0;
    $('appliedCount').textContent = counts.applied || 0;
    $('failedCount').textContent  = (counts.failed || 0) + (counts.skipped_external || 0);

    // Queue list (recent 8)
    const recent = (data.items || []).slice(0, 8);
    if (recent.length) {
      $('queueList').innerHTML = recent.map(item => `
        <div class="queue-item">
          <span class="badge badge-${getBadgeClass(item.status)}">${getStatusLabel(item.status)}</span>
          <span style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">
            ${item.job_title || 'Job'} · ${item.company || ''}
          </span>
        </div>
      `).join('');
    }
  } catch {}
}

function setupMainActions(apiBase, token) {
  $('startBtn').addEventListener('click', async () => {
    $('startBtn').disabled = true;
    $('startBtn').textContent = 'Starting...';
    await chrome.runtime.sendMessage({ type: 'START_APPLYING' });
    setTimeout(() => location.reload(), 1500);
  });

  $('openSettingsBtn').addEventListener('click', () => {
    chrome.tabs.create({ url: `${apiBase}/settings?tab=auto-apply` });
    window.close();
  });

  $('logoutLink').addEventListener('click', async () => {
    await chrome.storage.local.remove(['authToken', 'apiBase']);
    location.reload();
  });
}

function getBadgeClass(status) {
  if (status === 'applied') return 'applied';
  if (status === 'failed')  return 'failed';
  if (status === 'skipped_external') return 'skipped';
  return 'pending';
}

function getStatusLabel(status) {
  const map = {
    pending: 'Queued', applied: 'Applied', failed: 'Failed',
    skipped_external: 'External', running: 'Running', session_expired: 'Expired'
  };
  return map[status] || status;
}

init();
