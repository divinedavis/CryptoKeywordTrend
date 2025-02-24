from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
DB_FILE = "trend_data.db"

def query_trend_data(crypto=None):
    """
    Query the trend_data table from the SQLite database.
    If a crypto is provided, filter the results.
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Allows us to access columns by name
    cur = conn.cursor()
    if crypto:
        cur.execute("SELECT * FROM trend_data WHERE crypto = ? ORDER BY created DESC", (crypto,))
    else:
        cur.execute("SELECT * FROM trend_data ORDER BY created DESC")
    rows = cur.fetchall()
    conn.close()
    # Convert rows to a list of dictionaries
    return [dict(row) for row in rows]

@app.route("/trends", methods=["GET"])
def get_trends():
    """
    API endpoint to return aggregated trend data in JSON format.
    You can filter by a specific cryptocurrency using the 'crypto' query parameter.
    For example: http://127.0.0.1:5000/trends?crypto=bitcoin
    """
    crypto_filter = request.args.get("crypto")
    data = query_trend_data(crypto_filter)
    return jsonify(data)

if __name__ == "__main__":
    # Run the Flask development server on port 5000
    app.run(debug=True, port=5000)
