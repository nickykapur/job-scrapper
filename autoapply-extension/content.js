(function () {
  "use strict";

  const BTN_ID = "jsautoapply-fab";
  const PANEL_ID = "jsautoapply-panel";

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

  // ── Field collection ─────────────────────────────────────────────────────────

  function visibleLabel(el) {
    const id = el.id;
    if (id) {
      const lbl = document.querySelector(`label[for="${CSS.escape(id)}"]`);
      if (lbl?.innerText) return lbl.innerText.trim();
    }
    const wrappedLabel = el.closest("label");
    if (wrappedLabel?.innerText) return wrappedLabel.innerText.trim();
    const aria = el.getAttribute("aria-label");
    if (aria) return aria.trim();
    const labelledby = el.getAttribute("aria-labelledby");
    if (labelledby) {
      const lbl = document.getElementById(labelledby);
      if (lbl?.innerText) return lbl.innerText.trim();
    }
    if (el.placeholder) return el.placeholder.trim();
    return el.name || "";
  }

  function collectFields(root = document) {
    const selectors = [
      'input[type="text"]',
      'input[type="email"]',
      'input[type="tel"]',
      'input[type="url"]',
      'input[type="number"]',
      "input:not([type])",
      "textarea",
      "select",
    ];
    const els = Array.from(root.querySelectorAll(selectors.join(",")));
    const fields = [];
    els.forEach((el, idx) => {
      if (el.type === "hidden" || el.disabled || el.readOnly) return;
      const rect = el.getBoundingClientRect();
      if (rect.width === 0 && rect.height === 0) return;
      const id = el.id || `jsaa-${idx}`;
      if (!el.id) el.setAttribute("data-jsaa-id", id);
      fields.push({
        id,
        label: visibleLabel(el),
        tag: el.tagName.toLowerCase(),
        type: el.type || null,
        required: el.required || el.getAttribute("aria-required") === "true",
        options: el.tagName === "SELECT"
          ? Array.from(el.options).map((o) => ({ value: o.value, label: o.text }))
          : undefined,
      });
    });
    return fields;
  }

  function findElement(fieldId) {
    return document.getElementById(fieldId) || document.querySelector(`[data-jsaa-id="${CSS.escape(fieldId)}"]`);
  }

  function setValue(el, value) {
    if (value == null) return;
    if (el.tagName === "SELECT") {
      const wanted = String(value).toLowerCase();
      const match = Array.from(el.options).find(
        (o) => o.value.toLowerCase() === wanted || o.text.toLowerCase() === wanted,
      );
      if (match) el.value = match.value;
    } else {
      el.value = String(value);
    }
    el.dispatchEvent(new Event("input", { bubbles: true }));
    el.dispatchEvent(new Event("change", { bubbles: true }));
    el.style.outline = "2px solid #6366f1";
    setTimeout(() => { el.style.outline = ""; }, 1200);
  }

  // ── Apply form detection ─────────────────────────────────────────────────────

  function detectApplyForm() {
    const host = location.hostname;
    if (host.includes("linkedin.com")) {
      return document.querySelector(".jobs-easy-apply-content, .jobs-easy-apply-modal") || null;
    }
    if (host.includes("greenhouse.io") || host.includes("lever.co")) {
      return document.querySelector('form[action*="apply"], form#application_form, form.application-form') || null;
    }
    if (host.includes("myworkdayjobs.com")) {
      return document.querySelector('[data-automation-id="applyFlow"]') || null;
    }
    return null;
  }

  // ── UI ───────────────────────────────────────────────────────────────────────

  function injectFab() {
    if (document.getElementById(BTN_ID)) return;
    const btn = document.createElement("button");
    btn.id = BTN_ID;
    btn.textContent = "Auto-Fill";
    btn.addEventListener("click", onFillClick);
    document.body.appendChild(btn);
  }

  function showStatus(text, kind = "info") {
    let panel = document.getElementById(PANEL_ID);
    if (!panel) {
      panel = document.createElement("div");
      panel.id = PANEL_ID;
      document.body.appendChild(panel);
    }
    panel.textContent = text;
    panel.dataset.kind = kind;
    panel.style.display = "block";
    clearTimeout(panel._hide);
    panel._hide = setTimeout(() => { panel.style.display = "none"; }, 5000);
  }

  async function onFillClick() {
    try {
      const formRoot = detectApplyForm() || document;
      const fields = collectFields(formRoot);
      if (!fields.length) return showStatus("No form fields detected.", "warn");

      showStatus(`Reading profile and mapping ${fields.length} fields…`, "info");
      const profile = await send("getProfile", {});
      if (!profile?.exists) return showStatus("Upload your CV first on the JobScraper site.", "warn");

      const jobContext = {
        url: location.href,
        title: document.title,
        host: location.hostname,
      };
      const { mapping = {} } = await send("mapFields", { fields, jobContext });

      let filled = 0;
      for (const [fieldId, value] of Object.entries(mapping)) {
        const el = findElement(fieldId);
        if (el && value != null && value !== "") {
          setValue(el, value);
          filled += 1;
        }
      }
      showStatus(`Filled ${filled} of ${fields.length} fields. Review before submitting.`, filled ? "ok" : "warn");
    } catch (err) {
      if (err.message === "not_authenticated" || err.message === "unauthorized") {
        showStatus("Open the extension and log in first.", "warn");
      } else {
        showStatus(`Error: ${err.message}`, "error");
      }
    }
  }

  // ── Bootstrap ────────────────────────────────────────────────────────────────

  const observer = new MutationObserver(() => {
    if (detectApplyForm()) injectFab();
  });
  observer.observe(document.body, { childList: true, subtree: true });
  if (detectApplyForm()) injectFab();
})();
