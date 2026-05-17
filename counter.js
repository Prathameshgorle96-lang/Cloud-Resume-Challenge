// =============================================================
//  Cloud Resume Challenge — counter.js  (Step 7: JavaScript)
//  Fetches visitor count from API Gateway → Lambda → DynamoDB
// =============================================================

const API_URL =
  "https://YOUR_API_ID.execute-api.ap-south-1.amazonaws.com/prod/count";
// ☝️ Replace with your actual API Gateway invoke URL after deploy

async function updateVisitorCounter() {
  const counterEl = document.getElementById("counter");

  try {
    const response = await fetch(API_URL, {
      method: "POST",       // POST increments; GET just reads (Lambda handles both)
      headers: { "Content-Type": "application/json" },
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();

    // Animate the counter value in
    animateCount(counterEl, data.visitor_count);
  } catch (err) {
    console.error("Visitor counter error:", err);
    counterEl.textContent = "–";
  }
}

/**
 * Smoothly counts up from 0 to the target number.
 * @param {HTMLElement} el  - element to update
 * @param {number}      end - final visitor count
 */
function animateCount(el, end) {
  const duration = 800;          // ms
  const step     = 16;           // ~60 fps
  const steps    = duration / step;
  const increment = end / steps;
  let current = 0;

  const timer = setInterval(() => {
    current += increment;
    if (current >= end) {
      clearInterval(timer);
      el.textContent = Number(end).toLocaleString();
    } else {
      el.textContent = Math.floor(current).toLocaleString();
    }
  }, step);
}

// Run on page load
document.addEventListener("DOMContentLoaded", updateVisitorCounter);
