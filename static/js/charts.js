/* Stat counter animation */
function animateCounter(el) {
  const target = parseFloat(el.dataset.target);
  const suffix = el.dataset.suffix || '';
  const isDecimal = target % 1 !== 0;
  const duration = 1800;
  const start = performance.now();

  function tick(now) {
    const elapsed = now - start;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const current = target * eased;
    el.textContent = (isDecimal
      ? current.toFixed(1)
      : Math.floor(current).toLocaleString()) + suffix;
    if (progress < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

window.addEventListener('load', () => {
  document.querySelectorAll('.stat-number').forEach(animateCounter);
});

/* Sticky nav via IntersectionObserver */
const nav = document.getElementById('sticky-nav');
const hero = document.getElementById('hero');
if (nav && hero) {
  new IntersectionObserver(
    ([entry]) => nav.classList.toggle('visible', !entry.isIntersecting),
    { threshold: 0 }
  ).observe(hero);
}

/* Scroll fade-in for .fade-in-up elements */
const fadeObs = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      fadeObs.unobserve(entry.target);
    }
  });
}, { threshold: 0.1 });
document.querySelectorAll('.fade-in-up').forEach(el => fadeObs.observe(el));

/* Chart.js global defaults */
Chart.defaults.font.family = "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif";
Chart.defaults.plugins.legend.labels.boxWidth = 14;
Chart.defaults.plugins.legend.labels.padding = 16;

/* Overview doughnut charts */
(function () {
  const species = window.speciesData || [];
  const stats = window.statsData || {};

  new Chart(document.getElementById('speciesCompositionChart'), {
    type: 'doughnut',
    data: {
      labels: species.map(s => s.name),
      datasets: [{
        data: species.map(s => s.composition_pct),
        backgroundColor: species.map(s => s.color),
        borderWidth: 2,
        borderColor: '#f5f7f2',
      }],
    },
    options: {
      plugins: {
        tooltip: {
          callbacks: { label: ctx => ` ${ctx.label}: ${ctx.parsed.toFixed(1)}%` },
        },
      },
    },
  });

  new Chart(document.getElementById('overallCoverageChart'), {
    type: 'doughnut',
    data: {
      labels: ['With Invasives', 'No Invasives'],
      datasets: [{
        data: [stats.invasive_pct, stats.non_invasive_pct],
        backgroundColor: ['#c0392b', '#a8d5a2'],
        borderWidth: 2,
        borderColor: '#f5f7f2',
      }],
    },
    options: {
      plugins: {
        tooltip: {
          callbacks: { label: ctx => ` ${ctx.label}: ${ctx.parsed.toFixed(1)}%` },
        },
      },
    },
  });
})();

/* Per-species density bar charts */
(function () {
  (window.cardSpeciesData || []).forEach(s => {
    const canvas = document.getElementById(`densityBar_${s.code}`);
    if (!canvas) return;
    new Chart(canvas, {
      type: 'bar',
      data: {
        labels: ['Low', 'Moderate', 'High'],
        datasets: [{
          data: [s.low, s.moderate, s.high],
          backgroundColor: ['#90ee90', '#ffd700', s.color],
          borderWidth: 1,
          borderColor: 'rgba(0,0,0,0.08)',
        }],
      },
      options: {
        indexAxis: 'y',
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: 'rgba(0,0,0,0.05)' }, ticks: { font: { size: 11 } } },
          y: { ticks: { font: { size: 11 } } },
        },
      },
    });
  });
})();

/* Threat Index horizontal bar */
(function () {
  const sorted = [...(window.speciesData || [])].sort((a, b) => b.threat_score - a.threat_score);
  new Chart(document.getElementById('threatIndexChart'), {
    type: 'bar',
    data: {
      labels: sorted.map(s => s.name),
      datasets: [{
        label: 'Threat Index (0–100)',
        data: sorted.map(s => s.threat_score),
        backgroundColor: sorted.map(s => s.color),
        borderWidth: 1,
        borderColor: 'rgba(0,0,0,0.1)',
      }],
    },
    options: {
      indexAxis: 'y',
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: ctx => ` Score: ${ctx.parsed.x.toFixed(1)}` } },
      },
      scales: {
        x: { max: 25, grid: { color: 'rgba(0,0,0,0.05)' }, ticks: { font: { size: 11 } } },
        y: { ticks: { font: { size: 12 } } },
      },
    },
  });
})();

/* Management Effort horizontal bar */
(function () {
  const sorted = [...(window.speciesData || [])].sort((a, b) => b.effort_pct - a.effort_pct);
  new Chart(document.getElementById('effortChart'), {
    type: 'bar',
    data: {
      labels: sorted.map(s => `${s.name} (${s.effort_tier})`),
      datasets: [{
        label: 'Relative Effort (%)',
        data: sorted.map(s => s.effort_pct),
        backgroundColor: sorted.map(s => s.color),
        borderWidth: 1,
        borderColor: 'rgba(0,0,0,0.1)',
      }],
    },
    options: {
      indexAxis: 'y',
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: ctx => ` Effort: ${ctx.parsed.x.toFixed(1)}%` } },
      },
      scales: {
        x: { max: 100, grid: { color: 'rgba(0,0,0,0.05)' }, ticks: { font: { size: 11 } } },
        y: { ticks: { font: { size: 11 } } },
      },
    },
  });
})();
