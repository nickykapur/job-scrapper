const $ = (id) => document.getElementById(id);

function send(type, payload) {
  return new Promise((resolve, reject) => {
    chrome.runtime.sendMessage({ type, payload }, (res) => {
      if (chrome.runtime.lastError) return reject(new Error(chrome.runtime.lastError.message));
      if (!res) return reject(new Error("no_response"));
      if (!res.ok) return reject(new Error(res.error));
      resolve(res.data);
    });
  });
}

async function showLoggedIn(user) {
  $("logged-out").hidden = true;
  $("logged-in").hidden = false;
  $("user-name").textContent = user?.full_name || user?.username || "You";
  await renderProfile();
}

function showLoggedOut() {
  $("logged-in").hidden = true;
  $("logged-out").hidden = false;
}

async function renderProfile({ force = false } = {}) {
  const card = $("profile-card");
  card.innerHTML = '<p class="muted">Loading profile…</p>';
  try {
    const profile = await send("getProfile", { force });
    if (!profile?.exists) {
      card.innerHTML = '<p class="muted">No CV uploaded yet. Upload on the JobScraper site, then refresh.</p>';
      return;
    }
    const ins = profile.insights || {};
    const rows = [
      ["Name", profile.full_name],
      ["Email", profile.email],
      ["Location", profile.location],
      ["Experience", ins.years_of_experience != null ? `${ins.years_of_experience} yrs` : null],
      ["Seniority", ins.seniority],
      ["Skills", (profile.skills || []).length ? `${profile.skills.length} listed` : null],
    ].filter(([, v]) => v);
    card.innerHTML = rows
      .map(([k, v]) => `<div class="row"><span class="label">${k}</span><span>${escapeHtml(String(v))}</span></div>`)
      .join("");
  } catch (err) {
    if (err.message === "unauthorized" || err.message === "not_authenticated") {
      showLoggedOut();
      return;
    }
    card.innerHTML = `<p class="error">Could not load profile: ${escapeHtml(err.message)}</p>`;
  }
}

function escapeHtml(s) {
  return s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

async function init() {
  const { [CONFIG.STORAGE_KEYS.TOKEN]: token, [CONFIG.STORAGE_KEYS.USER]: user } = await chrome.storage.local.get([
    CONFIG.STORAGE_KEYS.TOKEN,
    CONFIG.STORAGE_KEYS.USER,
  ]);
  if (token && user) showLoggedIn(user);
  else showLoggedOut();
}

$("login-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const btn = $("login-btn");
  const err = $("login-error");
  err.hidden = true;
  btn.disabled = true;
  btn.textContent = "Signing in…";
  try {
    const user = await send("login", {
      username: $("login-username").value.trim(),
      password: $("login-password").value,
    });
    await showLoggedIn(user);
  } catch (e) {
    err.textContent = e.message || "Login failed";
    err.hidden = false;
  } finally {
    btn.disabled = false;
    btn.textContent = "Sign in";
  }
});

$("logout-btn").addEventListener("click", async () => {
  await send("logout", {});
  showLoggedOut();
});

$("refresh-btn").addEventListener("click", () => renderProfile({ force: true }));

init();
