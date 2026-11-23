import json
import os

import mysql.connector
from dotenv import load_dotenv
from mysql.connector import Error

# Load .env even when this module is imported independently.
load_dotenv()


class Database:
    """MySQL persistence for TrafficFlow optimization history and analytics."""

    def __init__(self):
        self.database_name = os.getenv("MYSQL_DATABASE", "trafficflow_db")
        self.config = {
            "host": os.getenv("MYSQL_HOST", "localhost"),
            "port": int(os.getenv("MYSQL_PORT", "3306")),
            "user": os.getenv("MYSQL_USER", "root"),
            "password": os.getenv("MYSQL_PASSWORD", ""),
            "connection_timeout": 5,
        }
        self.enabled = False

        try:
            self.initialize()
            print(
                f"[MySQL] Connected successfully to database: "
                f"{self.database_name}"
            )
        except Error as exc:
            self.enabled = False
            print(f"[MySQL] Connection unavailable: {exc}")
            print(
                "[MySQL] Check MYSQL_HOST, MYSQL_PORT, MYSQL_USER, "
                "MYSQL_PASSWORD and MYSQL_DATABASE in your .env file."
            )

    def connect(self, include_database=True):
        config = dict(self.config)
        if include_database:
            config["database"] = self.database_name
        return mysql.connector.connect(**config)

    def initialize(self):
        """Create the configured database and its history table if needed."""
        connection = self.connect(include_database=False)
        try:
            cursor = connection.cursor()
            try:
                # database_name comes from local configuration, not user input.
                cursor.execute(
                    f"CREATE DATABASE IF NOT EXISTS `{self.database_name}` "
                    "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                )
            finally:
                cursor.close()
        finally:
            connection.close()

        connection = self.connect()
        try:
            cursor = connection.cursor()
            try:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS optimization_history (
                        id BIGINT AUTO_INCREMENT PRIMARY KEY,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        total_vehicles INT NOT NULL,
                        traffic_json JSON NOT NULL,
                        greedy_results_json JSON NOT NULL,
                        comparison_json JSON NOT NULL,
                        average_wait_seconds DECIMAL(10,2) NOT NULL
                    )
                """)
                connection.commit()
            finally:
                cursor.close()
        finally:
            connection.close()

        self.enabled = True

    def save_optimization(self, traffic, results, comparison, total_vehicles):
        """Save one optimization run and return its database record ID."""
        if not self.enabled:
            return None

        connection = self.connect()
        try:
            cursor = connection.cursor()
            try:
                cursor.execute("""
                    INSERT INTO optimization_history (
                        total_vehicles,
                        traffic_json,
                        greedy_results_json,
                        comparison_json,
                        average_wait_seconds
                    )
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    total_vehicles,
                    json.dumps(traffic),
                    json.dumps(results),
                    json.dumps(comparison),
                    comparison["greedy"]["average_wait"],
                ))
                record_id = cursor.lastrowid
                connection.commit()
                print(f"[MySQL] Optimization saved. Record ID: {record_id}")
                return record_id
            except (Error, KeyError, TypeError, ValueError) as exc:
                connection.rollback()
                print(f"[MySQL] Could not save optimization: {exc}")
                return None
            finally:
                cursor.close()
        finally:
            connection.close()

    def get_history(self, limit=50):
        """Return the latest saved optimization runs."""
        if not self.enabled:
            return []

        connection = self.connect()
        try:
            cursor = connection.cursor(dictionary=True)
            try:
                cursor.execute("""
                    SELECT
                        id,
                        created_at,
                        total_vehicles,
                        traffic_json,
                        greedy_results_json,
                        comparison_json,
                        average_wait_seconds
                    FROM optimization_history
                    ORDER BY created_at DESC
                    LIMIT %s
                """, (limit,))
                rows = cursor.fetchall()
            finally:
                cursor.close()
        finally:
            connection.close()

        for row in rows:
            row["created_at"] = row["created_at"].isoformat(
                sep=" ", timespec="seconds"
            )
            for field in (
                "traffic_json",
                "greedy_results_json",
                "comparison_json",
            ):
                if isinstance(row[field], str):
                    row[field] = json.loads(row[field])
            row["average_wait_seconds"] = float(row["average_wait_seconds"])

        return rows

    def get_analytics(self):
        """Return aggregate statistics and the 12 most recent runs."""
        if not self.enabled:
            return {
                "available": False,
                "total_runs": 0,
                "total_vehicles": 0,
                "average_wait": 0,
                "recent": [],
            }

        connection = self.connect()
        try:
            cursor = connection.cursor(dictionary=True)
            try:
                cursor.execute("""
                    SELECT
                        COUNT(*) AS total_runs,
                        COALESCE(SUM(total_vehicles), 0) AS total_vehicles,
                        COALESCE(AVG(average_wait_seconds), 0) AS average_wait
                    FROM optimization_history
                """)
                summary = cursor.fetchone()

                cursor.execute("""
                    SELECT
                        id,
                        created_at,
                        total_vehicles,
                        average_wait_seconds
                    FROM optimization_history
                    ORDER BY created_at DESC
                    LIMIT 12
                """)
                recent = cursor.fetchall()
            finally:
                cursor.close()
        finally:
            connection.close()

        for row in recent:
            row["created_at"] = row["created_at"].isoformat(
                sep=" ", timespec="seconds"
            )
            row["average_wait_seconds"] = float(row["average_wait_seconds"])

        return {
            "available": True,
            "total_runs": int(summary["total_runs"]),
            "total_vehicles": int(summary["total_vehicles"]),
            "average_wait": round(float(summary["average_wait"]), 2),
            "recent": list(reversed(recent)),
        }
