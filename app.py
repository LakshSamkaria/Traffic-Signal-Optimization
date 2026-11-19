from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def optimize_signals(traffic, min_green=10, max_green=60):
    """Greedy scheduling: serve the highest-density road first.
    Green time is proportional to vehicle count, bounded by min/max.
    """
    roads = list(traffic.keys())
    total = sum(max(0, int(traffic[r])) for r in roads)
    if total == 0:
        return []

    # Greedy priority: highest vehicle count first; stable road-name tie-break.
    ordered = sorted(roads, key=lambda r: (-int(traffic[r]), r))
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

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/optimize", methods=["POST"])
def optimize():
    data = request.get_json(silent=True) or {}
    raw = data.get("traffic", {})
    try:
        traffic = {str(k): max(0, int(v)) for k, v in raw.items()}
        min_green = max(5, min(30, int(data.get("min_green", 10))))
        max_green = max(min_green, min(90, int(data.get("max_green", 60))))
        if len(traffic) < 2 or len(traffic) > 8:
            return jsonify({"error": "Please provide between 2 and 8 roads."}), 400
        result = optimize_signals(traffic, min_green, max_green)
        return jsonify({"results": result, "total_vehicles": sum(traffic.values())})
    except (TypeError, ValueError):
        return jsonify({"error": "Please enter valid whole numbers."}), 400

if __name__ == "__main__":
    app.run(debug=True)
