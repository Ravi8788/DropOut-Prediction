import streamlit as st
import pandas as pd
import sqlite3
from sklearn.ensemble import RandomForestClassifier
from email.message import EmailMessage
import smtplib
import matplotlib.pyplot as plt
import os
import json
from datetime import datetime

# ----------------------------
# Database Functions
# ----------------------------
def init_db():
    conn = sqlite3.connect('student_data.db')
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS students (
        Student_ID INTEGER PRIMARY KEY,
        Name TEXT,
        Class TEXT,
        Attendance REAL,
        Maths REAL,
        Science REAL,
        English REAL,
        Fee_Paid TEXT,
        Student_Email TEXT,
        Guardian_Email TEXT,
        Attempts REAL,
        Score_Trend REAL,
        Trend_Label TEXT,
        Average_Marks REAL,
        Risk TEXT,
        Mentor_Notes TEXT
    )
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS report_log (
        Report_Date TEXT PRIMARY KEY,
        Sent_At TEXT
    )
    ''')
    conn.commit()
    conn.close()

def insert_data(df):
    if 'Mentor_Notes' not in df.columns:
        df['Mentor_Notes'] = ""
    conn = sqlite3.connect('student_data.db')
    df.to_sql('students', conn, if_exists='replace', index=False)
    conn.close()

def update_notes(student_id, note):
    conn = sqlite3.connect('student_data.db')
    c = conn.cursor()
    c.execute("UPDATE students SET Mentor_Notes=? WHERE Student_ID=?", (note, student_id))
    conn.commit()
    conn.close()

def fetch_data():
    conn = sqlite3.connect('student_data.db')
    df = pd.read_sql("SELECT * FROM students", conn)
    conn.close()
    for col in ['Mentor_Notes','Fee_Paid','Student_Email','Guardian_Email','Attempts','Score_Trend','Trend_Label']:
        if col not in df.columns:
            if col in ['Attempts', 'Score_Trend']:
                df[col] = 0
            else:
                df[col] = ""
    return df

def was_report_sent_today(report_date):
    conn = sqlite3.connect('student_data.db')
    c = conn.cursor()
    c.execute("SELECT 1 FROM report_log WHERE Report_Date=?", (report_date,))
    row = c.fetchone()
    conn.close()
    return row is not None

def mark_report_sent(report_date):
    conn = sqlite3.connect('student_data.db')
    c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO report_log (Report_Date, Sent_At) VALUES (?, ?)",
        (report_date, datetime.now().isoformat(timespec='seconds')),
    )
    conn.commit()
    conn.close()

def build_trend_features(historical_df):
    trend_default = pd.DataFrame(columns=['Student_ID', 'Score_Trend', 'Trend_Label'])
    if historical_df.empty or 'Student_ID' not in historical_df.columns:
        return trend_default

    working = historical_df.copy()
    numeric_cols = [
        c for c in working.columns
        if c != 'Student_ID' and pd.api.types.is_numeric_dtype(working[c])
    ]

    if {'Student_ID', 'Score'}.issubset(working.columns):
        sort_col = None
        for candidate in ['Test_Date', 'Exam_Date', 'Attempt_No', 'Test_No']:
            if candidate in working.columns:
                sort_col = candidate
                break
        if sort_col is not None:
            working = working.sort_values(['Student_ID', sort_col])

        trend_series = working.groupby('Student_ID')['Score'].agg(
            lambda s: float(s.iloc[-1] - s.iloc[0]) if len(s) >= 2 else 0.0
        )
        trend_df = trend_series.reset_index(name='Score_Trend')
    elif len(numeric_cols) >= 2:
        trend_df = working[['Student_ID'] + numeric_cols].copy()
        trend_df['Score_Trend'] = trend_df[numeric_cols[-1]] - trend_df[numeric_cols[0]]
        trend_df = trend_df[['Student_ID', 'Score_Trend']]
    else:
        return trend_default

    def trend_label(x):
        if x <= -8:
            return 'Declining'
        if x >= 8:
            return 'Improving'
        return 'Stable'

    trend_df['Trend_Label'] = trend_df['Score_Trend'].apply(trend_label)
    return trend_df

EMAIL_CONFIG_FILE = "email_config.json"

def load_saved_email_config():
    defaults = {
        "email_from": os.getenv("DROPOUT_EMAIL_FROM", ""),
        "email_password": os.getenv("DROPOUT_EMAIL_PASSWORD", ""),
        "smtp_server": os.getenv("DROPOUT_SMTP_SERVER", "smtp.gmail.com"),
        "smtp_port": int(os.getenv("DROPOUT_SMTP_PORT", "465")),
        "mentor_email_sy": os.getenv("DROPOUT_MENTOR_EMAIL_SY", ""),
        "mentor_email_ty": os.getenv("DROPOUT_MENTOR_EMAIL_TY", ""),
    }

    if not os.path.exists(EMAIL_CONFIG_FILE):
        return defaults

    try:
        with open(EMAIL_CONFIG_FILE, "r", encoding="utf-8") as f:
            saved = json.load(f)
        defaults.update({
            "email_from": str(saved.get("email_from", defaults["email_from"])),
            "email_password": str(saved.get("email_password", defaults["email_password"])),
            "smtp_server": str(saved.get("smtp_server", defaults["smtp_server"])),
            "smtp_port": int(saved.get("smtp_port", defaults["smtp_port"])),
            "mentor_email_sy": str(saved.get("mentor_email_sy", defaults["mentor_email_sy"])),
            "mentor_email_ty": str(saved.get("mentor_email_ty", defaults["mentor_email_ty"])),
        })
    except Exception:
        return defaults

    return defaults

def save_email_config(config):
    with open(EMAIL_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

# ----------------------------
# Initialize DB
# ----------------------------
init_db()

# ----------------------------
# Streamlit Config + UI Theme
# ----------------------------
st.set_page_config(
    page_title="Dropout Prediction Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Global CSS for better UI
st.markdown(
    """
    <style>
        :root {
            --navy: #0b3b78;
            --navy-dark: #072a55;
            --slate: #334155;
            --surface: #f8fafc;
            --border: #dbe3ee;
            --text: #0f172a;
        }
        .stApp {
            background-color: #ffffff;
            color: var(--text);
        }
        [data-testid="stAppViewContainer"] {
            background-color: #ffffff;
        }
        [data-testid="stHeader"] {
            display: none;
        }
        [data-testid="stToolbar"] {
            display: none;
        }
        [data-testid="stDecoration"] {
            display: none;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
            border-right: 1px solid var(--border);
        }
        .block-container {
            max-width: 1250px;
            padding-top: 0.9rem;
            padding-bottom: 2rem;
        }
        h1, h2, h3, h4, h5, h6 {
            color: var(--text) !important;
            letter-spacing: 0.2px;
        }
        p {
            color: var(--slate);
        }
        [data-testid="stSidebar"] .stMarkdown,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            color: var(--text) !important;
            opacity: 1 !important;
            font-weight: 600;
        }
        [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"],
        [data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] {
            background-color: #ffffff !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 8px !important;
        }
        [data-testid="stFileUploaderDropzone"] {
            background: #ffffff !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 10px !important;
        }
        [data-testid="stFileUploaderDropzone"] * {
            color: #0f172a !important;
            opacity: 1 !important;
        }
        [data-testid="stFileUploaderDropzone"] button,
        [data-testid="stFileUploaderDropzone"] [kind="secondary"] {
            background-color: var(--navy) !important;
            color: #ffffff !important;
            border: 1px solid var(--navy-dark) !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
        }
        [data-testid="stFileUploaderDropzone"] button:hover,
        [data-testid="stFileUploaderDropzone"] [kind="secondary"]:hover {
            background-color: var(--navy-dark) !important;
            color: #ffffff !important;
        }
        [data-testid="stFileUploaderDropzone"] button * {
            color: #ffffff !important;
        }
        [data-testid="stMetricLabel"],
        [data-testid="stMetricValue"] {
            color: var(--text) !important;
        }
        .stButton > button {
            background-color: var(--navy) !important;
            color: #ffffff !important;
            border: 1px solid var(--navy-dark) !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            padding: 0.45rem 0.9rem !important;
        }
        .stButton > button * {
            color: #ffffff !important;
        }
        .stButton > button:hover {
            background-color: var(--navy-dark) !important;
            border-color: var(--navy-dark) !important;
            color: #ffffff !important;
        }
        .stButton > button:hover * {
            color: #ffffff !important;
        }
        [data-testid="stTextArea"] textarea,
        [data-testid="stTextInput"] input,
        [data-testid="stNumberInput"] input {
            background-color: #ffffff !important;
            color: #0f172a !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 8px !important;
        }
        [data-testid="stTextArea"] textarea::placeholder,
        [data-testid="stTextInput"] input::placeholder,
        [data-testid="stNumberInput"] input::placeholder {
            color: #64748b !important;
        }
        .main-title {
            text-align: center;
            font-size: 46px;
            font-weight: 800;
            color: var(--navy);
            text-shadow: 0 2px 10px rgba(11, 59, 120, 0.12);
            margin-bottom: 8px;
        }
        .sub-title {
            text-align: center;
            font-size: 19px;
            font-weight: 500;
            color: var(--slate);
            margin-bottom: 8px;
        }
        .hero-card {
            background: linear-gradient(120deg, #ffffff 0%, #f8fafc 100%);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 26px;
            margin-bottom: 20px;
            box-shadow: 0 8px 16px rgba(15, 23, 42, 0.06);
        }
        .hero-meta {
            text-align: center;
            font-size: 14px;
            color: #64748b;
            margin-top: 4px;
        }
        .section-heading {
            font-size: 24px;
            font-weight: 700;
            color: var(--navy);
            margin-bottom: 14px;
            border-bottom: 1px solid #e2e8f0;
            padding-bottom: 8px;
        }
        .report-section {
            background-color: #ffffff;
            padding: 20px 22px;
            border-radius: 14px;
            margin-bottom: 25px;
            border: 1px solid var(--border);
            box-shadow: 0 8px 18px rgba(15, 23, 42, 0.06);
        }
        table {
            width: 100%;
        }
        th {
            background-color: #003366;
            color: white;
            text-align: center;
            padding: 8px;
        }
        td {
            text-align: center;
            padding: 6px;
        }
        .status-note {
            background-color: #eff6ff;
            border: 1px solid #bfdbfe;
            color: #1e3a8a;
            border-radius: 10px;
            padding: 10px 14px;
            font-weight: 600;
            margin-bottom: 18px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Display Title
st.markdown(
    """
    <div class='hero-card'>
        <div class='main-title'>Dropout Prediction and Counseling Dashboard</div>
        <div class='sub-title'>Early warning analytics for timely academic intervention</div>
        <div class='hero-meta'>Institutional Monitoring Portal</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# CSV Upload
# ----------------------------
st.sidebar.header("Data Upload")
st.sidebar.caption("Upload all four files to refresh the dashboard data.")
attendance_file = st.sidebar.file_uploader("Attendance CSV", type=["csv"])
marks_file = st.sidebar.file_uploader("Marks CSV", type=["csv"])
fees_file = st.sidebar.file_uploader("Fees CSV", type=["csv"])
emails_file = st.sidebar.file_uploader("Emails CSV", type=["csv"])  # includes student + guardian
historical_marks_file = st.sidebar.file_uploader(
    "Historical Marks CSV (Optional)",
    type=["csv"],
    help="Used to detect score trend (improving/declining) over time.",
)

if attendance_file and marks_file and fees_file and emails_file:
    attendance = pd.read_csv(attendance_file)
    marks = pd.read_csv(marks_file)
    fees = pd.read_csv(fees_file)
    emails = pd.read_csv(emails_file)
    trend_df = pd.DataFrame(columns=['Student_ID', 'Score_Trend', 'Trend_Label'])

    if historical_marks_file is not None:
        historical_marks = pd.read_csv(historical_marks_file)
        trend_df = build_trend_features(historical_marks)

    if 'Fee_Paid' not in fees.columns:
        fees.rename(columns={fees.columns[1]:'Fee_Paid'}, inplace=True)
    if 'Student_Email' not in emails.columns:
        emails.rename(columns={emails.columns[1]:'Student_Email'}, inplace=True)
    if 'Guardian_Email' not in emails.columns:
        emails['Guardian_Email'] = ""

    data = attendance.merge(marks, on="Student_ID") \
                     .merge(fees, on="Student_ID") \
                     .merge(emails, on="Student_ID")

    if 'Attempts' not in data.columns:
        data['Attempts'] = 0

    if not trend_df.empty:
        data = data.merge(trend_df, on='Student_ID', how='left')
    if 'Score_Trend' not in data.columns:
        data['Score_Trend'] = 0.0
    if 'Trend_Label' not in data.columns:
        data['Trend_Label'] = 'Stable'

    data['Attempts'] = pd.to_numeric(data['Attempts'], errors='coerce').fillna(0).astype(int)
    data['Score_Trend'] = pd.to_numeric(data['Score_Trend'], errors='coerce').fillna(0.0)
    data['Trend_Label'] = data['Trend_Label'].fillna('Stable')
    
    data['Average_Marks'] = data[['Maths','Science','English']].mean(axis=1)
    if 'Mentor_Notes' not in data.columns:
        data['Mentor_Notes'] = ""

    # normalize class names (only SY/TY Data Science)
    def clean_class_name(x):
        x = str(x).strip()
        if "SY" in x:
            return "SY BTech Data Science"
        elif "TY" in x:
            return "TY BTech Data Science"
        else:
            return "Other"
    data['Class'] = data['Class'].apply(clean_class_name)
    data = data[data['Class'].isin(["SY BTech Data Science", "TY BTech Data Science"])]

    insert_data(data)
    st.success("✅ CSV Data Uploaded and Saved!")

# ----------------------------
# Fetch Data
# ----------------------------
data = fetch_data()
data['Fee_Status'] = data['Fee_Paid'].apply(lambda x: 1 if str(x).strip().lower()=='yes' else 0)
data['Attempts'] = pd.to_numeric(data['Attempts'], errors='coerce').fillna(0).astype(int)
data['Score_Trend'] = pd.to_numeric(data['Score_Trend'], errors='coerce').fillna(0.0)
data['Trend_Label'] = data['Trend_Label'].fillna('Stable')

# ----------------------------
# Risk Calculation
# ----------------------------
def calculate_risk(row):
    risk = 0
    if row['Attendance'] < 75: risk += 1
    if row['Average_Marks'] < 40: risk += 1
    if row['Fee_Status'] == 0: risk += 1
    failed_subjects = sum([row['Maths']<40, row['Science']<40, row['English']<40])
    if failed_subjects >= 2: risk += 1
    if row['Attempts'] >= 3: risk += 1
    if row['Attempts'] >= 5: risk += 1
    if row['Score_Trend'] <= -8: risk += 1
    if risk == 0: return "Low"
    elif risk <= 3: return "Medium"
    else: return "High"

data['Risk'] = data.apply(calculate_risk, axis=1)

# ----------------------------
# ML Prediction
# ----------------------------
X = data[['Attendance','Average_Marks','Fee_Status','Attempts','Score_Trend']]
risk_mapping = {'Low':0,'Medium':1,'High':2}
y = data['Risk'].map(risk_mapping)
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X,y)
data['Predicted_Risk_Num'] = model.predict(X)
reverse_mapping = {0:'Low',1:'Medium',2:'High'}
data['Predicted_Risk'] = data['Predicted_Risk_Num'].map(reverse_mapping)
insert_data(data)

# ----------------------------
# Filters
# ----------------------------
st.sidebar.header("Filters")
class_options = ['All Classes'] + ["SY BTech Data Science", "TY BTech Data Science"]
class_selected = st.sidebar.selectbox("Select Class", class_options)
risk_filter = st.sidebar.multiselect("Select Risk Level", ['Low','Medium','High'], default=['Low','Medium','High'])

st.sidebar.header("Auto Reports")
auto_reports_enabled = st.sidebar.checkbox("Enable daily auto reports", value=False)
auto_report_time = st.sidebar.time_input("Daily report time", value=datetime.strptime("18:00", "%H:%M").time())

saved_email_config = load_saved_email_config()

with st.sidebar.expander("Email Configuration", expanded=False):
    st.caption("Values are auto-loaded from saved settings or env vars.")
    email_from_input = st.text_input(
        "Sender Email",
        value=saved_email_config["email_from"],
        placeholder="example@gmail.com",
    )
    email_password_input = st.text_input(
        "Email App Password",
        value=saved_email_config["email_password"],
        type="password",
        placeholder="Gmail app password",
    )
    smtp_server_input = st.text_input(
        "SMTP Server",
        value=saved_email_config["smtp_server"],
    )
    smtp_port_input = st.number_input(
        "SMTP Port",
        min_value=1,
        max_value=65535,
        value=int(saved_email_config["smtp_port"]),
        step=1,
    )
    mentor_email_sy_input = st.text_input(
        "Mentor Email (SY)",
        value=saved_email_config["mentor_email_sy"],
        placeholder="mentor_sy@example.com",
    )
    mentor_email_ty_input = st.text_input(
        "Mentor Email (TY)",
        value=saved_email_config["mentor_email_ty"],
        placeholder="mentor_ty@example.com",
    )

    save_col, clear_col = st.columns(2)
    if save_col.button("Save Settings"):
        save_email_config({
            "email_from": email_from_input.strip(),
            "email_password": email_password_input.strip(),
            "smtp_server": smtp_server_input.strip() or "smtp.gmail.com",
            "smtp_port": int(smtp_port_input),
            "mentor_email_sy": mentor_email_sy_input.strip(),
            "mentor_email_ty": mentor_email_ty_input.strip(),
        })
        st.success("Email settings saved locally.")
    if clear_col.button("Clear Saved"):
        if os.path.exists(EMAIL_CONFIG_FILE):
            os.remove(EMAIL_CONFIG_FILE)
        st.info("Saved email settings removed.")

EMAIL_FROM = email_from_input.strip()
EMAIL_PASSWORD = email_password_input.strip()
SMTP_SERVER = smtp_server_input.strip() or "smtp.gmail.com"
SMTP_PORT = int(smtp_port_input)
MENTOR_EMAIL_SY = mentor_email_sy_input.strip()
MENTOR_EMAIL_TY = mentor_email_ty_input.strip()

if class_selected == 'All Classes':
    filtered_data = data[data['Predicted_Risk'].isin(risk_filter)]
else:
    filtered_data = data[(data['Class'] == class_selected) & (data['Predicted_Risk'].isin(risk_filter))]

st.markdown(
    f"<div class='status-note'>Active View: {class_selected} | Selected Risk Levels: {', '.join(risk_filter) if risk_filter else 'None'}</div>",
    unsafe_allow_html=True,
)

# ----------------------------
# Table with Risk Colors
# ----------------------------
def color_risk(risk):
    if risk=="High": return "background-color:#b91c1c;color:white"
    elif risk=="Medium": return "background-color:#f59e0b;color:#111827"
    else: return "background-color:#15803d;color:white"

st.markdown('<div class="report-section">', unsafe_allow_html=True)
st.markdown("<div class='section-heading'>Student Risk Table</div>", unsafe_allow_html=True)
styled_table = (
    filtered_data.style
    .set_properties(**{"background-color": "#ffffff", "color": "#0f172a"})
    .map(color_risk, subset=['Predicted_Risk'])
)
st.dataframe(styled_table, width='stretch')
if 'Attempts' in filtered_data.columns and 'Trend_Label' in filtered_data.columns:
    st.caption("Risk now includes attempts exhausted and historical score-trend decline.")
st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------
# Charts
# ----------------------------
st.markdown('<div class="report-section">', unsafe_allow_html=True)
st.markdown("<div class='section-heading'>Academic Performance Analytics</div>", unsafe_allow_html=True)
if filtered_data.empty:
    st.info("No student data available for current filters.")
else:
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.caption("Attendance by Student")
        attendance_fig, attendance_ax = plt.subplots(figsize=(6, 3.8))
        attendance_ax.bar(filtered_data['Name'], filtered_data['Attendance'], color="#0b3b78")
        attendance_ax.set_ylabel("Attendance (%)", color="#334155")
        attendance_ax.tick_params(axis='x', rotation=45, labelsize=8)
        attendance_ax.tick_params(axis='y', labelsize=9)
        attendance_ax.set_facecolor("#ffffff")
        attendance_ax.grid(axis='y', linestyle='--', alpha=0.25)
        attendance_fig.patch.set_facecolor("#ffffff")
        st.pyplot(attendance_fig)

    with chart_col2:
        st.caption("Average Marks by Student")
        marks_fig, marks_ax = plt.subplots(figsize=(6, 3.8))
        marks_ax.bar(filtered_data['Name'], filtered_data['Average_Marks'], color="#64748b")
        marks_ax.set_ylabel("Average Marks", color="#334155")
        marks_ax.tick_params(axis='x', rotation=45, labelsize=8)
        marks_ax.tick_params(axis='y', labelsize=9)
        marks_ax.set_facecolor("#ffffff")
        marks_ax.grid(axis='y', linestyle='--', alpha=0.25)
        marks_fig.patch.set_facecolor("#ffffff")
        st.pyplot(marks_fig)

st.markdown('</div>', unsafe_allow_html=True)
# ----------------------------
# Dashboard Summary
# ----------------------------
st.markdown('<div class="report-section">', unsafe_allow_html=True)
st.markdown("<div class='section-heading'>Dashboard Summary</div>", unsafe_allow_html=True)

total_students = len(filtered_data)
high_risk = (filtered_data['Predicted_Risk'] == "High").sum()
medium_risk = (filtered_data['Predicted_Risk'] == "Medium").sum()
low_risk = (filtered_data['Predicted_Risk'] == "Low").sum()
avg_attendance = filtered_data['Attendance'].mean()
avg_marks = filtered_data['Average_Marks'].mean()

summary_col1, summary_col2, summary_col3 = st.columns(3)
summary_col1.metric("Total Students", total_students)
summary_col2.metric("High Risk", high_risk)
summary_col3.metric("Medium Risk", medium_risk)

summary_col4, summary_col5, summary_col6 = st.columns(3)
summary_col4.metric("Low Risk", low_risk)
summary_col5.metric("Avg Attendance (%)", f"{avg_attendance:.2f}" if total_students else "0.00")
summary_col6.metric("Avg Marks", f"{avg_marks:.2f}" if total_students else "0.00")
st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------
# Pie Chart of Risk Levels
# ----------------------------

st.markdown('<div class="report-section">', unsafe_allow_html=True)
st.markdown("<div class='section-heading'>Risk Distribution</div>", unsafe_allow_html=True)

risk_counts = filtered_data['Predicted_Risk'].value_counts()
if risk_counts.empty:
    st.info("No risk distribution data available for current filters.")
else:
    fig, ax = plt.subplots()
    ax.pie(risk_counts, labels=risk_counts.index, autopct='%1.1f%%', startangle=90,
           colors=["#15803d", "#f59e0b", "#b91c1c"])
    ax.axis('equal')
    st.pyplot(fig)
st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------
# Mentor Notes
# ----------------------------
st.markdown('<div class="report-section">', unsafe_allow_html=True)
st.markdown("<div class='section-heading'>Mentor Notes</div>", unsafe_allow_html=True)
for i, row in filtered_data.iterrows():
    note = st.text_area(f"Notes for {row['Name']}", value=row['Mentor_Notes'] if 'Mentor_Notes' in row else '', key=row['Student_ID'])
    update_notes(row['Student_ID'], note)
st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------
# Email (Students + Guardians)
# ----------------------------
st.markdown('<div class="report-section">', unsafe_allow_html=True)
st.markdown("<div class='section-heading'>Email Reports to Students and Guardians</div>", unsafe_allow_html=True)

def validate_email_config():
    if not EMAIL_FROM or not EMAIL_PASSWORD:
        return False, "Missing email credentials. Open the left sidebar and fill Sender Email and Email App Password in Email Configuration."
    return True, None

def validate_smtp_login():
    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.login(EMAIL_FROM, EMAIL_PASSWORD)
        return True, None
    except Exception as e:
        err = str(e)
        if "InvalidSecondFactor" in err or "Application-specific password required" in err:
            return False, "Gmail requires an App Password. Enable 2-Step Verification on your Google account, then create and use a 16-character App Password in Email Configuration."
        return False, err

def send_email(to_email, subject, content, html=False):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_FROM
    msg['To'] = to_email
    if html:
        msg.add_alternative(content, subtype='html')
    else:
        msg.set_content(content)

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.login(msg['From'], EMAIL_PASSWORD)
            smtp.send_message(msg)
        return True, None
    except Exception as e:
        return False, str(e)

def send_students_guardians_reports(df):
    is_valid, err = validate_email_config()
    if not is_valid:
        return 0, [("Email Configuration", err)]

    smtp_ok, smtp_err = validate_smtp_login()
    if not smtp_ok:
        return 0, [("SMTP Login", smtp_err)]

    sent_count = 0
    failed_list = []
    for _, row in df.iterrows():
        content = f"""
D Y Patil Technical Campus, Talsande

Hello {row['Name']},

Your academic report shows:
- Risk Level: {row['Predicted_Risk']}
- Average Marks: {row['Average_Marks']:.2f}
- Attendance: {row['Attendance']}%
- Attempts: {int(row['Attempts'])}
- Score Trend: {row['Trend_Label']} ({row['Score_Trend']:+.1f})

Marks Details:
- Maths: {row['Maths']}
- Science: {row['Science']}
- English: {row['English']}

Please contact your mentor for guidance.
"""
        for email in [row['Student_Email'], row['Guardian_Email']]:
            if email:
                success, error = send_email(email, f"Academic Risk Report - {row['Name']}", content)
                if success:
                    sent_count += 1
                else:
                    failed_list.append((email, error))
    return sent_count, failed_list

def send_mentor_reports(df):
    is_valid, err = validate_email_config()
    if not is_valid:
        return 0, [("Email Configuration", err)]

    smtp_ok, smtp_err = validate_smtp_login()
    if not smtp_ok:
        return 0, [("SMTP Login", smtp_err)]

    mentor_emails = {
        "SY BTech Data Science": "ravirajchoudhari07@gmail.com",
        "TY BTech Data Science": "ravirajchoudhari8788@gmail.com",
    }
    sent_count = 0
    failed_list = []

    def risk_color(risk):
        if risk == "High":
            return "#b91c1c"
        elif risk == "Medium":
            return "#f59e0b"
        else:
            return "#15803d"

    for class_name, mentor_email in mentor_emails.items():
        if not mentor_email:
            continue

        class_data = df[df['Class'] == class_name]
        if class_data.empty:
            continue

        table_html = f"""
        <html>
        <body>
        <h2 style=\"color:#003366;\">Mentor Risk Report - {class_name}</h2>
        <p>This is the consolidated academic report for your class:</p>
        <table border=\"1\" cellpadding=\"5\" cellspacing=\"0\" style=\"border-collapse:collapse;width:100%;\">
            <tr>
                <th>Name</th>
                <th>Class</th>
                <th>Risk Level</th>
                <th>Average Marks</th>
                <th>Attendance</th>
                <th>Attempts</th>
                <th>Score Trend</th>
                <th>Maths</th>
                <th>Science</th>
                <th>English</th>
                <th>Fee Paid</th>
                <th>Mentor Notes</th>
            </tr>
        """

        for _, row in class_data.iterrows():
            color = risk_color(row['Predicted_Risk'])
            table_html += f"""
            <tr style=\"background-color:{color}; color:white;\">
                <td>{row['Name']}</td>
                <td>{row['Class']}</td>
                <td>{row['Predicted_Risk']}</td>
                <td>{row['Average_Marks']:.2f}</td>
                <td>{row['Attendance']}%</td>
                <td>{int(row['Attempts'])}</td>
                <td>{row['Trend_Label']} ({row['Score_Trend']:+.1f})</td>
                <td>{row['Maths']}</td>
                <td>{row['Science']}</td>
                <td>{row['English']}</td>
                <td>{row['Fee_Paid']}</td>
                <td>{row['Mentor_Notes']}</td>
            </tr>
            """

        table_html += "</table></body></html>"

        success, error = send_email(mentor_email, f"Mentor Risk Report - {class_name}", table_html, html=True)
        if success:
            sent_count += 1
        else:
            failed_list.append((mentor_email, error))

    return sent_count, failed_list

if auto_reports_enabled and not filtered_data.empty:
    now = datetime.now()
    today_key = now.strftime("%Y-%m-%d")
    if now.time() >= auto_report_time and not was_report_sent_today(today_key):
        sg_sent, sg_failed = send_students_guardians_reports(filtered_data)
        mentor_sent, mentor_failed = send_mentor_reports(filtered_data)
        mark_report_sent(today_key)
        st.sidebar.success(
            f"Auto reports sent: students/guardians={sg_sent}, mentors={mentor_sent}"
        )
        if sg_failed or mentor_failed:
            st.sidebar.warning(
                f"Auto report failures: {len(sg_failed) + len(mentor_failed)}"
            )

if st.button("Send All Reports (Students and Guardians)"):
    sent_count, failed_list = send_students_guardians_reports(filtered_data)
    st.success(f"✅ Successfully sent {sent_count} emails!")
    if failed_list:
        st.error("❌ Failed to send to:")
        for email, err in failed_list:
            st.write(f"- {email}: {err}")
st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------
# Email (Mentors)
# ----------------------------
st.markdown('<div class="report-section">', unsafe_allow_html=True)
st.markdown("<div class='section-heading'>Email Reports to Mentors</div>", unsafe_allow_html=True)

if st.button("Send Reports to Mentors"):
    sent_count, failed_list = send_mentor_reports(filtered_data)

    st.success(f"✅ Successfully sent {sent_count} mentor reports!")
    if failed_list:
        st.error("❌ Failed to send to:")
        for email, err in failed_list:
            st.write(f"- {email}: {err}")
st.markdown('</div>', unsafe_allow_html=True)
