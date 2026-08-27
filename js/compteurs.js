(() => {
  const cfg = window.HIADSI_CONFIG || {};
  const COUNTER_NS = cfg.counterNamespace || "hiadsi1959-interfaces";
  const COUNTER_API = String(cfg.counterApiBase || "https://countapi.mileshilliard.com/api/v1").replace(
    /\/$/,
    ""
  );
  const BASELINE = cfg.baselineCounts || {};
  const ACCESS_HASH = String(cfg.statsAccessHash || "").toLowerCase();
  const SESSION_KEY = "hiadsi.statsUnlocked";

  const IFACES = [
    { id: "generation_inputs-QE", label: "QE Input Generator" },
    { id: "generation_pseudos", label: "Pseudopotential Generator" },
    { id: "Interface-QE_v1", label: "Interface-QE v1" },
    { id: "thermo_pw", label: "THERMO_PW v1.1" },
    { id: "supra-QE", label: "Supra-QE v1.1" },
    { id: "QE-Alamode_interface", label: "QE–ALAMODE v1.1" },
  ];

  const gate = document.getElementById("stats-gate");
  const panel = document.getElementById("stats-panel");
  const err = document.getElementById("stats-error");
  const grid = document.getElementById("stats-grid");
  const refreshBtn = document.getElementById("stats-refresh");

  function counterKey(id) {
    return `${COUNTER_NS}_${id}`;
  }

  function baselineFor(id) {
    return Number(BASELINE[id]) || 0;
  }

  function escapeHtml(text) {
    return String(text)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  async function sha256Hex(text) {
    const data = new TextEncoder().encode(text);
    const buf = await crypto.subtle.digest("SHA-256", data);
    return Array.from(new Uint8Array(buf))
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("");
  }

  async function fetchLive(id) {
    try {
      const res = await fetch(`${COUNTER_API}/get/${encodeURIComponent(counterKey(id))}`, {
        cache: "no-store",
      });
      if (res.status === 404) return 0;
      if (!res.ok) return null;
      const data = await res.json();
      if (data && data.error) return 0;
      const n = Number(data.value);
      return Number.isFinite(n) ? n : 0;
    } catch {
      return null;
    }
  }

  async function loadCounts() {
    if (!grid) return;
    grid.innerHTML = '<p class="suggest-empty">Chargement…</p>';
    const rows = await Promise.all(
      IFACES.map(async (iface) => {
        const live = await fetchLive(iface.id);
        const base = baselineFor(iface.id);
        if (live == null) {
          return { ...iface, base, live: null, total: base, ok: false };
        }
        return { ...iface, base, live, total: base + live, ok: true };
      })
    );

    grid.innerHTML = rows
      .map(
        (r) => `
      <article class="stat-card">
        <h3>${escapeHtml(r.label)}</h3>
        <p class="stat-num">${r.total}</p>
        <p class="stat-label">
          ${r.ok ? `baseline ${r.base} + live ${r.live}` : "service indisponible (baseline seule)"}
        </p>
      </article>`
      )
      .join("");
  }

  function unlock() {
    if (gate) gate.hidden = true;
    if (err) err.hidden = true;
    if (panel) panel.hidden = false;
    loadCounts();
  }

  try {
    if (sessionStorage.getItem(SESSION_KEY) === "1") unlock();
  } catch (_) {
    /* ignore */
  }

  if (gate) {
    gate.addEventListener("submit", async (event) => {
      event.preventDefault();
      const code = document.getElementById("stats-code")?.value || "";
      if (!ACCESS_HASH) {
        if (err) {
          err.hidden = false;
          err.textContent = "Hash d’accès non configuré dans js/config.js.";
        }
        return;
      }
      const hash = await sha256Hex(code);
      if (hash !== ACCESS_HASH) {
        if (err) {
          err.hidden = false;
          err.textContent = "Code incorrect.";
        }
        return;
      }
      try {
        sessionStorage.setItem(SESSION_KEY, "1");
      } catch (_) {
        /* ignore */
      }
      unlock();
    });
  }

  if (refreshBtn) {
    refreshBtn.addEventListener("click", () => loadCounts());
  }
})();
