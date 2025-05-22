document.addEventListener("DOMContentLoaded", function () {
  if (typeof Sfdc === "undefined" || typeof Sfdc.canvas === "undefined") {
    console.warn("❌ Sfdc.canvas is not available. Canvas SDK not loaded or blocked.");
    return;
  }

  Sfdc.canvas.onReady(function () {
    try {
      const context = Sfdc.canvas.context();
      console.log("📦 Canvas context:", context);

      const sr = context.signedRequest;
      if (sr) {
        console.log("✅ signedRequest found, sending to backend...");
        fetch("/decode-direct", {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body: new URLSearchParams({ signed_request: sr })
        }).then(() => {
          console.log("🔄 Reloading to view decoded payload...");
          window.location.href = "/";
        });
      } else {
        console.warn("⚠️ signedRequest not found.");
      }
    } catch (err) {
      console.error("🚨 Error extracting signedRequest:", err);
    }
  });
});
