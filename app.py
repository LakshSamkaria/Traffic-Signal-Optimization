import json
import os
from collections import deque
from datetime import datetime

from flask import Flask, jsonify, render_template, request

from database import Database

app = Flask(__name__)
db = Database()


# 1. GRAPH CLASS - Adjacency List Representation
class TrafficGraph:
    def __init__(self):
        self.graph = {}

    def add_edge(self, road1, road2):
        self.graph.setdefault(road1, []).append(road2)
        self.graph.setdefault(road2, []).append(road1)

    # 2. BFS GRAPH TRAVERSAL
    def bfs(self, start):
        visited = {start}
        queue = deque([start])
        connected_roads = []

        while queue:
            node = queue.popleft()
            connected_roads.append(node)
            for neighbour in self.graph.get(node, []):
                if neighbour not in visited:
                    visited.add(neighbour)
                    queue.append(neighbour)
        return connected_roads


# 3. EXISTING GREEDY ALGORITHM (preserved)
def optimize_signals(traffic, min_green=10, max_green=60):
    if not traffic:
        return []

    graph = TrafficGraph()
    intersection = "Central Junction"
    for road in traffic:
        graph.add_edge(intersection, road)

    connected_roads = graph.bfs(intersection)
    roads = [road for road in connected_roads if road != intersection]
    total = sum(max(0, int(traffic[road])) for road in roads)
    if total == 0:
        return []

    ordered = sorted(roads, key=lambda road: (-int(traffic[road]), road))
    results = []
    for rank, road in enumerate(ordered, start=1):
        count = max(0, int(traffic[road]))
        proportional = round((count / total) * (max_green * len(roads)))
        green = max(min_green, min(max_green, proportional))
        results.append({
            "road": road,
            "vehicles": count,
            "priority": rank,
            "green_time": green
        })
    return results


# 4. FIXED-TIME BASELINE: equal green duration for every road
def fixed_time_signals(traffic, green_time=30):
    return [
        {"road": road, "vehicles": int(count), "priority": index,
         "green_time": green_time}
        for index, (road, count) in enumerate(traffic.items(), start=1)
    ]


def estimate_average_wait(results):
    """Simple simulation estimate: expected wait is half the red portion of a cycle."""
    if not results:
        return 0.0
    cycle = sum(item["green_time"] for item in results)
    total_vehicles = sum(item["vehicles"] for item in results)
    if not total_vehicles or not cycle:
        return 0.0
    weighted_wait = sum(
        item["vehicles"] * max(0, cycle - item["green_time"]) / 2
        for item in results
    )
    return round(weighted_wait / total_vehicles, 2)


def build_comparison(traffic, greedy_results):
    fixed_results = fixed_time_signals(traffic)
    greedy_wait = estimate_average_wait(greedy_results)
    fixed_wait = estimate_average_wait(fixed_results)
    improvement = (
        round(((fixed_wait - greedy_wait) / fixed_wait) * 100, 2)
        if fixed_wait else 0.0
    )
    return {
        "greedy": {"average_wait": greedy_wait, "total_green": sum(x["green_time"] for x in greedy_results),
                   "schedule": greedy_results},
        "fixed_time": {"average_wait": fixed_wait, "total_green": sum(x["green_time"] for x in fixed_results),
                       "schedule": fixed_results},
        "waiting_time_reduction_percent": improvement,
        "metric_note": "Estimated waiting time from the simulated signal cycle; not measured road telemetry."
    }


def clean_traffic(raw):
    if not isinstance(raw, dict):
        raise ValueError("Traffic data must be an object.")
    traffic = {}
    for key, value in raw.items():
        count = int(value)
        if count < 0 or count > 999:
            raise ValueError("Vehicle counts must be between 0 and 999.")
        traffic[str(key)] = count
    if len(traffic) < 2 or len(traffic) > 8:
        raise ValueError("Please provide between 2 and 8 roads.")
    if not any(traffic.values()):
        raise ValueError("At least one road must have a vehicle waiting.")
    return traffic


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/optimize", methods=["POST"])
def optimize():
    data = request.get_json(silent=True) or {}
    try:
        traffic = clean_traffic(data.get("traffic", {}))
        min_green = max(5, min(30, int(data.get("min_green", 10))))
        max_green = max(min_green, min(90, int(data.get("max_green", 60))))
        result = optimize_signals(traffic, min_green, max_green)
        comparison = build_comparison(traffic, result)
        record_id = db.save_optimization(
            traffic=traffic,
            results=result,
            comparison=comparison,
            total_vehicles=sum(traffic.values())
        )
        return jsonify({
            "results": result,
            "total_vehicles": sum(traffic.values()),
            "comparison": comparison,
            "record_id": record_id,
            "storage": "mysql" if db.enabled else "unavailable"
        })
    except (TypeError, ValueError, AttributeError) as exc:
        return jsonify({"error": str(exc) or "Please enter valid whole numbers."}), 400


@app.route("/api/history")
def optimization_history():
    try:
        return jsonify({"history": db.get_history(), "storage": "mysql" if db.enabled else "unavailable"})
    except Exception:
        app.logger.exception("Could not load optimization history")
        return jsonify({"error": "Could not load history. Check MySQL configuration."}), 503


@app.route("/api/compare", methods=["POST"])
def compare_algorithms():
    data = request.get_json(silent=True) or {}
    try:
        traffic = clean_traffic(data.get("traffic", {}))
        min_green = max(5, min(30, int(data.get("min_green", 10))))
        max_green = max(min_green, min(90, int(data.get("max_green", 60))))
        greedy = optimize_signals(traffic, min_green, max_green)
        return jsonify(build_comparison(traffic, greedy))
    except (TypeError, ValueError, AttributeError) as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/api/analytics")
def analytics():
    try:
        return jsonify(db.get_analytics())
    except Exception:
        app.logger.exception("Could not load traffic analytics")
        return jsonify({"error": "Could not load analytics. Check MySQL configuration."}), 503


@app.route("/api/database-status")
def database_status():
    return jsonify({"connected": db.enabled, "database": db.database_name})


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "true").lower() == "true")
