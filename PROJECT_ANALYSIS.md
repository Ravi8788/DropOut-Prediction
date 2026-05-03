# AI Dropout Prediction and Counselling - Project Analysis

**Project Date:** April 27, 2026  
**Author:** Ravi  
**Tech Stack:** Python, Streamlit, Scikit-learn, Pandas, SQLite

---

## 1. PROJECT OVERVIEW

### 1.1 Purpose
An intelligent **Streamlit-based dashboard** designed to:
- **Predict student dropout risk** using machine learning algorithms
- **Track student performance** across academic, attendance, and financial metrics
- **Facilitate counseling decisions** through mentor notes and risk classifications
- **Automate communication** with students and guardians via email
- **Support college administration** with data-driven insights

### 1.2 Target Users
- **College administrators** - Manage dropout prevention programs
- **Academic mentors/counselors** - Identify at-risk students and provide guidance
- **Department coordinators** - Monitor department-wide academic performance
- **Data Science educators** - Potential use case for BTech Data Science programs

### 1.3 Problem Statement
Educational institutions face high student dropout rates. Manual identification of at-risk students is time-consuming and error-prone. This system automates risk detection and facilitates timely intervention.

---

## 2. TECHNICAL ARCHITECTURE

### 2.1 Application Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Frontend Framework** | Streamlit | 1.49.0 |
| **Data Processing** | Pandas | 2.3.2 |
| **ML Algorithm** | Scikit-learn | 1.7.2 |
| **Data Visualization** | Matplotlib | 3.10.6 |
| **Database** | SQLite | Built-in |
| **Email Service** | SMTP (Gmail) | OAuth/App Password |
| **Language** | Python 3.11+ | Latest |

### 2.2 Directory Structure

```
d:\AI Drop out Prediction and Counselling\
├── professional_demo.py          # Main Streamlit application
├── demo.py                       # Enhanced alternate version (plotly, advanced DB)
├── creation.py                   # Data generation script
│
├── Data Files (CSV)
│   ├── Attendance.csv            # Student attendance records
│   ├── Marks.csv                 # Subject marks & attempts
│   ├── Fees.csv                  # Fee payment status
│   ├── Emails.csv                # Contact information
│   └── Mentor_Notes.csv          # Counselor observations
│
├── Database Files (SQLite)
│   ├── student_data.db           # Primary database (professional_demo.py)
│   └── enhanced_student_data.db  # Enhanced database (demo.py)
│
├── Deployment Configuration
│   ├── Procfile                  # Render/Heroku deployment
│   ├── render.yaml               # Render service config
│   ├── netlify.toml              # Netlify static site config
│   └── netlify-site/index.html   # Frontend wrapper (iframe)
│
├── Configuration
│   ├── email_config.json         # SMTP & email credentials
│   └── requirements.txt          # Python dependencies
│
├── Documentation
│   ├── README.md                 # Setup & deployment guide
│   ├── DEPLOY_NETLIFY.md         # Netlify deployment steps
│   └── Dropout Prediction Dashboard.pdf  # Project documentation
│
└── Utilities
    ├── run_dashboard.bat         # Windows batch launcher
    └── get-pip.py                # Pip installation utility
```

---

## 3. CORE FEATURES

### 3.1 Data Input Sources

**Five primary CSV files:**

1. **Attendance.csv**
   - Student_ID, Name, Class, Attendance (%)
   - Tracks class attendance percentage

2. **Marks.csv**
   - Student_ID, Maths, Science, English
   - Failed_Subjects (count of subjects < 40 marks)
   - Attempts (1-4 retake attempts)

3. **Fees.csv**
   - Student_ID, Fee_Paid (Yes/No)
   - Indicates financial obligation status

4. **Emails.csv**
   - Student_ID, Student_Email, Guardian_Email
   - Contact information for notifications

5. **Mentor_Notes.csv**
   - Student_ID, Mentor_Notes
   - Qualitative observations from counselors

### 3.2 ML Prediction Model

**Algorithm:** Random Forest Classifier (professional_demo.py)
- **Alternative:** Gradient Boosting + Random Forest ensemble (demo.py)

**Feature Engineering:**
- Attendance (continuous)
- Average marks across subjects
- Failed subjects count
- Fee payment status (categorical → numeric)
- Attempts taken
- Score trend (optional historical marks)

