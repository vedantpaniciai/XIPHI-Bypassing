// public-facing JavaScript to be loaded externally (CSP-friendly)

window.Sfdc = window.Sfdc || {};
Sfdc.canvas = Sfdc.canvas || {};

document.addEventListener("DOMContentLoaded", function () {
  if (typeof Sfdc.canvas !== "undefined") {
    Sfdc.canvas.onReady(function () {
      const sr = Sfdc.canvas.context().signedRequest;
      if (sr) {
        console.log("✅ signedRequest found, sending to backend...");
        fetch("/decode-direct", {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body: new URLSearchParams({ signed_request: sr })
        }).then(() => {
          // Reload the page to display the decoded payload
          window.location.href = "/";
        });
      } else {
        console.warn("⚠️ signedRequest not found.");
      }
    });
  }
});
