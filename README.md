

Github Repository: https://github.com/keita-nakata/job-training-teamc

# Important

# Django Project Setup

This guide explains how to set up this Django project on your local machine.

---

## 1. Clone the repository

First, download the project from GitHub.

```bash
git clone https://github.com/keita-nakata/job-training-teamc.git
cd job-training-teamc
```

---

## 2. Create a virtual environment

Create a virtual environment for this project.

```bash
python -m venv venv
```

If `python` does not work, try:

```bash
python3 -m venv venv
```

---

## 3. Activate the virtual environment

### macOS / Linux

```bash
source venv/bin/activate
```

### Windows (PowerShell)

```powershell
.\venv\Scripts\Activate
```

After activation, you should see `(venv)` at the beginning of your terminal prompt.

---

## 4. Install dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

---

## 5. Apply database migrations (optional)

If this project includes database models, apply migrations:

```bash
python manage.py migrate
```

---

## 6. Run the development server

Start the Django development server:

```bash
python manage.py runserver
```

Then open your browser and visit:

```
http://127.0.0.1:8000/
```

You should now see the project running locally 🎉

---

## 7. Deactivate the virtual environment

When you're done working:

```bash
deactivate
```