**Output:** Risk Classification
- HIGH RISK → Immediate intervention needed
- MEDIUM RISK → Monitoring recommended
- LOW RISK → Healthy trajectory

### 3.3 Dashboard Features

#### 📊 Analytics Views
- **Risk Distribution** - Pie/bar charts showing risk category breakdown
- **Attendance Trends** - Historical attendance patterns
- **Subject Performance** - Marks heatmap across Maths, Science, English
- **Fee Status** - Payment compliance overview

#### 👥 Student Management
- **Student List** - All students with risk scores
- **Risk Indicators** - Color-coded risk levels
- **Searchable Interface** - Filter by student ID, name, class
- **Detailed Profiles** - Individual student analytics

#### ✉️ Communication Module
- **Email Alerts** - Automated emails to students/guardians
- **Mentor Notifications** - Department-wise mentor alerts (SY/TY)
- **Report Scheduling** - Daily/manual report generation
- **Email Logging** - Track sent communications

#### 📝 Mentor Interaction
- **Add/Edit Notes** - Counselor comments on student progress
- **Track Interventions** - Record actions taken for at-risk students
- **Historical Notes** - Maintain counseling history

### 3.4 Advanced Features (demo.py)

- **Plotly Visualizations** - Interactive charts
- **Academic Records Table** - Historical marks tracking
- **Attendance Trends** - Month-over-month analysis
- **Fee Tracking** - Due date + payment date + days overdue
- **Advanced Database Schema** - Normalized tables for scalability

---

## 4. DATABASE DESIGN

### 4.1 Professional Demo DB (student_data.db)

```sql
students TABLE:
├── Student_ID (PRIMARY KEY)
├── Name, Class
├── Contact: Student_Email, Guardian_Email
├── Academic: Attendance, Maths, Science, English, Average_Marks, Attempts
├── Fee_Paid (Yes/No)
├── Prediction: Risk (HIGH/MEDIUM/LOW)
├── Trend Features: Score_Trend, Trend_Label
└── Counseling: Mentor_Notes

report_log TABLE:
├── Report_Date (PRIMARY KEY)
└── Sent_At (timestamp)
```

### 4.2 Enhanced Demo DB (enhanced_student_data.db)

Additional tables for production:
- `academic_records` - Historical marks per subject/semester
- `attendance_records` - Monthly attendance tracking with trends
- `fee_records` - Detailed payment history with due dates
- Supports normalized schema for scalability

---

## 5. DEPLOYMENT STRATEGY

### 5.1 Current Architecture

```
Frontend (Netlify Static)
    ↓ [iframe]
Backend (Render - Streamlit)
    ↓
SQLite Database
    ↓
SMTP Service (Gmail)
```

### 5.2 Backend Deployment (Render)

**Service:** `dropout-prediction-dashboard`
**Type:** Web service (Python)
**Build Command:** `pip install -r requirements.txt`
**Start Command:** `streamlit run professional_demo.py --server.port $PORT --server.address 0.0.0.0`
**Python Version:** 3.11.9

**Required Environment Variables:**
```
DROPOUT_EMAIL_FROM              (Gmail address)
DROPOUT_EMAIL_PASSWORD          (Gmail app password)
DROPOUT_MENTOR_EMAIL_SY         (SY mentor email)
DROPOUT_MENTOR_EMAIL_TY         (TY mentor email)
DROPOUT_SMTP_SERVER             (default: smtp.gmail.com)
DROPOUT_SMTP_PORT               (default: 465)
```

### 5.3 Frontend Deployment (Netlify)

**Framework:** Static site wrapper
**Publish Directory:** `netlify-site/`
**Config File:** `netlify.toml`
**Setup:**
- SPA redirect configured (all routes → index.html)
- Hosts a landing page that iframes the Render Streamlit app

### 5.4 Production Considerations

⚠️ **Current Limitations:**
- SQLite database doesn't persist across Render restarts
- Single instance scaling (no distributed sessions)
- No containerization (Docker)

✅ **Recommended Upgrades:**
- Migrate to PostgreSQL for persistent data
- Use Render's PostgreSQL add-on
- Implement session management
- Add authentication (JWT/OAuth)
- Use Docker for better environment consistency

---

