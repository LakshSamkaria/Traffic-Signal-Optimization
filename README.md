# TRAFFICFLOW – TRAFFIC SIGNAL OPTIMIZATION

## Project Overview
TrafficFlow is a web-based traffic signal optimization system that uses a Greedy Algorithm to prioritize roads based on vehicle density and calculate optimized green signal timings.

## Project Contents
- `app.py` – Flask backend and Greedy Algorithm
- `templates/index.html` – Website layout
- `static/style.css` – Styling and responsive design
- `static/script.js` – Frontend interaction
- `requirements.txt` – Project dependencies

## Technologies Used
- Python
- Flask
- HTML
- CSS
- JavaScript
- Greedy Algorithm
- Graph Theory (conceptual representation)

## How to Run (Windows)

1. Install Python 3.10 or newer.
2. Open Command Prompt in the project folder.
3. Install dependencies:

   `py -m pip install -r requirements.txt`

4. Run the application:

   `py app.py`

5. Open your browser and visit:

   `http://127.0.0.1:5000`

## How to Use

1. Enter vehicle counts for North, East, South and West roads.
2. Select minimum and maximum green signal duration.
3. Click **Run Optimization**.
4. View the road priority order and optimized green signal timings.

## Algorithm Explanation

**Graph Theory:** The road network is conceptually represented as a graph, where the intersection is a node and connected roads are edges.

**Greedy Algorithm:** The system sorts roads in descending order of vehicle count and gives the highest-traffic road the highest priority. Green signal time is calculated proportionally within the selected minimum and maximum limits.

## Project Objective
To demonstrate how Data Structures and Algorithms can be applied to traffic signal optimization and help understand traffic management concepts.

## Note
This project is an academic simulation only. It does not control real-world traffic signals.
