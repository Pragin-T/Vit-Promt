async function runPhishingDetection() {
  try {
    const pageText = document.body.innerText;
    const pageUrl = window.location.href;

    const response = await fetch("https://your-backend-domain/api/phishing-check/", {  // provide your real URL
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        // Add Authorization if needed
      },
      body: JSON.stringify({
        content: pageText,
        url: pageUrl
      })
    });

    const result = await response.json();

    if (result.isPhishing) {
      alert("Warning: Phishing detected! Reason: " + (result.reason || "Suspicious content"));
      // Add UI warning, badge, or block page here
    } else {
      console.log("Page appears safe.");
    }
  } catch (error) {
    console.error("Phishing detection error:", error);
  }
}