## 6. DATA FLOW

```
CSV Files (Input)
    ↓
creation.py (generates demo CSVs if needed)
    ↓
professional_demo.py / demo.py
    ├─→ Load CSVs via Pandas
    ├─→ Train ML Model (Random Forest)
    ├─→ Store in SQLite
    ├─→ Predict Risk Scores
    ├─→ Display Dashboard
    └─→ Send Emails (optional)
    ↓
SQLite Database
    ├─→ Students table (risk predictions)
    ├─→ Report log (sent communications)
    └─→ (Enhanced: academic, attendance, fee records)
    ↓
SMTP Gateway (Gmail)
    ↓
Student/Guardian/Mentor Inboxes
```

---

## 7. KEY PYTHON SCRIPTS

### 7.1 creation.py
**Purpose:** Generate dummy data for testing
**Output:** 5 CSV files with 20 sample students (SY/TY Data Science)
**Run:** `python creation.py`
**Note:** Only generates BTech Data Science students (no divisions)

### 7.2 professional_demo.py
**Purpose:** Main Streamlit application
**Features:**
- Clean, professional UI
- Risk prediction dashboard
- Email sending with template
- Mentor notes tracking
- Daily report scheduling
**Run:** `streamlit run professional_demo.py`
**Port:** localhost:8501

### 7.3 demo.py
**Purpose:** Enhanced alternate version
**Features:**
- Plotly interactive visualizations
- Advanced database schema
- Gradient Boosting + Random Forest ensemble
- More detailed analytics
**Note:** Uses `enhanced_student_data.db` separately
**Run:** `streamlit run demo.py`

### 7.4 email_config.json
**Purpose:** SMTP credentials (for offline testing)
**Fields:** email_from, email_password, smtp_server, mentor emails
**Note:** Environment variables override this file

---

## 8. SECURITY CONSIDERATIONS

### 🔐 Current Issues

1. **Hardcoded Credentials** 
   - `email_config.json` contains plaintext Gmail password
   - Should never be committed to production
   
2. **No Authentication**
   - Anyone with dashboard URL can access all student data
   - No login/role-based access control
   
3. **Email Exposure**
   - Student/guardian emails visible in UI
   - Consider masking or access controls

4. **SQLite Limitations**
   - No encryption at rest
   - No user audit logs
   - Single-threaded (not suitable for concurrent users)

### ✅ Recommendations

1. **Use Environment Variables Only**
   ```bash
   export DROPOUT_EMAIL_FROM="..."
   export DROPOUT_EMAIL_PASSWORD="..."
   ```

2. **Implement Authentication**
   - Streamlit authentication (streamlit-authenticator library)
   - Role-based access (admin, mentor, viewer)

3. **Add Encryption**
   - Encrypt sensitive student data
   - Use HTTPS only (enforced by Render)

4. **Migration to Production DB**
   - PostgreSQL with encrypted connections
   - Row-level security for data isolation

5. **Audit Logging**
   - Log all data access
   - Track email send failures

---

## 9. FUNCTIONALITY MATRIX

| Feature | Status | Location | Requirements |
|---------|--------|----------|--------------|
| Load Student Data | ✅ Active | Both scripts | CSV files |
| ML Prediction | ✅ Active | Both scripts | sklearn |
| SQLite Storage | ✅ Active | Both scripts | sqlite3 |
| Dashboard UI | ✅ Active | Both scripts | Streamlit |
| Visualization | ✅ Active (Matplotlib in pro, Plotly in demo) | Both scripts | matplotlib/plotly |
| Email Sending | ✅ Active | Both scripts | SMTP + env vars |
| Mentor Notes | ✅ Active | Both scripts | SQLite update |
| Report Scheduling | ✅ Active | professional_demo.py | Daily check logic |
| Render Deployment | ✅ Configured | render.yaml | Render account |
| Netlify Frontend | ✅ Configured | netlify.toml | Netlify account |
| Historical Marks Trend | ✅ Optional | professional_demo.py | Optional CSV |
| Department-wise Mentors | ✅ Implemented | Both scripts | Env vars (SY/TY) |

---

## 10. WORKFLOW & USE CASES

