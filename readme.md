# AI Applications Lab - Task 3: Tesseract, Keycloak, and Streamlit

## Project Overview

This project demonstrates the integration of Tesseract for Optical Character Recognition (OCR), Keycloak for authentication, and Streamlit for creating a web application interface. The goal is to create a secure web application that can extract text from images and display the results.

## Tech Stack

- **Tesseract**: An open-source OCR engine used to extract text from images.
- **Keycloak**: An open-source identity and access management solution for authentication and authorization.
- **Streamlit**: An open-source app framework for Machine Learning and Data Science teams to create beautiful web apps.

## Getting Started

Follow these steps to initialize and run the project:

### Prerequisites

- Python 3.7 or higher
- Tesseract OCR
- Keycloak server
- Streamlit

### Installation

1. **Clone the repository:**
    ```sh
    git clone https://github.com/your-username/your-repo-name.git
    cd your-repo-name
    ```

2. **Set up a virtual environment:**
    ```sh
    python -m venv venv
    source venv/bin/activate   # On Windows use `venv\Scripts\activate`
    ```

3. **Install the required Python packages:**
    ```sh
    pip install -r requirements.txt
    ```

4. **Install Tesseract OCR:**
    - Follow the instructions on the [Tesseract GitHub page](https://github.com/tesseract-ocr/tesseract) to install Tesseract for your operating system.

5. **Set up Keycloak:**
    - Download and install Keycloak from the [official website](https://www.keycloak.org/downloads).
    - Start the Keycloak server and create a new realm and client for the application.

### Running the Application

1. **Start the Streamlit app:**
    ```sh
    streamlit run app.py
    ```

2. **Access the application:**
    - Open your web browser and go to `http://localhost:8501`.

## Usage

- Upload an image file through the Streamlit interface.
- The application will use Tesseract to extract text from the image.
- The extracted text will be displayed on the web page.
- Authentication is handled by Keycloak to ensure secure access to the application.

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any questions or feedback, please open an issue on the GitHub repository.
