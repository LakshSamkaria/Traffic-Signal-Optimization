
from flask import Flask, render_template, request, jsonify
from collections import deque

app = Flask(__name__)


# 1. GRAPH CLASS - Adjacency List Representation
class TrafficGraph:
    def __init__(self):
        self.graph = {}

    def add_edge(self, road1, road2):
        self.graph.setdefault(road1, []).append(road2)
        self.graph.setdefault(road2, []).append(road1)

    # 2. BFS GRAPH TRAVERSAL
    def bfs(self, start):
        visited = set()
        queue = deque([start])
        visited.add(start)

        connected_roads = []

        while queue:
            node = queue.popleft()
            connected_roads.append(node)

            for neighbour in self.graph.get(node, []):
                if neighbour not in visited:
                    visited.add(neighbour)
                    queue.append(neighbour)

        return connected_roads


# 3. GREEDY ALGORITHM
def optimize_signals(traffic, min_green=10, max_green=60):

    if not traffic:
        return []

    # Create graph for the intersection
    graph = TrafficGraph()

    intersection = "Central Junction"

    for road in traffic:
        graph.add_edge(intersection, road)

    # Get connected roads using BFS
    connected_roads = graph.bfs(intersection)

    # Remove central junction from road list
    roads = [road for road in connected_roads if road != intersection]

    total = sum(max(0, int(traffic[road])) for road in roads)

    if total == 0:
        return []

    # Greedy: Highest traffic road gets first priority
    ordered = sorted(
        roads,
        key=lambda road: (-int(traffic[road]), road)
    )

    results = []

    for rank, road in enumerate(ordered, start=1):
        count = max(0, int(traffic[road]))

        proportional = round(
            (count / total) * (max_green * len(roads))
        )

        green = max(
            min_green,
            min(max_green, proportional)
        )

        results.append({
            "road": road,
            "vehicles": count,
            "priority": rank,
            "green_time": green
        })

    return results


# 4. HOME PAGE
@app.route("/")
def home():
    return render_template("index.html")


# 5. OPTIMIZATION API
@app.route("/optimize", methods=["POST"])
def optimize():

    data = request.get_json(silent=True) or {}
    raw = data.get("traffic", {})

    try:
        traffic = {
            str(k): max(0, int(v))
            for k, v in raw.items()
        }

        min_green = max(5, min(30, int(data.get("min_green", 10))))
        max_green = max(min_green, min(90, int(data.get("max_green", 60))))

        if len(traffic) < 2 or len(traffic) > 8:
            return jsonify({
                "error": "Please provide between 2 and 8 roads."
            }), 400

        result = optimize_signals(
            traffic,
            min_green,
            max_green
        )

        return jsonify({
            "results": result,
            "total_vehicles": sum(traffic.values())
        })

    except (TypeError, ValueError, AttributeError):
        return jsonify({
            "error": "Please enter valid whole numbers."
        }), 400


if __name__ == "__main__":
    app.run(debug=True)
