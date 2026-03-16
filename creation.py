import pandas as pd
import numpy as np

num_students = 20  # Number of students

# ----------------------------
# Generate Student IDs, Names, Classes, Emails
# ----------------------------
student_ids = range(101, 101 + num_students)

# Realistic Indian-style names for demo
first_names = ["Aarav","Vivaan","Aditya","Sai","Ananya","Ishaan","Kavya","Diya","Rohan","Meera",
               "Aryan","Saanvi","Krishna","Aditi","Tanvi","Ria","Dev","Shreya","Kabir","Naina"]
last_names = ["Sharma","Patel","Gupta","Verma","Reddy","Singh","Choudhary","Mehta","Jain","Khan"]

# Generate random names
names = [f"{np.random.choice(first_names)} {np.random.choice(last_names)}" for _ in range(num_students)]

# Only SY and TY Data Science (no divisions, no other dept)
years = ['SY', 'TY']
department = "BTech Data Science"
classes = [f"{np.random.choice(years)} {department}" for _ in range(num_students)]

# Random student & guardian emails
student_emails = [f"{name.lower().replace(' ','')}@example.com" for name in names]
guardian_emails = [f"guardian_{i}@example.com" for i in range(num_students)]

# ----------------------------
# Attendance CSV
# ----------------------------
attendance = np.random.randint(40, 100, size=num_students)
attendance_df = pd.DataFrame({
    'Student_ID': student_ids,
    'Name': names,
    'Class': classes,
    'Attendance': attendance
})
attendance_df.to_csv('Attendance.csv', index=False)

# ----------------------------
# Marks CSV
# ----------------------------
marks = {
    'Maths': np.random.randint(20, 100, size=num_students),
    'Science': np.random.randint(20, 100, size=num_students),
    'English': np.random.randint(20, 100, size=num_students)
}
marks_df = pd.DataFrame({'Student_ID': student_ids, **marks})

# Count failed subjects (<40 marks considered fail)
marks_df['Failed_Subjects'] = (marks_df[['Maths','Science','English']] < 40).sum(axis=1)

# Random number of attempts (1 to 4)
marks_df['Attempts'] = np.random.randint(1, 5, size=num_students)

marks_df.to_csv('Marks.csv', index=False)

# ----------------------------
# Fees CSV
# ----------------------------
fee_status = np.random.choice(['Yes','No'], size=num_students, p=[0.8,0.2])
fees_df = pd.DataFrame({
    'Student_ID': student_ids,
    'Fee_Paid': fee_status
})
fees_df.to_csv('Fees.csv', index=False)

# ----------------------------
# Emails CSV (students + guardians together in one file)
# ----------------------------
emails_df = pd.DataFrame({
    'Student_ID': student_ids,
    'Student_Email': student_emails,
    'Guardian_Email': guardian_emails
})
emails_df.to_csv('Emails.csv', index=False)

# ----------------------------
# Optional Mentor Notes CSV
# ----------------------------
mentor_notes_df = pd.DataFrame({
    'Student_ID': student_ids,
    'Mentor_Notes': [""] * num_students
})
mentor_notes_df.to_csv('Mentor_Notes.csv', index=False)

print("✅ Generated Attendance.csv, Marks.csv, Fees.csv, Emails.csv (Student+Guardian together), Mentor_Notes.csv for 20 students (SY/TY Data Science only)")
