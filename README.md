TRAFFICFLOW - TRAFFIC SIGNAL OPTIMIZATION

PROJECT CONTENTS
- app.py: Flask backend and Greedy Algorithm
- templates/index.html: Website layout
- static/style.css: Styling and responsive design
- static/script.js: Frontend interaction

HOW TO RUN (Windows)
1. Install Python 3.10 or newer.
2. Open Command Prompt in this project folder.
3. Run: py -m pip install -r requirements.txt
4. Run: py app.py
5. Open this address in your browser: http://127.0.0.1:5000

HOW TO USE
1. Enter the number of vehicles on North, East, South and West roads.
2. Choose minimum and maximum green signal duration.
3. Click Run optimization.
4. Review the priority order and green time table.

ALGORITHM NOTE
The road network is represented conceptually as a graph: one intersection is a node and each connected road is an edge. The greedy strategy sorts roads by descending vehicle count and gives the highest-traffic road first priority. Green time is calculated proportionally and bounded by the selected minimum and maximum values.

This is an academic simulation only. It does not control real traffic lights.
