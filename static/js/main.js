document.addEventListener("DOMContentLoaded", () => {
  // Konfirmasi sebelum menghapus data
  document.querySelectorAll("form[data-confirm]").forEach((form) => {
    form.addEventListener("submit", (e) => {
      const msg = form.getAttribute("data-confirm") || "Yakin ingin melanjutkan?";
      if (!confirm(msg)) {
        e.preventDefault();
      }
    });
  });

  // Auto-hide flash message setelah beberapa detik
  document.querySelectorAll(".flash").forEach((el, i) => {
    setTimeout(() => {
      el.style.transition = "opacity .4s ease";
      el.style.opacity = "0";
      setTimeout(() => el.remove(), 400);
    }, 4500 + i * 300);
  });
});
