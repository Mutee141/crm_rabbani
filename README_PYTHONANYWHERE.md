# Deploy CRM Rabbani to PythonAnywhere - Complete Guide

## 🚀 Quick Start (15 minutes)

### Step 1: Create PythonAnywhere Account
1. Go to https://www.pythonanywhere.com/
2. Click **"Create a Free account"**
3. Choose **"Beginner"** plan (free)
4. Verify your email address

### Step 2: Set Up Your Account
1. After login, go to **"Account"** tab
2. Note your **username** (this will be part of your URL)
3. Go to **"Dashboard"** tab

### Step 3: Create Web App
1. Click **"Web"** tab (left sidebar)
2. Click **"+ Add a new web app"**
3. Select **"Manual configuration"**
4. Choose **"Python 3.12"** (or latest available)
5. Click **"Next"**

### Step 4: Set Up Database
1. Go to **"Databases"** tab
2. Click **"Initialize a new database"**
3. Choose **"MySQL"**
4. Note your database password
5. Your database name will be: `yourusername$crm_rabbani`

### Step 5: Upload Your Code
1. Go to **"Files"** tab
2. Navigate to `/home/yourusername/`
3. Click **"Upload a file"**
4. Upload your entire project as a ZIP file
5. Right-click the ZIP file and **"Unzip"**
6. Rename the folder to `mysite`

### Step 6: Configure Virtual Environment
1. Go to **"Consoles"** tab
2. Click **"$"** (Bash console)
3. Run these commands:
```bash
cd ~/mysite
mkvirtualenv --python=/usr/bin/python3.12 myenv
workon myenv
pip install -r requirements.txt
```

### Step 7: Update Settings for Your Username
1. In **"Files"**, open `rabbani/pythonanywhere_settings.py`
2. Replace ALL instances of `yourusername` with your actual PythonAnywhere username
3. Update database password with your MySQL password

### Step 8: Configure Web App
1. Go back to **"Web"** tab
2. Set **"Source code"** to: `/home/yourusername/mysite`
3. Set **"Working directory"** to: `/home/yourusername/mysite`
4. Set **"WSGI configuration file"** to: `/home/yourusername/mysite/wsgi.py`
5. Click **"Reload"** button

### Step 9: Run Migrations
1. Go to **"Consoles"** tab
2. Open your Bash console
3. Run:
```bash
cd ~/mysite
workon myenv
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### Step 10: Test Your App
1. Go to **"Web"** tab
2. Click the URL: `https://yourusername.pythonanywhere.com`
3. You should see your CRM login page!

## 🔧 Troubleshooting

### If you get "500 Server Error":
1. Check **"Web"** tab → **"Error log"**
2. Common issues:
   - Wrong username in settings file
   - Database password incorrect
   - Missing dependencies

### If static files don't load:
1. Run: `python manage.py collectstatic --noinput`
2. Click **"Reload"** in Web tab

### If database connection fails:
1. Verify database name: `yourusername$crm_rabbani`
2. Check database password in **"Databases"** tab
3. Update settings file with correct password

## 📱 Your Live App URL

After successful deployment, your CRM will be available at:
`https://yourusername.pythonanywhere.com`

**Share this URL with users - NOT your GitHub repository!**

## 🔄 Updating Your App

When you make changes:
1. Upload new files to `/home/yourusername/mysite/`
2. In Bash console:
```bash
cd ~/mysite
workon myenv
pip install -r requirements.txt  # if new dependencies
python manage.py migrate
python manage.py collectstatic --noinput
```
3. Go to **"Web"** tab and click **"Reload"**

## 💡 Pro Tips

- **Free plan limitations**: 100MB storage, limited CPU time
- **Upgrade anytime**: More resources for larger teams
- **Custom domain**: Available on paid plans
- **SSL certificate**: Automatically provided

## 🆘 Need Help?

If you get stuck:
1. Check the error logs in **"Web"** tab
2. Make sure all `yourusername` placeholders are replaced
3. Verify database credentials
4. Ensure all requirements are installed

Your CRM will be live and accessible to users once deployed! 🎉
