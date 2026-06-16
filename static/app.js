document.addEventListener("click", (event) => {
  const opener = event.target.closest("[data-dialog-id]");
  if (opener) {
    const dialog = document.getElementById(opener.dataset.dialogId);
    if (dialog && typeof dialog.showModal === "function") {
      dialog.showModal();
    }
    return;
  }

  const closer = event.target.closest("[data-close-dialog]");
  if (closer) {
    const dialog = closer.closest("dialog");
    if (dialog) dialog.close();
    return;
  }

  const dialog = event.target.closest("dialog");
  if (dialog && event.target === dialog) {
    dialog.close();
  }
});

window.addEventListener("DOMContentLoaded", () => {
  const grid = document.querySelector(".number-grid");
  const active = grid && grid.querySelector("a.active");
  if (grid && active) {
    // centraliza horizontalmente sem mexer no scroll vertical da página
    grid.scrollLeft = active.offsetLeft - grid.clientWidth / 2 + active.clientWidth / 2;
  }

  // Painel lateral com o caderno (PDF) inteiro. Carrega só ao abrir (lazy).
  const bookletToggle = document.querySelector("[data-booklet-toggle]");
  const bookletPanel = document.getElementById("booklet-panel");
  if (bookletToggle && bookletPanel) {
    const frame = bookletPanel.querySelector(".booklet-frame");
    const open = () => {
      if (frame && !frame.src && frame.dataset.bookletSrc) frame.src = frame.dataset.bookletSrc;
      bookletPanel.classList.add("open");
      bookletPanel.setAttribute("aria-hidden", "false");
    };
    const close = () => {
      bookletPanel.classList.remove("open");
      bookletPanel.setAttribute("aria-hidden", "true");
    };
    bookletToggle.addEventListener("click", () => {
      bookletPanel.classList.contains("open") ? close() : open();
    });
    const closer = bookletPanel.querySelector("[data-booklet-close]");
    if (closer) closer.addEventListener("click", close);
    document.addEventListener("keydown", (e) => { if (e.key === "Escape") close(); });
  }

  // Progresso ao vivo da classificação por tema (admin) — serve prova única e "todas".
  document.querySelectorAll("form.classify-progress").forEach((form) => {
    const statusUrl = form.dataset.statusUrl;
    if (!statusUrl) return;
    const idleLabel = form.dataset.idleLabel || "Classificar";
    const busyLabel = form.dataset.busyLabel || "Classificando…";
    const countEl = document.getElementById(form.dataset.count);
    const totalEl = document.getElementById(form.dataset.total);
    const btn = document.getElementById(form.dataset.btn);
    const statusEl = document.getElementById(form.dataset.status);
    let timer = null;

    const stop = () => { if (timer) { clearInterval(timer); timer = null; } };
    const start = () => { if (!timer) { poll(); timer = setInterval(poll, 3000); } };

    async function poll() {
      try {
        const res = await fetch(statusUrl, { cache: "no-store" });
        const data = await res.json();
        if (countEl) countEl.textContent = data.classified;
        if (totalEl) totalEl.textContent = data.total;
        if (data.running) {
          // run_total reflete o lote atual (inclui re-scan forçado); cai pra classified/total se ausente.
          const progress = data.run_total ? `${data.done}/${data.run_total}` : `${data.classified}/${data.total}`;
          if (btn) { btn.disabled = true; btn.textContent = `${busyLabel} (${progress})`; }
          if (statusEl) statusEl.textContent = "Rodando em segundo plano. Pode fechar o navegador — o progresso é salvo no servidor e continua.";
        } else {
          if (btn) { btn.disabled = false; btn.textContent = idleLabel; }
          if (statusEl) {
            if (data.error) statusEl.textContent = "Parou: " + data.error + " — clique para retomar.";
            else if (timer) statusEl.textContent = "Concluído. Recarregue para ver o estado atualizado.";
          }
          stop();
        }
      } catch (e) {
        /* mantém tentando no próximo tick */
      }
    }

    // Ao enviar, começa a acompanhar (o POST recarrega a página já com data-running=1).
    form.addEventListener("submit", () => setTimeout(start, 800));
    if (form.dataset.running === "1") start();
  });
});
