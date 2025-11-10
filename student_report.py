# ===========================================
# 🎓 STUDENT PERFORMANCE ANALYZER - REPORT VERSION (with Plotly)
# ===========================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# ===========================================
# 📂 Load Data
# ===========================================
df = pd.read_csv("students.csv")

# ===========================================
# 🧮 Data Processing
# ===========================================
df['Total'] = df[['Maths', 'Science', 'English', 'History']].sum(axis=1)
df['Average'] = df['Total'] / 4

def grade(avg):
    if avg >= 90: return 'A+'
    elif avg >= 80: return 'A'
    elif avg >= 70: return 'B'
    elif avg >= 60: return 'C'
    elif avg >= 50: return 'D'
    else: return 'F'

df['Grade'] = df['Average'].apply(grade)
df['Result'] = np.where(df['Average'] >= 40, 'Pass', 'Fail')

# ===========================================
# 📊 Summary Statistics
# ===========================================
print("📈 Total Students:", len(df))
print("📊 Average Score:", round(df['Average'].mean(), 2))
print("✅ Pass %:", round((df['Result'].value_counts().get('Pass', 0) / len(df)) * 100, 2))
print("🏆 Top Student:", df.loc[df['Average'].idxmax(), 'Name'])
print("-" * 50)

# ===========================================
# 🎨 Visualization (Matplotlib / Seaborn)
# ===========================================
sns.set(style="whitegrid", palette="coolwarm")

# 1️⃣ Subject-wise Average
plt.figure(figsize=(12,6))
subject_avg = df[['Maths','Science','English','History']].mean()
subject_avg.plot(kind='bar', color='skyblue')
plt.title('Subject-wise Average Marks')
plt.ylabel('Marks')
plt.tight_layout()
plt.show()

# 2️⃣ Grade Distribution
plt.figure(figsize=(6,6))
df['Grade'].value_counts().plot(kind='pie', autopct='%1.1f%%', startangle=140, colors=sns.color_palette('pastel'))
plt.title('Grade Distribution')
plt.ylabel('')
plt.show()

# 3️⃣ Gender vs Average
plt.figure(figsize=(8,5))
sns.boxplot(x='Gender', y='Average', data=df, palette='Set2')
plt.title('Gender vs Average Marks')
plt.show()

# 4️⃣ Study Hours vs Average
plt.figure(figsize=(8,5))
sns.lineplot(x='Study Hours/Week', y='Average', data=df, marker='o', color='tomato')
plt.title('Study Hours vs Average Marks')
plt.show()

# 5️⃣ Attendance vs Average
plt.figure(figsize=(8,5))
sns.scatterplot(x='Attendance (%)', y='Average', hue='Result', data=df, s=80)
plt.title('Attendance vs Average Marks')
plt.show()

# ===========================================
# 🌐 Interactive Visualizations (Plotly)
# ===========================================

print("\n🌟 Launching interactive visualizations...")

# 1️⃣ Interactive Subject-wise Average
subject_avg_df = subject_avg.reset_index()
subject_avg_df.columns = ['Subject', 'Average Marks']
fig1 = px.bar(subject_avg_df, x='Subject', y='Average Marks',
              title='📊 Subject-wise Average Marks (Interactive)',
              color='Subject', text='Average Marks', color_discrete_sequence=px.colors.qualitative.Set2)
fig1.update_traces(textposition='outside')
fig1.show()

# 2️⃣ Interactive Grade Distribution
fig2 = px.pie(df, names='Grade', title='🥧 Grade Distribution (Interactive)',
              color='Grade', hole=0.3, color_discrete_sequence=px.colors.qualitative.Pastel)
fig2.show()

# 3️⃣ Interactive Gender vs Average
fig3 = px.box(df, x='Gender', y='Average', color='Gender',
              title='🧍 Gender vs Average Marks (Interactive)',
              color_discrete_sequence=px.colors.qualitative.Set3)
fig3.show()

# 4️⃣ Interactive Study Hours vs Average
fig4 = px.line(df, x='Study Hours/Week', y='Average', markers=True,
               title='📈 Study Hours vs Average Marks (Interactive)',
               color_discrete_sequence=['#FF6347'])
fig4.show()

# 5️⃣ Interactive Attendance vs Average
fig5 = px.scatter(df, x='Attendance (%)', y='Average', color='Result', size='Average',
                  title='🎯 Attendance vs Average Marks (Interactive)',
                  hover_data=['Name', 'Grade'],
                  color_discrete_sequence=['#00CC96', '#EF553B'])
fig5.show()

print("\n✅ Report generation complete with Matplotlib + Plotly visuals!")
