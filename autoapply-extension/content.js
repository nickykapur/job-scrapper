(function () {
  "use strict";

  const BTN_ID = "jsautoapply-fab";
  const PANEL_ID = "jsautoapply-panel";
  const FILL_TRACKING = new WeakMap(); // element → { fieldKey, filledValue, fieldId }
  const RADIO_TRACKING = new Map();    // radioGroupKey → { fieldKey, filledValue, fieldId }

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

  // ── ATS + job context detection ──────────────────────────────────────────────

  function detectAts() {
    const host = location.hostname;
    if (host.includes("linkedin.com")) return "linkedin";
    if (host.includes("greenhouse.io")) return "greenhouse";
    if (host.includes("lever.co")) return "lever";
    if (host.includes("myworkdayjobs.com")) return "workday";
    return "generic";
  }

  function scrapeJobContext() {
    const ctx = { ats: detectAts(), url: location.href, host: location.hostname };
    if (ctx.ats === "linkedin") {
      const title = document.querySelector(
        ".job-details-jobs-unified-top-card__job-title, .jobs-unified-top-card__job-title, h1.t-24"
      );
      const company = document.querySelector(
        ".job-details-jobs-unified-top-card__company-name a, .jobs-unified-top-card__company-name a, .jobs-unified-top-card__company-name"
      );
      const loc = document.querySelector(
        ".job-details-jobs-unified-top-card__primary-description-container .tvm__text, .jobs-unified-top-card__bullet"
      );
      if (title) ctx.job_title = textOf(title);
      if (company) ctx.company = textOf(company);
      if (loc) ctx.job_location = textOf(loc);
    } else {
      const h1 = document.querySelector("h1");
      if (h1) ctx.job_title = textOf(h1);
    }
    // Extract job_country from "… · Dublin, Ireland" / "Remote · Germany" etc.
    if (ctx.job_location) {
      const parts = ctx.job_location.split(",").map((p) => p.trim()).filter(Boolean);
      if (parts.length) ctx.job_country = parts[parts.length - 1];
    }
    return ctx;
  }

  // ── Field collection ─────────────────────────────────────────────────────────

  function collectFields(root = document) {
    const fields = [];

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
      const currentVal = el.value != null ? String(el.value).trim() : "";
      fields.push({
        id,
        label: visibleLabel(el),
        tag: el.tagName.toLowerCase(),
        type: el.type || null,
        required: el.required || el.getAttribute("aria-required") === "true",
        hadValue: currentVal !== "",
        options: el.tagName === "SELECT"
          ? Array.from(el.options).map((o) => ({ value: o.value, label: o.text }))
          : undefined,
      });
    });

    // Radio groups
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
        hadValue: inputs.some((i) => i.checked),
        options,
      });
    });

    // Checkboxes
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
        hadValue: cb.checked,
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

  function flash(el, color) {
    if (!el) return;
    el.style.outline = `2px solid ${color}`;
    el.style.outlineOffset = "2px";
    setTimeout(() => { el.style.outline = ""; el.style.outlineOffset = ""; }, 1500);
  }

  function setValue(target, value, sourceColor) {
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
          flash(r.closest("label") || r, sourceColor);
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
      flash(el, sourceColor);
      return true;
    }
    if (el.tagName === "SELECT") {
      const wanted = String(value).toLowerCase();
      const match = Array.from(el.options).find(
        (o) => o.value.toLowerCase() === wanted || o.text.toLowerCase() === wanted
      );
      if (match) el.value = match.value;
      el.dispatchEvent(new Event("change", { bubbles: true }));
      flash(el, sourceColor);
      return !!match;
    }
    el.value = String(value);
    el.dispatchEvent(new Event("input", { bubbles: true }));
    el.dispatchEvent(new Event("change", { bubbles: true }));
    flash(el, sourceColor);
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
    panel._hide = setTimeout(() => { panel.style.display = "none"; }, 9000);
  }

  // ── Learning: track + record user edits ─────────────────────────────────────

  function trackFilledField(target, field, fieldKey, filledValue, jobContext, ats) {
    const record = {
      fieldKey, filledValue, fieldId: field.id, jobContext,
      label: field.label, fieldType: field.type, ats,
    };
    if (target && target.radioGroup !== undefined) {
      RADIO_TRACKING.set(target.radioGroup, record);
      return;
    }
    if (target instanceof Element) {
      FILL_TRACKING.set(target, record);
      attachRecorder(target);
    }
  }

  function trackUnfilledField(target, field, fieldKey, jobContext, ats) {
    const record = {
      fieldKey, filledValue: null, fieldId: field.id, jobContext,
      label: field.label, fieldType: field.type, ats,
    };
    if (target && target.radioGroup !== undefined) {
      RADIO_TRACKING.set(target.radioGroup, record);
      return;
    }
    if (target instanceof Element) {
      FILL_TRACKING.set(target, record);
      attachRecorder(target);
    }
  }

  function debounce(fn, ms) {
    let t;
    return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); };
  }

  function attachRecorder(el) {
    if (el._jsaaRecorder) return;
    const handler = debounce(() => recordCurrent(el), 800);
    el.addEventListener("change", handler);
    el.addEventListener("blur", handler);
    if (el.tagName === "TEXTAREA" || el.type === "text" || el.type === "email" || el.type === "tel" || el.type === "url" || el.type === "number") {
      el.addEventListener("input", handler);
    }
    el._jsaaRecorder = handler;
  }

  async function recordCurrent(el) {
    const rec = FILL_TRACKING.get(el);
    if (!rec) return;
    let value = el.type === "checkbox" ? (el.checked ? "yes" : "no") : el.value;
    if (value == null || value === "") return;
    if (String(value) === String(rec.filledValue)) return;

    // Unknown/custom_question: auto-teach so future pages remember this answer.
    if (!rec.fieldKey || rec.fieldKey === "unknown" || rec.fieldKey === "custom_question") {
      if (!rec.label || !rec.ats) return;
      try {
        const res = await send("teachField", {
          ats: rec.ats,
          label: rec.label,
          fieldType: rec.fieldType || el.type || null,
          value: String(value),
          jobContext: rec.jobContext,
        });
        if (res?.field_key) rec.fieldKey = res.field_key;
        rec.filledValue = value;
      } catch (_) {}
      return;
    }

    const source = rec.filledValue ? "user_edited_our_fill" : "user_typed";
    try {
      await send("recordAnswer", {
        fieldKey: rec.fieldKey,
        value: String(value),
        source,
        jobContext: rec.jobContext,
      });
      rec.filledValue = value;
    } catch (e) {
      // swallow — don't break the page
    }
  }

  // Record radio group selections via delegated click on the modal root
  function hookRadioRecorders(formRoot) {
    if (formRoot._jsaaRadioHooked) return;
    formRoot._jsaaRadioHooked = true;
    formRoot.addEventListener("change", async (e) => {
      const r = e.target;
      if (!(r instanceof HTMLInputElement) || r.type !== "radio") return;
      const group = r.getAttribute("data-jsaa-group");
      if (!group) return;
      const rec = RADIO_TRACKING.get(group);
      if (!rec) return;
      const lblFor = r.id ? document.querySelector(`label[for="${CSS.escape(r.id)}"]`) : null;
      const lblText = textOf(lblFor) || textOf(r.closest("label")) || r.value;
      if (!lblText) return;
      if (String(lblText).toLowerCase() === String(rec.filledValue || "").toLowerCase()) return;

      if (!rec.fieldKey || rec.fieldKey === "unknown" || rec.fieldKey === "custom_question") {
        if (!rec.label || !rec.ats) return;
        try {
          const res = await send("teachField", {
            ats: rec.ats, label: rec.label, fieldType: rec.fieldType || "radio",
            value: String(lblText), jobContext: rec.jobContext,
          });
          if (res?.field_key) rec.fieldKey = res.field_key;
          rec.filledValue = lblText;
        } catch (_) {}
        return;
      }

      const source = rec.filledValue ? "user_edited_our_fill" : "user_typed";
      try {
        await send("recordAnswer", {
          fieldKey: rec.fieldKey,
          value: String(lblText),
          source,
          jobContext: rec.jobContext,
        });
        rec.filledValue = lblText;
      } catch (_) {}
    });
  }

  // ── Teach-me chip: ask once, remember forever ───────────────────────────────

  function currentValueOf(target) {
    if (target && target.radioGroup !== undefined) {
      const inputs = document.querySelectorAll(
        `input[type="radio"][data-jsaa-group="${CSS.escape(target.radioGroup)}"]`
      );
      for (const r of inputs) {
        if (r.checked) {
          const lblFor = r.id ? document.querySelector(`label[for="${CSS.escape(r.id)}"]`) : null;
          return textOf(lblFor) || textOf(r.closest("label")) || r.value || "";
        }
      }
      return "";
    }
    if (!(target instanceof HTMLElement)) return "";
    if (target.type === "checkbox") return target.checked ? "yes" : "no";
    return target.value || "";
  }

  function anchorFor(target) {
    if (target && target.radioGroup !== undefined) {
      const first = document.querySelector(
        `input[type="radio"][data-jsaa-group="${CSS.escape(target.radioGroup)}"]`
      );
      return first ? (first.closest("fieldset, [role='radiogroup'], [role='group']") || first.parentElement) : null;
    }
    return target instanceof HTMLElement ? target : null;
  }

  function attachTeachChip(field, target, ats, jobContext) {
    const anchor = anchorFor(target);
    if (!anchor || anchor._jsaaChip) return;
    const chip = document.createElement("button");
    chip.type = "button";
    chip.className = "jsautoapply-chip";
    chip.textContent = "💬 Teach me";
    chip.title = "Answer once — I'll remember for future applications.";
    chip.addEventListener("click", async (e) => {
      e.preventDefault();
      e.stopPropagation();
      const existing = currentValueOf(target);
      const answer = window.prompt(
        `Save an answer for:\n\n"${field.label}"\n\nI'll reuse this on every future application.`,
        existing || ""
      );
      if (answer == null) return;
      const trimmed = String(answer).trim();
      if (!trimmed) return;
      try {
        const res = await send("teachField", {
          ats, label: field.label, fieldType: field.type,
          value: trimmed, jobContext,
        });
        setValue(target, trimmed, SOURCE_COLORS.user_own);
        if (res?.field_key && target instanceof Element) {
          const rec = FILL_TRACKING.get(target) || {};
          FILL_TRACKING.set(target, { ...rec, fieldKey: res.field_key, filledValue: trimmed, jobContext });
        }
        chip.textContent = "✓ Saved";
        chip.disabled = true;
        setTimeout(() => chip.remove(), 2000);
      } catch (err) {
        chip.textContent = "⚠ " + (err.message || "failed");
        setTimeout(() => { chip.textContent = "💬 Teach me"; }, 2500);
      }
    });
    anchor._jsaaChip = chip;
    // Place chip right after the anchor
    if (anchor.parentNode) anchor.parentNode.insertBefore(chip, anchor.nextSibling);
  }

  // ── Main fill flow ──────────────────────────────────────────────────────────

  const SOURCE_COLORS = {
    user_own: "#22c55e",       // green — their own prior answer
    cv_profile: "#6366f1",     // blue — from CV
    cohort: "#f59e0b",         // yellow — cohort suggestion (confirm with one click)
    mapper: "#8b5cf6",         // purple — Claude mapper fallback
  };

  async function onFillClick() {
    try {
      const formRoot = detectApplyForm() || document;
      const fields = collectFields(formRoot);
      if (!fields.length) return showStatus("No form fields detected on this step.", "warn");

      showStatus(`Classifying ${fields.length} fields…`, "info");

      const profile = await send("getProfile", {});
      if (!profile?.exists) return showStatus("Upload your CV first on the JobScraper site.", "warn");

      const ats = detectAts();
      const jobContext = scrapeJobContext();
      hookRadioRecorders(formRoot);

      // Step 1 — classify labels into canonical keys
      const classifyInput = fields.map((f) => ({ id: f.id, label: f.label, type: f.type }));
      let classify = { mapping: {} };
      try {
        classify = await send("classifyFields", { ats, fields: classifyInput });
      } catch (e) {
        console.warn("classifyFields failed:", e.message);
      }

      // Step 2 — resolve canonical keys to values (user_own / cv_profile / cohort)
      const keys = Object.values(classify.mapping || {}).filter(Boolean);
      const uniqueKeys = Array.from(new Set(keys));
      let resolveRes = { resolutions: {} };
      try {
        if (uniqueKeys.length) {
          resolveRes = await send("resolveFields", { fieldKeys: uniqueKeys, jobContext });
        }
      } catch (e) {
        console.warn("resolveFields failed:", e.message);
      }

      // Step 3 — fill what we can; collect custom_question / unknown for mapper fallback
      let filled = 0;
      let alreadyFilled = 0;
      let suggestions = 0;
      const fallbackFields = [];
      for (const f of fields) {
        const target = findTarget(f.id);
        const fieldKey = classify.mapping?.[f.id] || "unknown";

        // Respect pre-filled fields (e.g. LinkedIn email/phone) — still track for learning
        if (f.hadValue) {
          alreadyFilled += 1;
          if (target) trackUnfilledField(target, f, fieldKey, jobContext, ats);
          continue;
        }

        if (fieldKey === "custom_question" || fieldKey === "unknown") {
          fallbackFields.push(f);
          if (target) {
            trackUnfilledField(target, f, fieldKey, jobContext, ats);
            attachTeachChip(f, target, ats, jobContext);
          }
          continue;
        }
        const resolution = resolveRes.resolutions?.[fieldKey];
        if (resolution && resolution.value != null && resolution.value !== "") {
          const color = SOURCE_COLORS[resolution.source] || SOURCE_COLORS.cv_profile;
          const ok = setValue(target, resolution.value, color);
          if (ok) {
            filled += 1;
            if (resolution.source === "cohort") suggestions += 1;
            if (target) trackFilledField(target, f, fieldKey, resolution.value, jobContext, ats);
          } else if (target) {
            trackUnfilledField(target, f, fieldKey, jobContext, ats);
          }
        } else if (target) {
          trackUnfilledField(target, f, fieldKey, jobContext, ats);
          attachTeachChip(f, target, ats, jobContext);
        }
      }

      // Step 4 — Claude mapper for the remainder (custom questions)
      if (fallbackFields.length) {
        try {
          const { mapping = {} } = await send("mapFields", { fields: fallbackFields, jobContext });
          for (const [fieldId, value] of Object.entries(mapping)) {
            if (value == null || value === "") continue;
            const target = findTarget(fieldId);
            if (!target) continue;
            if (setValue(target, value, SOURCE_COLORS.mapper)) {
              filled += 1;
              // Mapper fills aren't tied to a canonical key, so don't record
            }
          }
        } catch (e) {
          console.warn("mapFields fallback failed:", e.message);
        }
      }

      const needsReview = fields.length - filled - alreadyFilled;
      const parts = [`Filled ${filled} of ${fields.length}.`];
      if (alreadyFilled) parts.push(`${alreadyFilled} already filled.`);
      if (suggestions) parts.push(`${suggestions} yellow suggestion(s) — confirm or edit.`);
      if (needsReview > 0) parts.push(`${needsReview} left for your review.`);
      showStatus(parts.join(" "), filled ? "ok" : "warn");
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
