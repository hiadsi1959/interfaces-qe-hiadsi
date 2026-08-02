(() => {
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

  const form = document.getElementById("form-suggestions");
  const status = document.getElementById("sug-status");
  const list = document.getElementById("liste-suggestions");

  function escapeHtml(text) {
    return String(text)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  async function chargerSuggestions() {
    if (!list) return;
    try {
      const res = await fetch("/api/suggestions");
      const data = await res.json();
      const items = data.suggestions || [];
      if (!items.length) {
        list.innerHTML = '<p class="suggest-empty">Aucune suggestion pour le moment — soyez le premier.</p>';
        return;
      }
      list.innerHTML = items
        .map(
          (s) => `
        <article class="suggest-card">
          <header>
            <span>${escapeHtml(s.nom || "Anonyme")}</span>
            <span class="iface">${escapeHtml(s.interface || "")}</span>
            <span>${escapeHtml(s.date || "")}</span>
          </header>
          <p>${escapeHtml(s.message || "")}</p>
        </article>`
        )
        .join("");
    } catch {
      list.innerHTML = '<p class="suggest-empty">Impossible de charger les suggestions (relancez le site avec ./DEMARRER-SITE.sh).</p>';
    }
  }

  if (form && status) {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      status.className = "suggest-status";
      status.textContent = "Envoi…";

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
          status.textContent = data.error || "Envoi impossible.";
          return;
        }
        status.classList.add("is-ok");
        status.textContent = data.message || "Merci !";
        form.reset();
        chargerSuggestions();
      } catch {
        status.classList.add("is-err");
        status.textContent = "Serveur inaccessible. Lancez ./DEMARRER-SITE.sh puis réessayez.";
      }
    });
  }

  chargerSuggestions();
})();
