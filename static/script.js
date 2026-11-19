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
