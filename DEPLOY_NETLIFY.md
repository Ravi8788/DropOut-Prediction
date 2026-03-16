# Deploy to Netlify (with Streamlit backend)

Netlify does not run long-lived Streamlit servers directly.
Use this production setup:

- Backend: Render runs `professional_demo.py` (Streamlit app)
- Frontend: Netlify hosts `netlify-site/index.html` and embeds the Render URL

## 1) Push this project to GitHub

From the project folder:

    git init
    git add .
    git commit -m "Add Render + Netlify deploy setup"
    git branch -M main
    git remote add origin https://github.com/<your-username>/<your-repo>.git
    git push -u origin main

## 2) Deploy backend on Render

1. Open Render dashboard.
2. Click New > Blueprint and select your GitHub repo.
3. Render auto-detects `render.yaml`.
4. Create service.
5. In service Environment, set these secrets:
   - `DROPOUT_EMAIL_FROM`
   - `DROPOUT_EMAIL_PASSWORD`
   - `DROPOUT_MENTOR_EMAIL_SY` (optional)
   - `DROPOUT_MENTOR_EMAIL_TY` (optional)
6. Wait until deploy is healthy and copy URL, for example:
   - `https://dropout-prediction-dashboard.onrender.com`

## 3) Point Netlify page to Render URL

1. Edit `netlify-site/index.html`.
2. Replace both instances of:

    https://your-render-service.onrender.com

with your real Render URL.

3. Commit and push changes.

## 4) Deploy frontend on Netlify

1. Open Netlify dashboard.
2. Add new site > Import an existing project.
3. Choose this GitHub repo.
4. Build settings are auto-read from `netlify.toml`:
   - Publish directory: `netlify-site`
5. Deploy site.

## 5) Verify

- Open Netlify URL.
- Confirm Streamlit app renders in the iframe.
- Test upload, prediction, and email workflow.

## Notes

- SQLite file storage on Render free plan is ephemeral.
- If you need persistent database storage, move from SQLite to a managed DB (PostgreSQL).
- If iframe loading is blocked by browser/security policy, deploy directly on Render and use that URL as your primary app link.
