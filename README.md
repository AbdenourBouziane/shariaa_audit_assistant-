# Shariah Audit Assistant - Deployment Guide

This guide walks you through deploying the **Shariah Audit Assistant**, a tool that analyzes financial documents for Shariah compliance using a Flask backend and an HTML/JavaScript frontend.

---

## 🧰 Prerequisites

- Python 3.8 or higher
- `pip` (Python package installer)
- Basic command-line knowledge
- A local folder to store PDF documents for analysis

---

## 📁 Project Structure

```

shariah-audit-assistant/
├── app.py                      # Flask backend API
├── shariah\_audit\_assistant.py # Core audit logic
├── requirements.txt            # Python dependencies
├── static/                     # Frontend files
│   └── index.html              # User interface
├── pdfs/                       # Uploaded PDF files
└── README.md                   # Deployment guide

````

---

## ⚙️ Step 1: Set Up the Environment

1. **Create the project directory:**

   ```bash
   mkdir shariah-audit-assistant
   cd shariah-audit-assistant
````

2. **Set up a virtual environment:**

   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**

   * **Windows:**

     ```bash
     venv\Scripts\activate
     ```
   * **macOS/Linux:**

     ```bash
     source venv/bin/activate
     ```

4. **Create `requirements.txt` with the following content:**

   ```text
   flask==2.3.3
   flask-cors==4.0.0
   langchain==0.1.0
   langchain-community==0.0.10
   langchain-together==0.0.1
   python-dotenv==1.0.0
   tenacity==8.2.3
   faiss-cpu==1.7.4
   huggingface-hub==0.19.4
   sentence-transformers==2.2.2
   PyPDF2==3.0.1
   ```

5. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

---

## 🏗️ Step 2: Set Up Application Files

1. Add your core logic in `shariah_audit_assistant.py`.

2. Create `app.py` with the Flask API logic (from your backend code).

3. Create the frontend folder and file:

   ```bash
   mkdir -p static
   ```

   Place your frontend interface in `static/index.html`.

4. Create a folder to store uploaded PDF files:

   ```bash
   mkdir -p pdfs
   ```

---

## 🔐 Step 3: Configure Environment Variables

Create a `.env` file in the project root:

```env
TOGETHER_API_KEY=your_together_api_key
PDF_FOLDER=./pdfs
PORT=5000
```

> 🔑 Replace `your_together_api_key` with your actual key from [Together AI](https://together.ai).

---

## 🚀 Step 4: Run the Application

1. Make sure your virtual environment is activated.

2. Start the Flask app:

   ```bash
   python app.py
   ```

3. Open the frontend in your browser:

   ```
   http://localhost:5000/static/index.html
   ```

---

## 🧪 Step 5: Using the Application

1. Place your PDF files inside the `pdfs` folder.

2. Enter a product description or contract in the frontend.

3. Click **"Perform Shariah Audit"**.

4. Review the results across:

   * **Summary** – Quick compliance insights
   * **Violations** – List of flagged non-compliant clauses
   * **Detailed Analysis** – In-depth clause evaluation

---

## 🛠️ Troubleshooting

* Check the Flask console for errors.
* Verify your `.env` file is correctly configured.
* Ensure PDF files are placed in the correct `pdfs` directory.
* Confirm your Together API key is valid and active.

---

## 📦 Production Deployment

1. **Use a WSGI server like Gunicorn:**

   ```bash
   pip install gunicorn
   gunicorn app:app
   ```

2. **Set up a reverse proxy with Nginx** for better performance and static file handling.

3. **Deploy to a cloud provider** (e.g., AWS, GCP, Azure) or container platform (e.g., Docker, Kubernetes).

4. **Secure your app:**

   * Enable HTTPS
   * Add API authentication and rate limiting
   * Restrict CORS in production

---

## 🎨 Customization

* **Theme Colors:** Edit CSS variables in the `<style>` section of `index.html`.
* **New Features:** Extend the Flask API and update the frontend.
* **Advanced Analytics:** Enhance the `ShariahAuditAssistant` class logic.
