import json
import threading
import psycopg2
from kafka import KafkaConsumer
from flask import Flask, request, jsonify

# Database configuration
DB_CONFIG = {
    "dbname": "ai-applications",
    "user": "postgres",
    "password": "password",
    "host": "localhost",
    "port": "5432",
}

# Kafka configuration
KAFKA_TOPIC = "ocr-messages"
KAFKA_BROKER = "localhost:9092"

# Initialize Flask app
app = Flask(__name__)

# Function to create a table if it does not exist
def create_table():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

# Function to insert data into PostgreSQL
def insert_into_db(email, message):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("INSERT INTO messages (email, message) VALUES (%s, %s)", (email, message))
    conn.commit()
    cur.close()
    conn.close()

# Kafka consumer function
def kafka_consumer():
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="earliest",
    )

    for message in consumer:
        data = message.value
        email = data.get("email")
        msg = data.get("message")
        if email and msg:
            insert_into_db(email, msg)

# Start Kafka consumer in a separate thread
consumer_thread = threading.Thread(target=kafka_consumer, daemon=True)
consumer_thread.start()


@app.route("/messages", methods=["GET"])
def get_messages():
    email = request.args.get("email")  # Get email from query parameters
    if not email:
        return jsonify({"error": "Email parameter is required"}), 400

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT message, created_at FROM messages WHERE email = %s ORDER BY created_at DESC", (email,))
    results = cur.fetchall()
    cur.close()
    conn.close()

    if not results:
        return jsonify({"error": "No messages found"}), 404

    return jsonify({"email": email, "messages": [{"message": msg, "timestamp": str(ts)} for msg, ts in results]})


# Entry point for running Flask
if __name__ == "__main__":
    create_table()
    app.run(host="0.0.0.0", port=5000, debug=True)
