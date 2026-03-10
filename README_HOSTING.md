# 🚀 Hosting TNP Intelligence Hub

This folder is ready for deployment to the web. Follow these simple steps to host your dashboard online.

## Option 1: Streamlit Community Cloud (Recommended & Free)
1. **Upload to GitHub**: Create a new private or public repository on GitHub and upload all files from the `TNP_Web_Hosting` folder to it.
2. **Sign in to Streamlit**: Go to [share.streamlit.io](https://share.streamlit.io/) and log in with your GitHub account.
3. **Deploy App**:
   - Click "New app".
   - Select your repository, the main branch, and set the main file path to `dashboard.py`.
   - Click **Deploy**.
4. **Done!** Your dashboard will be live on a public (or private) URL.

## Option 2: Vercel (Static Hosting via stlite)
Vercel usually expects static sites (HTML). We have provided an `index.html` that uses **stlite** to run your Python code directly in the browser.

1. **Upload to GitHub**: Upload the entire content of `TNP_Web_Hosting` to a new repo.
2. **Import to Vercel**: Connect your GitHub repo to Vercel.
3. **Deployment Settings**:
   - Vercel will see the `index.html` and automatically treat it as a static site.
   - Click **Deploy**.
4. **Result**: Your dashboard will run at `your-project.vercel.app` WITHOUT needing a Python backend server.

---

## Folder Structure for Hosting
```text
TNP_Web_Hosting/
├── .streamlit/
│   └── config.toml    # Theme settings
├── index.html         # Vercel Entry Point (stlite)
├── dashboard.py       # Main Application code
├── placement_analyzer.py # Analytics Engine code
├── requirements.txt   # Dependencies (for Streamlit Cloud)
└── amcat-raw-data.csv # Default Data
```

---

## Option 3: Streamlit Community Cloud (Traditional Python)
1. **Upload to GitHub**: Upload all files.
2. **Deploy**: Go to [share.streamlit.io](https://share.streamlit.io/) and select `dashboard.py`.
3. **Benefit**: Faster initial load than Vercel/stlite, but requires a Streamlit account.

## Data Persistence Note
Since web hosting platforms use ephemeral filesystems, any data you upload via the "Data Source" section in the sidebar will be lost if the server restarts. 
- **For a permanent update**: Replace the `amcat-raw-data.csv` in your GitHub repository with your latest data.
- **For dynamic use**: Use the drag-and-drop feature on the live site for temporary analysis.
