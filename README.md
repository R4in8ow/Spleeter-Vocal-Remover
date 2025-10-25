# 🎧 Team Amigos AI Splitter (Spleeter Vocal Remover)



This is a local web application built with Python's **Flask** framework, leveraging **Deezer's Spleeter** library for high-quality **Music Source Separation**. Users can upload any audio file (MP3/WAV) and instantly receive the separated Vocal and Instrumental tracks in MP3 format. The application features a clean, modern **Liquid Glass (Glassmorphism)** UI design.

## ✨ Features

* **Vocal Isolation:** Separate vocals and instrumental tracks from any song.
* **High Quality Output:** Uses Spleeter's pre-trained model for accurate separation.
* **MP3 Output:** All resulting audio stems are provided in MP3 format.
* **Modern UI:** Features a Liquid Glass (Glassmorphism) design with animated backgrounds and custom file input.
* **Localhost Deployment:** Designed to run efficiently on a local development server.

---

## 🚀 Getting Started (Local Setup)

### Prerequisites

To run this application, you need **Python 3.8** (or compatible) and **FFmpeg** installed on your system. We highly recommend using a **Conda** or **Virtual Environment (Venv)** to manage dependencies and avoid system conflicts.

### Step 1: Clone the Repository

Clone this repository to your local machine:

```bash
git clone YOUR_REPOSITORY_URL
cd your-repository-name

**Create and Activate Environment**
We must use the specific Python environment (3.8) to ensure Spleeter/TensorFlow dependencies (like Click, Protobuf, Jinja2) are compatible.
# Create a new Conda environment with Python 3.8
conda create -n vocal_env_py38 python=3.8 -y

# Activate the new environment
conda activate vocal_env_py38


**Install Dependencies**
Install all required Python packages (Flask, Spleeter, etc.) from the requirements.txt file:
python -m pip install -r requirements.txt


**Run the Application**
Start the Flask server on your localhost:
python app.py
