// content.js — Runs on LinkedIn job pages. Handles the actual Easy Apply flow.

let _apiBase = '';
let _token = '';

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg.type === 'APPLY_TO_JOB') {
    _apiBase = msg.apiBase;
    _token = msg.token;
    applyToJob(msg.job, msg.profile, msg.answerMap, msg.resume)
      .then(result => sendResponse(result))
      .catch(err => sendResponse({ status: 'failed', error: err.message }));
    return true; // async
  }
});

// ─────────────────────────────────────────────────────────────────────────────

async function applyToJob(job, profile, answerMap, resume) {
  await sleep(2000 + rand(1500));

  // Find the Easy Apply button
  const easyApplyBtn = await waitForElement(
    'button[aria-label*="Easy Apply"], .jobs-apply-button--top-card button',
    8000
  );

  if (!easyApplyBtn) {
    return { status: 'skipped_external', error: 'No Easy Apply button found' };
  }

  // Check it actually says Easy Apply (not just Apply)
  if (!easyApplyBtn.innerText.toLowerCase().includes('easy apply')) {
    return { status: 'skipped_external', error: 'Button is not Easy Apply' };
  }

  easyApplyBtn.click();
  await sleep(2000 + rand(1000));

  // Walk through form pages
  let pageCount = 0;
  const MAX_PAGES = 10;

  while (pageCount < MAX_PAGES) {
    pageCount++;

    // Check if modal is open
    const modal = document.querySelector('.jobs-easy-apply-modal, [data-test-modal]');
    if (!modal) break;

    // Check for "Review" / final page
    const submitBtn = modal.querySelector('button[aria-label*="Submit application"]');
    if (submitBtn) {
      await sleep(500 + rand(500));
      submitBtn.click();
      await sleep(2000 + rand(1000));
      // Look for confirmation
      const confirmed = await waitForElement(
        '.artdeco-inline-feedback--success, .jobs-easy-apply-modal__confirmation',
        5000
      );
      return { status: confirmed ? 'applied' : 'failed', error: confirmed ? null : 'No confirmation found' };
    }

    // Fill all fields on current page
    await fillPage(modal, profile, answerMap, resume);
    await sleep(800 + rand(600));

    // Click Next
    const nextBtn = modal.querySelector(
      'button[aria-label*="Continue to next step"], button[aria-label*="Review your application"], button[aria-label*="Next"]'
    );
    if (!nextBtn) {
      // No next button and no submit — stuck
      return { status: 'failed', error: 'Could not find Next or Submit button' };
    }
    nextBtn.click();
    await sleep(1500 + rand(1000));
  }

  return { status: 'failed', error: 'Exceeded max page count' };
}

async function fillPage(modal, profile, answerMap, resume) {
  // ── Text inputs and textareas ─────────────────────────────────────────────
  const textInputs = modal.querySelectorAll('input[type="text"], input[type="tel"], input[type="email"], input[type="number"], textarea');
  for (const input of textInputs) {
    if (input.value && input.value.trim()) continue; // already filled

    const label = getLabelFor(input, modal);
    if (!label) continue;

    const answer = await resolveAnswer(label, profile, answerMap);
    if (answer) {
      await typeIntoField(input, answer);
    }
  }

  // ── Radio buttons ─────────────────────────────────────────────────────────
  const radioGroups = modal.querySelectorAll('fieldset');
  for (const group of radioGroups) {
    const legend = group.querySelector('legend')?.innerText?.trim();
    if (!legend) continue;

    // Check if already answered
    const checked = group.querySelector('input[type="radio"]:checked');
    if (checked) continue;

    const answer = await resolveAnswer(legend, profile, answerMap);
    if (!answer) continue;

    // Find the radio option matching the answer
    const radios = group.querySelectorAll('input[type="radio"]');
    let matched = false;
    for (const radio of radios) {
      const radioLabel = getLabelFor(radio, group);
      if (radioLabel && radioLabel.toLowerCase().includes(answer.toLowerCase().substring(0, 10))) {
        radio.click();
        matched = true;
        break;
      }
    }
    // Default to first option if no match
    if (!matched && radios.length > 0) {
      radios[0].click();
    }
    await sleep(300 + rand(200));
  }

  // ── Select dropdowns ──────────────────────────────────────────────────────
  const selects = modal.querySelectorAll('select');
  for (const select of selects) {
    if (select.value && select.value !== '') continue;

    const label = getLabelFor(select, modal);
    if (!label) continue;

    const answer = await resolveAnswer(label, profile, answerMap);
    if (!answer) continue;

    // Try to find matching option
    const options = Array.from(select.options);
    const match = options.find(o =>
      o.text.toLowerCase().includes(answer.toLowerCase().substring(0, 8))
    );
    if (match) {
      select.value = match.value;
      select.dispatchEvent(new Event('change', { bubbles: true }));
      await sleep(300 + rand(200));
    }
  }

  // ── Resume upload ─────────────────────────────────────────────────────────
  if (resume?.resume_b64) {
    const fileInput = modal.querySelector('input[type="file"][accept*="pdf"], input[type="file"]');
    if (fileInput) {
      try {
        const blob = b64toBlob(resume.resume_b64, 'application/pdf');
        const file = new File([blob], resume.filename || 'resume.pdf', { type: 'application/pdf' });
        const dt = new DataTransfer();
        dt.items.add(file);
        fileInput.files = dt.files;
        fileInput.dispatchEvent(new Event('change', { bubbles: true }));
        await sleep(1500 + rand(500));
      } catch {}
    }
  }
}

