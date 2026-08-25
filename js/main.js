(() => {
  const cfg = window.HIADSI_CONFIG || {};
  const COUNTER_NS = cfg.counterNamespace || "hiadsi1959-interfaces";
  const COUNTER_API = String(cfg.counterApiBase || "https://countapi.mileshilliard.com/api/v1").replace(/\/$/, "");
  const BASELINE = cfg.baselineCounts || {};
  const NOTIFY_EMAIL = String(cfg.notificationEmail || "").trim();

  const IFACES = [
    { id: "generation_inputs-QE", label: "QE Input Generator" },
    { id: "generation_pseudos", label: "Pseudopotential Generator" },
    { id: "Interface-QE_v1", label: "Interface-QE v1" },
    { id: "thermo_pw", label: "THERMO_PW v1.1" },
    { id: "supra-QE", label: "Supra-QE" },
    { id: "QE-Alamode_interface", label: "QE–ALAMODE" },
  ];

  function counterKey(id) {
    return `${COUNTER_NS}_${id}`;
  }

  function baselineFor(id) {
    return Number(BASELINE[id]) || 0;
  }

  function totalCount(id, live) {
    return baselineFor(id) + (Number(live) || 0);
  }

  /* Presentation language toggle (FR / EN) */
  const langBtns = document.querySelectorAll("[data-pres-lang]");
  const langPanels = document.querySelectorAll("[data-pres-panel]");
  function setPresLang(lang) {
    langBtns.forEach((btn) => {
      const on = btn.getAttribute("data-pres-lang") === lang;
      btn.classList.toggle("is-active", on);
      btn.setAttribute("aria-pressed", on ? "true" : "false");
    });
    langPanels.forEach((panel) => {
      const on = panel.getAttribute("data-pres-panel") === lang;
      panel.hidden = !on;
      panel.classList.toggle("is-active", on);
    });
    try {
      localStorage.setItem("hiadsi.presLang", lang);
    } catch (_) {
      /* ignore */
    }
  }
  langBtns.forEach((btn) => {
    btn.addEventListener("click", () => setPresLang(btn.getAttribute("data-pres-lang") || "fr"));
  });
  try {
    const saved = localStorage.getItem("hiadsi.presLang");
    if (saved === "en" || saved === "fr") setPresLang(saved);
  } catch (_) {
    /* ignore */
  }

  const nodes = document.querySelectorAll(".reveal");
  if (nodes.length) {
    if (!("IntersectionObserver" in window)) {
      nodes.forEach((el) => el.classList.add("is-visible"));
    } else {
      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (!entry.isIntersecting) return;
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          });
        },
        { threshold: 0.18, rootMargin: "0px 0px -40px 0px" }
      );
      nodes.forEach((el) => observer.observe(el));
    }
  }

  function escapeHtml(text) {
    return String(text)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  async function bumpCounter(id) {
    try {
      const res = await fetch(
        `${COUNTER_API}/hit/${encodeURIComponent(counterKey(id))}`,
        { cache: "no-store" }
      );
      if (!res.ok) return null;
      const data = await res.json();
      const live = Number(data.value);
      if (!Number.isFinite(live)) return null;
      return totalCount(id, live);
    } catch {
      return null;
    }
  }

  /* ——— Feedback ——— */
  const form = document.getElementById("form-suggestions");
  const status = document.getElementById("sug-status");
  const list = document.getElementById("liste-suggestions");

  async function loadFeedback() {
    if (!list) return;
    try {
      const res = await fetch("/api/suggestions");
      const data = await res.json();
      const items = data.suggestions || [];
      if (!items.length) {
        list.innerHTML =
          '<p class="suggest-empty">No feedback yet — be the first to share yours.</p>';
        return;
      }
      list.innerHTML = items
        .map(
          (s) => `
        <article class="suggest-card">
          <header>
            <span>${escapeHtml(s.nom || "Anonymous")}</span>
            <span class="iface">${escapeHtml(s.interface || "")}</span>
            <span>${escapeHtml(s.date || "")}</span>
          </header>
          <p>${escapeHtml(s.message || "")}</p>
        </article>`
        )
        .join("");
    } catch {
      list.innerHTML =
        '<p class="suggest-empty">Feedback appears when the local site server is running (<code>./DEMARRER-SITE.sh</code>).</p>';
    }
  }

  if (form && status) {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      status.className = "suggest-status";
      status.textContent = "Sending…";

      const payload = {
        nom: form.nom.value.trim(),
        email: form.email.value.trim(),
        interface: form.interface.value,
        message: form.message.value.trim(),
      };

      try {
        const res = await fetch("/api/suggestions", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        const data = await res.json();
        if (!res.ok || !data.ok) {
          status.classList.add("is-err");
          status.textContent = data.error || "Could not send.";
          return;
        }
        status.classList.add("is-ok");
        status.textContent = data.message || "Thank you!";
        form.reset();
        loadFeedback();
      } catch {
        status.classList.add("is-err");
        status.textContent =
          "Server unavailable. Start ./DEMARRER-SITE.sh and try again.";
      }
    });
  }

  /* ——— Downloads ——— */
  const modal = document.getElementById("dl-modal");
  const dlForm = document.getElementById("form-download");
  const dlStatus = document.getElementById("dl-status");
  const dlIfaceLabel = document.getElementById("dl-modal-iface");
  let pending = null;

  function openModal(button) {
    pending = {
      id: button.getAttribute("data-interface"),
      label: button.getAttribute("data-label"),
      file: button.getAttribute("data-file"),
    };
    if (dlIfaceLabel) dlIfaceLabel.textContent = pending.label || pending.id;
    if (dlStatus) {
      dlStatus.className = "suggest-status";
      dlStatus.textContent = "";
    }
    if (dlForm) dlForm.reset();
    if (modal) {
      modal.hidden = false;
      document.body.classList.add("modal-open");
      const nom = document.getElementById("dl-nom");
      if (nom) nom.focus();
    }
  }

  function closeModal() {
    if (modal) modal.hidden = true;
    document.body.classList.remove("modal-open");
    pending = null;
  }

  document.querySelectorAll(".btn-download[data-file]").forEach((btn) => {
    btn.addEventListener("click", () => openModal(btn));
  });

  if (modal) {
    modal.querySelectorAll("[data-dl-close]").forEach((el) => {
      el.addEventListener("click", closeModal);
    });
  }

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && modal && !modal.hidden) closeModal();
  });

  function startFileDownload(filePath) {
    const a = document.createElement("a");
    a.href = filePath;
    a.download = "";
    a.rel = "noopener";
    document.body.appendChild(a);
    a.click();
    a.remove();
  }

  async function notifyAuthor(payload) {
    if (!NOTIFY_EMAIL) return false;
    try {
      const res = await fetch(`https://formsubmit.co/ajax/${encodeURIComponent(NOTIFY_EMAIL)}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify({
          _subject: `[S. HIADSI] Download — ${payload.interface}`,
          _template: "table",
          nom: payload.nom,
          organisme: payload.organisme,
          email: payload.email || "(not provided)",
          interface: payload.interface,
          total_downloads: payload.total != null ? String(payload.total) : "(n/a)",
          date: payload.date,
        }),
      });
      return res.ok;
    } catch {
      return false;
    }
  }

  async function logLocal(payload) {
    try {
      const res = await fetch("/api/telechargements", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) return null;
      const data = await res.json();
      return data.ok ? data : null;
    } catch {
      return null;
    }
  }

  if (dlForm) {
    dlForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      if (!pending) return;

      const nom = dlForm.nom.value.trim();
      const organisme = dlForm.organisme.value.trim();
      const email = dlForm.email.value.trim();

      if (nom.length < 2) {
        dlStatus.className = "suggest-status is-err";
        dlStatus.textContent = "Please enter your name.";
        return;
      }
      if (organisme.length < 2) {
        dlStatus.className = "suggest-status is-err";
        dlStatus.textContent = "Please enter your institution or laboratory.";
        return;
      }

      dlStatus.className = "suggest-status";
      dlStatus.textContent = "Saving…";

      const payload = {
        nom,
        organisme,
        email,
        interface: pending.id,
        date: new Date().toISOString().slice(0, 19).replace("T", " "),
      };

      const filePath = pending.file;
      const ifaceId = pending.id;

      await logLocal(payload);
      const newCount = await bumpCounter(ifaceId);
      await notifyAuthor({ ...payload, total: newCount });

      startFileDownload(filePath);
      dlStatus.className = "suggest-status is-ok";
      dlStatus.textContent = "Download started. Thank you.";
      setTimeout(closeModal, 700);
    });
  }

  loadFeedback();
})();