### Use Case 1: Identify At-Risk Students
1. Upload CSV files (or use `creation.py` to generate demo)
2. Open dashboard
3. View risk distribution
4. Filter by HIGH RISK students
5. Mentor adds counseling notes
6. System sends email notifications

### Use Case 2: Monitor Attendance Trends
1. Dashboard → Attendance Tab
2. View historical attendance graphs
3. Identify students below threshold (typically 75%)
4. Correlate with marks and fees
5. Plan intervention

### Use Case 3: Generate Daily Reports
1. System auto-checks if report sent today
2. Aggregates HIGH RISK students
3. Compiles report with metrics
4. Sends email to SY/TY mentors
5. Logs in `report_log` table

### Use Case 4: Track Counseling Interventions
1. Mentor clicks "Add Note" for student
2. Enters observation/action taken
3. Saved to SQLite `Mentor_Notes`
4. Persists across sessions
5. Visible in student detail view

---

## 11. PERFORMANCE & SCALABILITY

### Current Metrics
- **Students Supported:** 20-100 (demo dataset)
- **Data Load Time:** < 2 seconds
- **ML Training Time:** < 1 second (20 students)
- **Dashboard Load:** < 3 seconds
- **Email Send Time:** 2-5 seconds per email

### Bottlenecks

1. **SQLite Single-Threaded**
   - Locks during concurrent writes
   - Not suitable for > 100 concurrent users

2. **In-Memory Data**
   - Entire dataset loaded on each interaction
   - Streamlit reruns script on every button click

3. **No Caching**
   - Model retrains unnecessarily
   - CSV re-reads on every session

4. **Email Blocking**
   - Synchronous SMTP sends pause UI
   - Should use async/queue for large batches

### Scaling Recommendations

| Change | Impact | Effort |
|--------|--------|--------|
| Add `@st.cache_data` to data loads | 🟢 High | 🟢 Low |
| Cache ML model with joblib | 🟢 High | 🟢 Low |
| Migrate to PostgreSQL | 🟢 Critical | 🟡 Medium |
| Async email queue (Celery) | 🟡 Medium | 🔴 High |
| Redis caching layer | 🟡 Medium | 🔴 High |
| Containerize with Docker | 🟢 Important | 🟡 Medium |

---

## 12. DATA QUALITY ISSUES & FIXES

### Identified Issues

1. **Missing Columns**
   - Not all students have mentor notes
   - Trend_Label may be missing
   - **Fix:** Apply defaults (empty string, 0)

2. **Inconsistent Data Types**
   - Attendance might be int or float
   - Fee_Paid stored as "Yes"/"No" (categorical)
   - **Fix:** Explicit type casting in load functions

3. **Email Format Validation**
   - `email_config.json` has typo: `gmai.com` instead of `gmail.com`
   - **Fix:** Validate email format, use env vars instead

4. **Duplicate Student IDs**
   - Risk if creation.py runs twice
   - **Fix:** Check for duplicates during load

5. **Marks Out of Bounds**
   - Some marks might exceed 100
   - Attempts might be 0 or > 4
   - **Fix:** Clamp values during preprocessing

### Data Validation Code

```python
def validate_and_clean_data(df):
    """Ensure data consistency"""
    # Type conversions
    df['Attendance'] = pd.to_numeric(df['Attendance'], errors='coerce').fillna(0)
    df['Maths'] = pd.to_numeric(df['Maths'], errors='coerce').fillna(0)
    df['Science'] = pd.to_numeric(df['Science'], errors='coerce').fillna(0)
    df['English'] = pd.to_numeric(df['English'], errors='coerce').fillna(0)
    
    # Clamp values
    df['Attendance'] = df['Attendance'].clip(0, 100)
    for col in ['Maths', 'Science', 'English']:
        df[col] = df[col].clip(0, 100)
    
    # Remove duplicates
    df = df.drop_duplicates(subset=['Student_ID'])
    
    # Fill missing
    df['Mentor_Notes'].fillna("", inplace=True)
    df['Attempts'].fillna(1, inplace=True)
    
    return df
```

---

## 13. CONFIGURATION CHECKLIST

### Before Running

- [ ] Virtual environment created and activated
- [ ] `pip install -r requirements.txt` executed
- [ ] CSV files exist or run `python creation.py`
- [ ] For email features: Set environment variables
  ```bash
  export DROPOUT_EMAIL_FROM="your-email@gmail.com"
  export DROPOUT_EMAIL_PASSWORD="your-app-password"
  ```