// ── Answer resolution ─────────────────────────────────────────────────────────

async function resolveAnswer(question, profile, answerMap) {
  const key = normalizeQuestion(question);

  // 1. Local cache map (loaded from DB at session start)
  if (answerMap[key]) return answerMap[key];

  // 2. Profile field shortcuts — avoid AI call for common fields
  const profileAnswer = profileShortcut(question, profile);
  if (profileAnswer !== null) {
    // Save back to cache via API so we don't AI-generate this later
    saveAnswerCache(key, question, profileAnswer, 'profile').catch(() => {});
    return profileAnswer;
  }

  // 3. Call our API to AI-generate (checks server-side cache first)
  try {
    const res = await fetch(`${_apiBase}/api/auto-apply/answers/ai-generate`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${_token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ question_raw: question }),
    });
    if (res.ok) {
      const data = await res.json();
      // Update local map for remainder of this session
      answerMap[key] = data.answer;
      return data.answer;
    }
  } catch {}

  return null;
}

function profileShortcut(question, profile) {
  const q = question.toLowerCase();
  if (/(phone|mobile|telephone)/.test(q)) return profile.phone || null;
  if (/linkedin/.test(q)) return profile.linkedin_url || null;
  if (/(city|location|where)/.test(q) && !/(work|remote)/.test(q))
    return profile.city ? `${profile.city}, ${profile.state}` : null;
  if (/years.*(experience|exp)/.test(q)) return profile.years_experience?.toString() || null;
  if (/(authorized|eligible|legally).*(work|employ)/.test(q))
    return profile.work_authorized ? 'Yes' : 'No';
  if (/(visa|sponsorship)/.test(q))
    return profile.requires_visa ? 'Yes' : 'No';
  if (/(salary|compensation|pay).*(expect|desired|minimum)/.test(q))
    return profile.salary_min ? profile.salary_min.toString() : null;
  if (/education|degree|highest/.test(q)) return profile.education_level || null;
  if (/cover letter/.test(q)) return profile.cover_letter || null;
  return null;
}

async function saveAnswerCache(key, raw, answer, source) {
  await fetch(`${_apiBase}/api/auto-apply/answers`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${_token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ question_raw: raw, answer, source }),
  });
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function getLabelFor(input, container) {
  // Try aria-label first
  if (input.getAttribute('aria-label')) return input.getAttribute('aria-label');
  // Try associated <label>
  if (input.id) {
    const label = (container || document).querySelector(`label[for="${input.id}"]`);
    if (label) return label.innerText.trim();
  }
  // Try parent label
  const parentLabel = input.closest('label');
  if (parentLabel) return parentLabel.innerText.trim();
  // Try preceding sibling label or legend
  const prev = input.previousElementSibling;
  if (prev && (prev.tagName === 'LABEL' || prev.tagName === 'LEGEND')) return prev.innerText.trim();
  // Try data-test attribute
  return input.getAttribute('placeholder') || input.getAttribute('name') || null;
}

async function typeIntoField(input, value) {
  input.focus();
  await sleep(200 + rand(150));
  // Clear existing
  input.value = '';
  input.dispatchEvent(new Event('input', { bubbles: true }));
  // Type character by character with random delays (human-like)
  for (const char of value) {
    input.value += char;
    input.dispatchEvent(new Event('input', { bubbles: true }));
    await sleep(30 + rand(60));
  }
  input.dispatchEvent(new Event('change', { bubbles: true }));
  input.blur();
  await sleep(200 + rand(200));
}

function waitForElement(selector, timeout = 5000) {
  return new Promise((resolve) => {
    const existing = document.querySelector(selector);
    if (existing) return resolve(existing);
    const observer = new MutationObserver(() => {
      const el = document.querySelector(selector);
      if (el) { observer.disconnect(); resolve(el); }
    });
    observer.observe(document.body, { childList: true, subtree: true });
    setTimeout(() => { observer.disconnect(); resolve(null); }, timeout);
  });
}

function normalizeQuestion(q) {
  return q.toLowerCase().replace(/[^\w\s]/g, '').replace(/\s+/g, ' ').trim();
}

function b64toBlob(b64, type) {
  const bytes = atob(b64);
  const ab = new ArrayBuffer(bytes.length);
  const ia = new Uint8Array(ab);
  for (let i = 0; i < bytes.length; i++) ia[i] = bytes.charCodeAt(i);
  return new Blob([ab], { type });
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
function rand(max) { return Math.floor(Math.random() * max); }
