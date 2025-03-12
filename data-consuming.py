import json
import psycopg2
import logging
from kafka import KafkaConsumer
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Database Configuration
DB_CONFIG = {
    "dbname": "ai-applications",
    "user": "postgres",
    "password": "password",
    "host": "localhost",
    "port": "5432"
}

# Kafka Configuration
KAFKA_TOPIC = "ocr-messages"
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"

# Connect to PostgreSQL
def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

# Initialize Database Table
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS public.extracted_text (
            id SERIAL PRIMARY KEY,
            username TEXT NOT NULL,
            text_data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

# Save message to PostgreSQL
def save_to_db(username, text_data):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO public.extracted_text (username, text_data, created_at) VALUES (%s, %s, %s)",
        (username, text_data, datetime.utcnow())
    )
    conn.commit()
    cur.close()
    conn.close()
    logging.info(f"Saved message from {username}")

# Kafka Consumer Process
def consume_messages():
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="ocr-consumer-group",
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        value_deserializer=lambda x: json.loads(x.decode("utf-8"))
    )
    
    logging.info("Kafka Consumer started. Waiting for messages...")
    
    for msg in consumer:
        try:
            data = msg.value
            username = data.get("username", "unknown")
            text_data = data.get("message", "")
            
            if username and text_data:
                save_to_db(username, text_data)
            else:
                logging.warning("Received message with missing data fields")
        except Exception as e:
            logging.error(f"Error processing message: {e}")

if __name__ == "__main__":
    init_db()
    consume_messages()
