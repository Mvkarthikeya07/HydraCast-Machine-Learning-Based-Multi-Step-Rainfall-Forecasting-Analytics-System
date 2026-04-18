// ── Rain level thresholds ──────────────────────────────────────
// Adjust these mm values to match your region's rainfall patterns
function rainLevel(mm) {
  if (mm < 1)  return { label: "Dry",           cls: "lvl-none", icon: "☀️" };
  if (mm < 5)  return { label: "Light drizzle", cls: "lvl-low",  icon: "🌦️" };
  if (mm < 15) return { label: "Moderate rain", cls: "lvl-mod",  icon: "🌧️" };
  return           { label: "Heavy rain",    cls: "lvl-high", icon: "⛈️" };
}

// Bar fill colour matches the badge colour
const barColors = {
  "lvl-none": "rgba(29,158,117,0.7)",
  "lvl-low" : "rgba(55,138,221,0.7)",
  "lvl-mod" : "rgba(186,117,23,0.8)",
  "lvl-high": "rgba(226,75,74,0.8)",
};

// ── Chart instance ─────────────────────────────────────────────
let chart;

// ── Main loader ────────────────────────────────────────────────
async function loadData() {
  const district = document.getElementById("district").value;
  document.getElementById("selectedDistrict").innerText = district;

  try {
    // Fetch history + forecast + single prediction in parallel
    const [histRes, foreRes, predRes] = await Promise.all([
      fetch(`/history/${district}`),
      fetch(`/forecast/${district}`),
      fetch("/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ district }),
      }),
    ]);

    const histData = await histRes.json();
    const foreData = await foreRes.json();
    const predData = await predRes.json();

    // ── Hero: tomorrow's prediction ──────────────────────────
    document.getElementById("prediction").innerText =
      (predData.prediction ?? 0).toFixed(2) + " mm";

    // ── Summary metric cards ─────────────────────────────────
    if (foreData.rainfall.length > 0) {
      const peak    = Math.max(...foreData.rainfall);
      const total   = foreData.rainfall.reduce((a, b) => a + b, 0);
      const peakIdx = foreData.rainfall.indexOf(peak);

      document.getElementById("cardTotal").innerText   = total.toFixed(2) + " mm";
      document.getElementById("cardPeak").innerText    = peak.toFixed(2) + " mm";
      document.getElementById("cardPeakDay").innerText = foreData.dates[peakIdx] ?? "--";
    }

    // ── Build combined chart ─────────────────────────────────
    const allDates = histData.dates.concat(foreData.dates);
    const histLen  = histData.rainfall.length;

    // Forecast line: null for all history except last point (bridge)
    const forecastLine = new Array(histLen - 1)
      .fill(null)
      .concat([histData.rainfall[histLen - 1]])
      .concat(foreData.rainfall);

    // Past dataset: pad with nulls after history ends
    const pastFull = histData.rainfall.concat(
      new Array(foreData.rainfall.length).fill(null)
    );

    const ctx = document.getElementById("chart").getContext("2d");
    if (chart) chart.destroy();

    chart = new Chart(ctx, {
      type: "line",
      data: {
        labels: allDates,
        datasets: [
          {
            label: "Past Rainfall",
            data: pastFull,
            borderColor: "#4facfe",
            backgroundColor: "rgba(79,172,254,0.12)",
            fill: true,
            tension: 0.3,
            pointRadius: 1.5,
            pointHoverRadius: 5,
            borderWidth: 2,
            spanGaps: false,
          },
          {
            label: "Forecast",
            data: forecastLine,
            borderColor: "#ff6b6b",
            borderDash: [6, 4],
            backgroundColor: "rgba(255,107,107,0.08)",
            fill: true,
            tension: 0.3,
            pointRadius: 4,
            pointHoverRadius: 6,
            borderWidth: 2,
            spanGaps: false,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: "index", intersect: false },
        plugins: {
          legend: { display: false },  // we use custom HTML legend
          tooltip: {
            callbacks: {
              label: (ctx) =>
                ctx.raw !== null
                  ? `${ctx.dataset.label}: ${ctx.raw.toFixed(2)} mm`
                  : "",
            },
          },
        },
        scales: {
          x: {
            grid: { color: "rgba(255,255,255,0.1)" },
            ticks: {
              color: "rgba(255,255,255,0.7)",
              font: { size: 11 },
              maxTicksLimit: 14,
              maxRotation: 45,
              autoSkip: true,
            },
          },
          y: {
            beginAtZero: true,
            grid: { color: "rgba(255,255,255,0.1)" },
            ticks: {
              color: "rgba(255,255,255,0.7)",
              font: { size: 11 },
              callback: (v) => v + " mm",
            },
          },
        },
      },
    });

    // ── Forecast strip (day cards) ───────────────────────────
    const strip = document.getElementById("forecastStrip");
    strip.innerHTML = "";
    foreData.dates.forEach((date, i) => {
      const mm  = foreData.rainfall[i];
      const lvl = rainLevel(mm);
      strip.innerHTML += `
        <div class="day-card">
          <div class="day-date">${date}</div>
          <div class="day-mm">${mm.toFixed(2)} mm</div>
          <span class="level-badge ${lvl.cls}">${lvl.icon} ${lvl.label}</span>
        </div>`;
    });

    // ── Results table (what your mam asked for) ──────────────
    const tbody = document.getElementById("fcTableBody");
    tbody.innerHTML = "";

    const peak = foreData.rainfall.length > 0
      ? Math.max(...foreData.rainfall)
      : 1;

    foreData.dates.forEach((date, i) => {
      const mm  = foreData.rainfall[i];
      const lvl = rainLevel(mm);
      const px  = Math.max(4, Math.round((mm / Math.max(peak, 1)) * 70));
      const col = barColors[lvl.cls];

      tbody.innerHTML += `
        <tr>
          <td class="td-date">${date}</td>
          <td class="td-mm">${mm.toFixed(2)} mm</td>
          <td><span class="level-badge ${lvl.cls}">${lvl.icon} ${lvl.label}</span></td>
          <td>
            <span class="bar-track">
              <span class="bar-fill" style="width:${px}px; background:${col};"></span>
            </span>
          </td>
        </tr>`;
    });

  } catch (err) {
    console.error("Error loading data:", err);
  }
}

// ── Auto-refresh every 10 seconds ─────────────────────────────
setInterval(loadData, 10000);
window.onload = loadData;