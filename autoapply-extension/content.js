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

  // ── Label extraction ─────────────────────────────────────────────────────────

  function textOf(el) {
    if (!el) return "";
    return (el.innerText || el.textContent || "").replace(/\s+/g, " ").trim();
  }

  function visibleLabel(el) {
    const id = el.id;
    if (id) {
      const lbl = document.querySelector(`label[for="${CSS.escape(id)}"]`);
      const t = textOf(lbl);
      if (t) return t;
    }
    const wrappedLabel = el.closest("label");
    if (wrappedLabel) {
      const t = textOf(wrappedLabel);
      if (t) return t;
    }
    const aria = el.getAttribute("aria-label");
    if (aria) return aria.trim();
    const labelledby = el.getAttribute("aria-labelledby");
    if (labelledby) {
      const parts = labelledby.split(/\s+/).map((id) => textOf(document.getElementById(id))).filter(Boolean);
      if (parts.length) return parts.join(" ");
    }
    if (el.placeholder) return el.placeholder.trim();
    return el.name || "";
  }

  function groupLabel(firstInput) {
    const fieldset = firstInput.closest("fieldset");
    if (fieldset) {
      const legend = fieldset.querySelector(":scope > legend");
      const t = textOf(legend);
      if (t) return t;
    }
    const rg = firstInput.closest('[role="radiogroup"], [role="group"]');
    if (rg) {
      const labelledby = rg.getAttribute("aria-labelledby");
      if (labelledby) {
        const parts = labelledby.split(/\s+/).map((id) => textOf(document.getElementById(id))).filter(Boolean);
        if (parts.length) return parts.join(" ");
      }
      const aria = rg.getAttribute("aria-label");
      if (aria) return aria.trim();
    }
    // LinkedIn sometimes wraps the question in a div above the radio inputs
    const container = firstInput.closest(
      ".jobs-easy-apply-form-element, .fb-dash-form-element, [data-test-form-element]"
    );
    if (container) {
      const q = container.querySelector(
        "legend, .jobs-easy-apply-form-element__label, label, .t-14, .fb-dash-form-element__label"
      );
      const t = textOf(q);
      if (t) return t;
    }
    return firstInput.name || "";
  }

  function visible(el) {
    if (!el) return false;
    const rect = el.getBoundingClientRect();
    if (rect.width === 0 && rect.height === 0) return false;
    const style = getComputedStyle(el);
    return style.visibility !== "hidden" && style.display !== "none";
  }

  // ── Field collection ─────────────────────────────────────────────────────────

  function collectFields(root = document) {
    const fields = [];

    // 1. Text-like inputs + textarea + select
    const textSelectors = [
      'input[type="text"]',
      'input[type="email"]',
      'input[type="tel"]',
      'input[type="url"]',
      'input[type="number"]',
      'input[type="date"]',
      "input:not([type])",
      "textarea",
      "select",
    ];
    Array.from(root.querySelectorAll(textSelectors.join(","))).forEach((el, idx) => {
      if (el.disabled || el.readOnly) return;
      if (!visible(el)) return;
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

    // 2. Radio groups — group by name, then by nearest fieldset/radiogroup
    const radios = Array.from(root.querySelectorAll('input[type="radio"]')).filter(
      (r) => !r.disabled && visible(r)
    );
    const groups = new Map();
    radios.forEach((r, idx) => {
      const container = r.closest('fieldset, [role="radiogroup"], [role="group"]');
      const key = (r.name && r.name.trim())
        || (container && container.id)
        || `jsaa-radio-${idx}`;
      if (!groups.has(key)) groups.set(key, []);
      groups.get(key).push(r);
    });
    groups.forEach((inputs, key) => {
      const first = inputs[0];
      inputs.forEach((r) => r.setAttribute("data-jsaa-group", key));
      const options = inputs.map((r) => {
        const lblFor = r.id ? document.querySelector(`label[for="${CSS.escape(r.id)}"]`) : null;
        const wrap = r.closest("label");
        const optLabel = textOf(lblFor) || textOf(wrap) || r.value || "";
        return { value: r.value || optLabel, label: optLabel || r.value };
      });
      fields.push({
        id: `radio:${key}`,
        label: groupLabel(first),
        tag: "radio-group",
        type: "radio",
        required: inputs.some((i) => i.required || i.getAttribute("aria-required") === "true"),
        options,
      });
    });

    // 3. Standalone checkboxes
    Array.from(root.querySelectorAll('input[type="checkbox"]')).forEach((cb, idx) => {
      if (cb.disabled || !visible(cb)) return;
      const id = cb.id || `jsaa-cb-${idx}`;
      if (!cb.id) cb.setAttribute("data-jsaa-id", id);
      fields.push({
        id,
        label: visibleLabel(cb),
        tag: "checkbox",
        type: "checkbox",
        required: cb.required || cb.getAttribute("aria-required") === "true",
      });
    });

    return fields;
  }

  function findTarget(fieldId) {
    if (fieldId.startsWith("radio:")) {
      return { radioGroup: fieldId.slice(6) };
    }
    return document.getElementById(fieldId) || document.querySelector(`[data-jsaa-id="${CSS.escape(fieldId)}"]`);
  }

  function flash(el) {
    if (!el) return;
    const prev = el.style.outline;
    el.style.outline = "2px solid #6366f1";
    setTimeout(() => { el.style.outline = prev; }, 1200);
  }

  function setValue(target, value) {
    if (value == null || value === "") return false;
    if (target && target.radioGroup !== undefined) {
      const inputs = document.querySelectorAll(
        `input[type="radio"][data-jsaa-group="${CSS.escape(target.radioGroup)}"]`
      );
      const wanted = String(value).toLowerCase().trim();
      for (const r of inputs) {
        const lblFor = r.id ? document.querySelector(`label[for="${CSS.escape(r.id)}"]`) : null;
        const lblText = (textOf(lblFor) || textOf(r.closest("label")) || r.value || "").toLowerCase().trim();
        if (r.value.toLowerCase() === wanted || lblText === wanted || lblText.startsWith(wanted) || wanted.startsWith(lblText)) {
          r.click();
          flash(r.closest("label") || r);
          return true;
        }
      }
      return false;
    }
    const el = target;
    if (!el || !el.tagName) return false;
    if (el.type === "checkbox") {
      const want = String(value).toLowerCase();
      const on = want === "true" || want === "yes" || want === "1" || want === "on" || want === "y";
      if (el.checked !== on) el.click();
      flash(el);
      return true;
    }
    if (el.tagName === "SELECT") {
      const wanted = String(value).toLowerCase();
      const match = Array.from(el.options).find(
        (o) => o.value.toLowerCase() === wanted || o.text.toLowerCase() === wanted
      );
      if (match) el.value = match.value;
      el.dispatchEvent(new Event("change", { bubbles: true }));
      flash(el);
      return !!match;
    }
    el.value = String(value);
    el.dispatchEvent(new Event("input", { bubbles: true }));
    el.dispatchEvent(new Event("change", { bubbles: true }));
    flash(el);
    return true;
  }

  // ── Apply form detection ─────────────────────────────────────────────────────

  function detectApplyForm() {
    const host = location.hostname;
    if (host.includes("linkedin.com")) {
      return document.querySelector(
        ".jobs-easy-apply-content, .jobs-easy-apply-modal, [data-test-modal]"
      ) || null;
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
    panel._hide = setTimeout(() => { panel.style.display = "none"; }, 7000);
  }

  async function onFillClick() {
    try {
      const formRoot = detectApplyForm() || document;
      const fields = collectFields(formRoot);
      if (!fields.length) return showStatus("No form fields detected on this step.", "warn");

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
        const target = findTarget(fieldId);
        if (target && value != null && value !== "") {
          if (setValue(target, value)) filled += 1;
        }
      }
      const skipped = fields.length - filled;
      showStatus(
        `Filled ${filled} of ${fields.length} fields. ${skipped ? `${skipped} need your review (often protected / custom questions).` : "Review before submitting."}`,
        filled ? "ok" : "warn"
      );
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
