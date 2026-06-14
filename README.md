# AI Dropout Prediction and Counselling

This project is a Streamlit-based dashboard to identify students at dropout risk and support counselling decisions using attendance, marks, fees, and mentor notes.

## Features

- Student risk prediction using machine learning
- Dashboard views for attendance, marks, and fee status
- Mentor notes tracking
- Email configuration for reports and communication
- CSV-based data workflow

## Project Structure

- `professional_demo.py`: Main Streamlit app
- `demo.py`: Alternate app/demo entrypoint
- `Attendance.csv`, `Marks.csv`, `Fees.csv`, `Emails.csv`, `Mentor_Notes.csv`: Input data files
- `student_data.db`, `enhanced_student_data.db`: SQLite databases
- `render.yaml`, `Procfile`, `requirements.txt`: Backend deployment setup
- `netlify.toml`, `netlify-site/index.html`: Netlify frontend wrapper setup

## Local Setup

1. Create and activate a virtual environment.
2. Install dependencies:

	```bash
	pip install -r requirements.txt
	```

3. Run the app:

	```bash
	streamlit run professional_demo.py
	```

4. Open the local URL shown in terminal (usually `http://localhost:8501`).

## Environment Variables

Set these for email/report features:

- `DROPOUT_EMAIL_FROM`
- `DROPOUT_EMAIL_PASSWORD`
- `DROPOUT_MENTOR_EMAIL_SY` (optional)
- `DROPOUT_MENTOR_EMAIL_TY` (optional)
- `DROPOUT_SMTP_SERVER` (optional, default: `smtp.gmail.com`)
- `DROPOUT_SMTP_PORT` (optional, default: `465`)

## Deployment

This repository includes a working deployment structure:

- Backend (Streamlit): Render
- Frontend wrapper: Netlify

### Backend on Render

1. Connect this GitHub repository to Render.
2. Deploy using `render.yaml` (or use `Procfile` + start command).
3. Set environment variables in Render.
4. Copy your Render service URL.

### Frontend on Netlify

1. In `netlify-site/index.html`, replace:

	- `https://your-render-service.onrender.com`

	with your real Render URL.

2. Connect this repo to Netlify.
3. Publish directory is `netlify-site` (already configured in `netlify.toml`).

Detailed deployment steps are in `DEPLOY_NETLIFY.md`.

## Notes

- Netlify does not run Streamlit directly as a long-running Python service.
- Current DB is SQLite; for production persistence, consider migrating to PostgreSQL.

## Authors & Contributors

- **Owner/Author**: [Ravi8788](https://github.com/Ravi8788)
- **Contributor**: [sahilkatkar0026](https://github.com/sahilkatkar0026)