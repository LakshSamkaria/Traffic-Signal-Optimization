# TrafficFlow – Traffic Signal Optimization

TrafficFlow is a web-based traffic signal optimization project that demonstrates how Data Structures and Algorithms can be applied to a simulated road intersection. It uses a Greedy Algorithm to rank roads by vehicle density and calculate green-signal durations. The project also includes BFS-based graph traversal, MySQL-backed optimization history, an algorithm comparison, and traffic analytics.

> **Academic simulation:** TrafficFlow works with manually entered vehicle counts. It does not connect to cameras, sensors, live traffic feeds, or real traffic-light hardware.

## Features

- **Greedy-based signal optimization:** Prioritizes roads in descending order of vehicle count.
- **Configurable signal limits:** Accepts minimum and maximum green-signal durations.
- **Graph representation and BFS:** Represents the junction using an adjacency list and traverses connected roads with Breadth-First Search.
- **Optimization history:** Stores optimization runs in MySQL, including traffic input, results, and comparison data.
- **Greedy vs Fixed-Time comparison:** Compares the Greedy schedule with an equal-duration fixed-time baseline.
- **Traffic analytics:** Summarizes saved runs, total vehicles, average estimated waiting time, and recent activity.
- **Database status endpoint:** Reports whether MySQL storage is available.

## Tech Stack

| Area | Technology |
|---|---|
| Backend | Python, Flask |
| Frontend | HTML, CSS, JavaScript |
| Database | MySQL |
| Database connector | mysql-connector-python |
| Environment configuration | python-dotenv |
| Algorithms | Greedy Algorithm, BFS |
| Data structure | Graph using an adjacency list |

## Project Structure

```text
Traffic-Signal-Optimization/
├── app.py                  # Flask application, graph/BFS and optimization logic
├── database.py             # MySQL connection, schema and data operations
├── templates/
│   └── index.html          # Dashboard page
├── static/
│   ├── style.css           # Dashboard styling
│   └── script.js           # Frontend interactions and API requests
├── requirements.txt        # Python dependencies
├── .env.example            # Example environment configuration
└── README.md               # Project documentation
```

## Requirements

- Python 3.10 or newer
- MySQL Server
- A web browser

## Installation and Setup (Windows)

### 1. Clone the repository

```bash
git clone https://github.com/LakshSamkaria/Traffic-Signal-Optimization.git
cd Traffic-Signal-Optimization
```

### 2. Create and activate a virtual environment (recommended)

```bash
py -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
py -m pip install -r requirements.txt
```

### 4. Configure MySQL

Make sure MySQL Server is installed and running. Copy the example environment file:

```bash
copy .env.example .env
```

Open `.env` and enter the credentials for your local MySQL account:

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=trafficflow
FLASK_DEBUG=true
```

Use your own MySQL username and password. Do not commit your actual `.env` file or database password to GitHub.

On startup, the application attempts to create the configured database and the `optimization_history` table. The MySQL account must have permission to create the database and table.

### 5. Run the application

```bash
py app.py
```

### 6. Open the dashboard

Visit:

```text
http://127.0.0.1:5000
```

## How to Use

1. Open the TrafficFlow dashboard.
2. Enter the vehicle counts for the available roads.
3. Set the minimum and maximum green-signal durations.
4. Select **Run Optimization**.
5. Review the road priority order and calculated green-signal timings.
6. Use the comparison, history, and analytics sections to review saved optimization results.

The application validates vehicle counts before processing. The current backend accepts between 2 and 8 roads, with each vehicle count between 0 and 999, and requires at least one vehicle across the roads.

## Algorithm Overview

### 1. Graph and BFS

The road connections are represented using an adjacency-list graph. The application connects each road to a central junction and uses Breadth-First Search (BFS) to traverse the connected roads.

### 2. Greedy Algorithm

The Greedy approach:

1. Reads the vehicle count for each road.
2. Sorts roads from highest to lowest vehicle count.
3. Assigns priority based on that order.
4. Calculates a proportional green-signal duration using the configured maximum duration and number of roads.
5. Keeps the calculated duration within the configured minimum and maximum limits.

This is a simplified scheduling model for demonstrating algorithmic prioritization.

### 3. Fixed-Time Comparison

The comparison baseline assigns the same 30-second green duration to each road. TrafficFlow compares the estimated average waiting time of this baseline with the Greedy schedule.

**Important:** Waiting-time values are educational estimates calculated from the simulated signal cycle. They are not measurements of actual traffic conditions or validated predictions.

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Loads the dashboard |
| POST | `/optimize` | Runs Greedy optimization and attempts to save the result |
| GET | `/api/history` | Returns recent optimization history |
| POST | `/api/compare` | Compares Greedy and fixed-time schedules |
| GET | `/api/analytics` | Returns database-backed traffic analytics |
| GET | `/api/database-status` | Returns MySQL availability status |

## Database

The application uses a MySQL database configured through the `.env` file. By default, the database name is `trafficflow`.

The `optimization_history` table stores:
- Run timestamp
- Total vehicle count
- Input traffic data
- Greedy optimization results
- Comparison results
- Estimated average waiting time

If MySQL is unavailable or its credentials are incorrect, database-backed history and analytics will not be available. Configure and start MySQL to use persistent storage.

## Future Improvements

- Connect simulated inputs to traffic sensors or camera-based vehicle detection.
- Explore adaptive signal timing using real traffic data.
- Add more junctions and configurable road networks.
- Evaluate scheduling approaches with realistic traffic simulations.

## Author

**Laksh Samkaria**

GitHub: [@LakshSamkaria](https://github.com/LakshSamkaria)

## License

No license has currently been specified for this repository.
