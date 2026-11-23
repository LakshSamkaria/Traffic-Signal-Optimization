const roadIds = ["north", "east", "south", "west"];
const roadNames = {north:"North Road", east:"East Road", south:"South Road", west:"West Road"};
const sample = {north:25, east:40, south:15, west:30};
let latestResults = [];

function setSignal(activeRoad) {
  roadIds.forEach(road => {
    const lights = document.querySelectorAll(`#signal${road[0].toUpperCase()+road.slice(1)} i`);
    lights.forEach((light, index) => {
      light.className = "";
      if (road === activeRoad && index === 2) light.classList.add("green-on");
      else if (index === 0) light.classList.add("red-on");
    });
  });
}
function renderResults(results, total) {
  const body = document.getElementById("resultsBody");
  body.innerHTML = "";
  results.forEach(item => {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td><span class="priority">${item.priority}</span></td>
      <td class="road-cell">${item.road}</td><td>${item.vehicles}</td>
      <td class="duration">${item.green_time} sec</td>
      <td><span class="status">${item.priority === 1 ? "FIRST PRIORITY" : "QUEUED"}</span></td>`;
    body.appendChild(tr);
  });
  document.getElementById("totalStat").textContent = total.toLocaleString();
  document.getElementById("resultTag").textContent = "OPTIMIZATION COMPLETE";
  if (results.length) {
    document.getElementById("currentRoad").textContent = results[0].road;
    document.getElementById("currentTime").textContent = results[0].green_time;
    const key = roadIds.find(k => roadNames[k] === results[0].road);
    setSignal(key);
  }
}
async function runOptimization() {
  const error = document.getElementById("error");
  error.textContent = "";
  const traffic = {};
  for (const id of roadIds) {
    const value = Number(document.getElementById(id).value);
    if (!Number.isInteger(value) || value < 0 || value > 999) {
      error.textContent = "Enter a whole number between 0 and 999 for every road.";
      return;
    }
    traffic[roadNames[id]] = value;
  }
  if (Object.values(traffic).every(v => v === 0)) {
    error.textContent = "At least one road must have a vehicle waiting.";
    return;
  }
  const button = document.getElementById("runBtn");
  button.disabled = true;
  button.querySelector("span").textContent = "Optimizing...";
  try {
    const response = await fetch("/optimize", {
      method:"POST", headers:{"Content-Type":"application/json"},
      body:JSON.stringify({traffic, min_green:Number(document.getElementById("minGreen").value), max_green:Number(document.getElementById("maxGreen").value)})
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Unable to optimize traffic.");
    latestResults = data.results;
    renderResults(data.results, data.total_vehicles);
  } catch (err) {
    error.textContent = err.message + " Make sure the Flask server is running.";
  } finally {
    button.disabled = false;
    button.querySelector("span").textContent = "Run optimization";
  }
}
document.getElementById("runBtn").addEventListener("click", runOptimization);
document.getElementById("resetBtn").addEventListener("click", () => {
  roadIds.forEach(id => document.getElementById(id).value = sample[id]);
  document.getElementById("totalStat").textContent = "—";
  document.getElementById("currentRoad").textContent = "Run optimization";
  document.getElementById("currentTime").textContent = "--";
  document.getElementById("resultTag").textContent = "AWAITING INPUT";
  document.getElementById("resultsBody").innerHTML = '<tr><td colspan="5" class="empty">Enter traffic data and run optimization to see results.</td></tr>';
  document.getElementById("error").textContent = "";
  roadIds.forEach(id => setSignal(null));
});
roadIds.forEach(id => document.getElementById(id).addEventListener("input", () => {
  const total = roadIds.reduce((sum, key) => sum + Math.max(0, Number(document.getElementById(key).value) || 0), 0);
  document.getElementById("totalStat").textContent = total.toLocaleString();
}));

let comparisonChartInstance = null;
let analyticsChartInstance = null;

function renderComparison(data) {
  document.getElementById("greedyWait").textContent = data.greedy.average_wait + " s";
  document.getElementById("fixedWait").textContent = data.fixed_time.average_wait + " s";
  document.getElementById("waitReduction").textContent = data.waiting_time_reduction_percent + "%";
  document.getElementById("metricNote").textContent = data.metric_note;
  const ctx = document.getElementById("comparisonChart");
  if (!ctx || !window.Chart) return;
  if (comparisonChartInstance) comparisonChartInstance.destroy();
  comparisonChartInstance = new Chart(ctx, {
    type: "bar",
    data: {labels: ["Greedy", "Fixed-Time"], datasets: [{
      label: "Estimated average waiting time (seconds)",
      data: [data.greedy.average_wait, data.fixed_time.average_wait],
      backgroundColor: ["#20a875", "#8b9aa3"], borderRadius: 7
    }]},
    options: {responsive: true, plugins: {legend: {display: false}},
      scales: {y: {beginAtZero: true, title: {display: true, text: "Seconds"}}}}
  });
}

async function refreshHistory() {
  const body = document.getElementById("historyBody");
  const status = document.getElementById("historyStatus");
  try {
    const response = await fetch("/api/history");
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "History unavailable");
    body.replaceChildren();
    if (!data.history.length) {
      const row = body.insertRow();
      const cell = row.insertCell();
      cell.colSpan = 3; cell.className = "empty"; cell.textContent = "No saved runs yet.";
    }
    data.history.forEach(item => {
      const row = body.insertRow();
      [item.created_at, item.total_vehicles, item.average_wait_seconds + " s"].forEach(value => {
        const cell = row.insertCell(); cell.textContent = value;
      });
    });
    status.textContent = data.storage === "mysql"
      ? "Connected to MySQL · showing latest 50 runs"
      : "MySQL is not configured. Runs are not being saved.";
  } catch (error) { status.textContent = error.message; }
}

async function refreshAnalytics() {
  const status = document.getElementById("analyticsStatus");
  try {
    const response = await fetch("/api/analytics");
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Analytics unavailable");
    document.getElementById("analyticsRuns").textContent = data.total_runs;
    document.getElementById("analyticsVehicles").textContent = Number(data.total_vehicles).toLocaleString();
    document.getElementById("analyticsWait").textContent = data.average_wait + " s";
    if (!data.available) {
      status.textContent = "Connect MySQL to store and display analytics.";
      return;
    }
    status.textContent = "Based on the latest 12 saved optimization runs. Waiting time is a simulation estimate.";
    const ctx = document.getElementById("analyticsChart");
    if (!ctx || !window.Chart) return;
    if (analyticsChartInstance) analyticsChartInstance.destroy();
    analyticsChartInstance = new Chart(ctx, {
      type: "line",
      data: {labels: data.recent.map(item => "#" + item.id), datasets: [
        {label: "Vehicles", data: data.recent.map(item => item.total_vehicles),
          borderColor: "#20a875", backgroundColor: "rgba(32,168,117,.12)", yAxisID: "y", tension: .3},
        {label: "Estimated wait (sec)", data: data.recent.map(item => item.average_wait_seconds),
          borderColor: "#7186ad", backgroundColor: "rgba(113,134,173,.1)", yAxisID: "y1", tension: .3}
      ]},
      options: {responsive: true, interaction: {mode: "index", intersect: false},
        scales: {y: {type: "linear", position: "left", beginAtZero: true},
          y1: {type: "linear", position: "right", beginAtZero: true, grid: {drawOnChartArea: false}}}}
    });
  } catch (error) { status.textContent = error.message; }
}

const previousRenderResults = renderResults;
renderResults = function(results, total) {
  previousRenderResults(results, total);
  refreshHistory();
  refreshAnalytics();
  fetch("/api/compare", {
    method: "POST", headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      traffic: Object.fromEntries(roadIds.map(id => [roadNames[id], Number(document.getElementById(id).value)])),
      min_green: Number(document.getElementById("minGreen").value),
      max_green: Number(document.getElementById("maxGreen").value)
    })
  }).then(response => response.json()).then(data => {
    if (data.greedy) renderComparison(data);
  }).catch(() => {});
};
document.getElementById("refreshHistory")?.addEventListener("click", refreshHistory);
refreshHistory();
refreshAnalytics();
