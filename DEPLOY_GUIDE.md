# 🚀 Deploy Ticket Management System to PythonAnywhere

## Prerequisites
- A **GitHub account** with your code pushed to a repository
- A **PythonAnywhere account** (free): https://www.pythonanywhere.com/registration/register/beginner/

---

## Step 1: Push Your Code to GitHub

If you haven't already, push your project to GitHub:

```bash
cd "e:\Academics\Django Project"
git add .
git commit -m "Prepare for PythonAnywhere deployment"
git push origin main
```

> **Note**: Make sure `.env` and `db.sqlite3` are NOT pushed (they're in `.gitignore`).

---

## Step 2: Create a PythonAnywhere Account

1. Go to https://www.pythonanywhere.com
2. Click **"Start running Python online"** → Sign up for a **free Beginner account**
3. Remember your username — your site will be at: `yourusername.pythonanywhere.com`

---

## Step 3: Clone Your Code on PythonAnywhere

1. On PythonAnywhere, go to **Dashboard** → Click **"$ Bash"** (under "New console")
2. In the Bash console, run:

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
```

This creates a folder with your project code.

---

## Step 4: Set Up Virtual Environment

In the same Bash console:

```bash
cd YOUR_REPO_NAME/ticket_project
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Step 5: Create the `.env` File on PythonAnywhere

```bash
nano .env
```

Paste the following (replace values):

```
SECRET_KEY=paste-a-new-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourusername.pythonanywhere.com
```

> **Generate a secret key** at https://djecrety.ir/ — copy it and paste as your SECRET_KEY.

Press `Ctrl+X`, then `Y`, then `Enter` to save.

---

## Step 6: Run Database Migrations & Collect Static Files

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

Follow the prompts to create an admin account (username, email, password).

---

## Step 7: Configure the Web App

1. Go to PythonAnywhere **Dashboard** → Click **"Web"** tab → **"Add a new web app"**
2. Click **Next** → Select **"Manual configuration"** (NOT "Django")
3. Select **Python 3.10** (or latest available)
4. Click **Next** to create the web app

---

## Step 8: Configure WSGI File

1. On the **Web** tab, find **"WSGI configuration file"** — click the link to edit it
2. **Delete everything** in the file and replace with:

```python
import os
import sys

# Add your project directory to the path
project_home = '/home/yourusername/YOUR_REPO_NAME/ticket_project'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set the Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'ticket_project.settings'

# Load the .env file
from dotenv import load_dotenv
env_path = os.path.join(project_home, '.env')
load_dotenv(env_path)

# Start Django
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

> ⚠️ **Replace `yourusername`** with your PythonAnywhere username and **`YOUR_REPO_NAME`** with your actual repo folder name.

3. Click **Save**

---

## Step 9: Configure Virtual Environment

On the **Web** tab, find **"Virtualenv"** section, enter:

```
/home/yourusername/YOUR_REPO_NAME/ticket_project/venv
```

---

## Step 10: Configure Static Files

On the **Web** tab, find **"Static files"** section, add:

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/yourusername/YOUR_REPO_NAME/ticket_project/staticfiles` |

---

## Step 11: Go Live! 🎉

1. Click the big green **"Reload"** button on the Web tab
2. Visit `https://yourusername.pythonanywhere.com`
3. Your Ticket Management System should be live!

---

## Troubleshooting

### "Server Error (500)"
- Check the **error log**: Web tab → click on the error log link
- Most common cause: wrong paths in WSGI file or missing `.env`

### "Static files not loading (CSS missing)"
- Make sure you ran `python manage.py collectstatic --noinput`
- Verify the static files mapping path in Web tab matches your actual `staticfiles/` directory

### "DisallowedHost" error
- Add your PythonAnywhere domain to `ALLOWED_HOSTS` in your `.env` file
- Reload the web app

### Need to update your code?
```bash
cd ~/YOUR_REPO_NAME
git pull origin main
cd ticket_project
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```
Then click **Reload** on the Web tab.
