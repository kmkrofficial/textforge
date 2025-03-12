import streamlit as st
import base64
import pytesseract
from PIL import Image
import io
import datetime
import psycopg2
from keycloak import KeycloakOpenID
from streamlit_cookies_manager import CookieManager
from kafka import KafkaProducer
import json

# Keycloak settings
KEYCLOAK_SERVER_URL = "http://localhost:8080"
KEYCLOAK_REALM = "master"
KEYCLOAK_CLIENT_ID = "streamlit-tesseract"
KEYCLOAK_CLIENT_SECRET = "VZ7vo5htQ2LXBIY7okanesviwEJFmYuV"
SESSION_EXPIRY_HOURS = 3

# Kafka settings
KAFKA_TOPIC = "ocr-messages"
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"

# Database settings
DB_CONFIG = {
    "dbname": "ai-applications",
    "user": "postgres",
    "password": "password",
    "host": "localhost",
    "port": "5432"
}

# Initialize Keycloak client
keycloak_openid = KeycloakOpenID(server_url=KEYCLOAK_SERVER_URL,
                                 client_id=KEYCLOAK_CLIENT_ID,
                                 realm_name=KEYCLOAK_REALM,
                                 client_secret_key=KEYCLOAK_CLIENT_SECRET)


# Streamlit layout configuration
st.set_page_config(layout="wide")

cookies = CookieManager()

# Initialize Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)


def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def fetch_messages_from_db(username):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT text_data, created_at FROM public.extracted_text WHERE username = %s ORDER BY created_at DESC", (username,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"message": row[0], "created_at": row[1].isoformat()} for row in rows]

def authenticate_user(username, password):
    try:
        token = keycloak_openid.token(username, password)
    except Exception as e:
        st.error("Incorrect email or password.")
        return None, False
    roles = set(keycloak_openid.decode_token(token['access_token'])["resource_access"]
                .get(KEYCLOAK_CLIENT_ID, {}).get("roles", []))
    if "access-tesseract" not in roles:
        return token, False
    return token, True

def convert_image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def extract_text_from_image(image):
    image_data = base64.b64decode(convert_image_to_base64(image))
    image = Image.open(io.BytesIO(image_data))
    return pytesseract.image_to_string(image)

def preprocess_text(text):
    return text.strip().lower()

def send_to_kafka(username, message):
    data = {"username": username, "message": message}
    print(f"Sending message to Kafka: {data}")
    producer.send(KAFKA_TOPIC, data)

if cookies.ready():
    if "token" in cookies:
        st.session_state["token"] = cookies.get("token")
    if "expires_at" in cookies:
        try:
            st.session_state["expires_at"] = datetime.datetime.fromisoformat(cookies.get("expires_at"))
        except Exception:
            pass
    if "username" in cookies:
        st.session_state["username"] = cookies.get("username")

if "expires_at" in st.session_state and datetime.datetime.now(datetime.timezone.utc) > st.session_state["expires_at"]:
    st.error("Session expired. Please log in again.")
    st.session_state.clear()
    cookies.__delitem__("token")
    cookies.__delitem__("expires_at")
    cookies.save()
    st.rerun()

def logout():
    st.session_state.clear()
    cookies.__delitem__("token")
    cookies.__delitem__("username")
    cookies.__delitem__("expires_at")
    cookies.save()
    st.rerun()

if "token" not in st.session_state:
    st.title("Login to Image Text Extractor")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        token, has_access = authenticate_user(username, password)
        if token is None:
            st.error("Incorrect email or password.")
        elif not has_access:
            st.error("Insufficient permissions. Your account does not have the required role.")
        else:
            st.session_state["token"] = token
            st.session_state["username"] = username
            st.session_state["expires_at"] = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=SESSION_EXPIRY_HOURS)
            cookies["token"] = token
            cookies["expires_at"] = st.session_state["expires_at"].isoformat()
            cookies["username"] = str(username)
            cookies.save()
            st.success("Login successful!")
            st.rerun()
else:
    st.title("Dashboard - Image Text Extractor")
    if st.button("Logout"):
        logout()
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_container_width=True)
       
        if st.button("Extract Text"):
            raw_text = extract_text_from_image(image)
            processed_text = preprocess_text(raw_text)
            st.text_area("Extracted Text", processed_text, height=200)
            send_to_kafka(st.session_state.get("username", "unknown"), processed_text)
    
    # Fetch and display messages from the database
    st.subheader("Retrieved Messages")
    username = st.session_state.get("username", "unknown")
    messages = fetch_messages_from_db(username)
    
    if messages:
        st.dataframe(messages, use_container_width=True)  # Expands table width
    else:
        st.write("No messages found.")