### Before Deployment

- [ ] Remove `email_config.json` or mark as `.gitignore`
- [ ] All env vars configured in Render dashboard
- [ ] Test email sending in local environment
- [ ] Verify Netlify custom domain (if used)
- [ ] Check Render service logs for startup errors

### Production Checklist

- [ ] Enable HTTPS (automatic on Render)
- [ ] Add authentication layer
- [ ] Migrate to PostgreSQL
- [ ] Set up automated backups
- [ ] Configure monitoring/alerts
- [ ] Add API rate limiting
- [ ] Enable CORS if needed

---

## 14. TESTING STRATEGY

### Unit Tests Needed

```python
# Test data loading
def test_load_attendance_csv():
    df = load_attendance("Attendance.csv")
    assert len(df) > 0
    assert 'Student_ID' in df.columns

# Test model prediction
def test_risk_prediction():
    model = train_model(data)
    predictions = model.predict(X_test)
    assert all(p in ['HIGH', 'MEDIUM', 'LOW'] for p in predictions)

# Test email validation
def test_email_format():
    assert validate_email("student@example.com")
    assert not validate_email("invalid-email")
```

### Integration Tests
- CSV → DB → Model → Prediction pipeline
- Email sending with mock SMTP
- Concurrent user sessions
- Data persistence across restarts

### Manual Tests
- Load dashboard with different class filters
- Send test email to mentor
- Edit mentor notes, verify persistence
- Try filter by risk level
- Check visualizations render correctly

---

## 15. FUTURE ENHANCEMENTS

### Phase 2 (Short-term)
- [ ] Add data validation & error handling
- [ ] Implement caching for performance
- [ ] Add user authentication
- [ ] Migrate to PostgreSQL
- [ ] Create REST API for external integrations

### Phase 3 (Medium-term)
- [ ] Advanced ML: Deep learning models
- [ ] Predictive analytics: predict future semester marks
- [ ] Recommendation engine: suggest interventions
- [ ] Mobile app companion
- [ ] Parent/student portal

### Phase 4 (Long-term)
- [ ] Integration with college ERP system
- [ ] Real-time alerts system (SMS/Slack)
- [ ] Multi-college support
- [ ] AI chatbot for student support
- [ ] Blockchain-based certificate issuance

---

## 16. TROUBLESHOOTING GUIDE

| Issue | Cause | Solution |
|-------|-------|----------|
| "No such table: students" | DB corrupted | Delete `.db` files, restart app |
| Email sending fails | Wrong env vars | Check DROPOUT_EMAIL_FROM, PASSWORD |
| Dashboard blank | CSV not found | Run `python creation.py` |
| Streamlit crashes | Memory limit | Reduce dataset, use caching |
| Render deployment fails | Missing dependencies | Add to requirements.txt |
| Gmail 2FA blocked | Security policy | Use app-specific password |

---

## 17. SUMMARY

### Strengths ✅
- Clean, user-friendly Streamlit interface
- Automated ML-based risk prediction
- Email notification system
- SQLite persistence
- Deployment infrastructure in place
- Scalable architecture foundation

### Weaknesses ⚠️
- No authentication/authorization
- SQLite not production-ready
- Hardcoded credentials in config
- No error handling for email failures
- Limited data validation
- Single-threaded (not concurrent-safe)

### Opportunities 🚀
- PostgreSQL migration
- API layer for integrations
- Mobile app
- Advanced ML models
- Real-time notifications
- Multi-institution support

### Threats 🛡️
- Data privacy regulations (GDPR/FERPA)
- Email deliverability issues
- Database failures
- Scaling challenges
- Security vulnerabilities

---

## 18. QUICK START COMMANDS

```bash
# Setup
python -m venv venv
source venv/Scripts/activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Generate demo data
python creation.py

# Run main dashboard
streamlit run professional_demo.py

# Run enhanced version
streamlit run demo.py

# Deploy to Render
git push origin main  # (auto-deploys with render.yaml)
```

---

**Document Generated:** April 27, 2026  
**Project Status:** Development/Early Deployment Phase  
**Maintainer:** Ravi  
**Version:** 1.0 (Analysis)
