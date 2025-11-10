import pandas as pd
import numpy as np
from dash import Dash, html, dcc, dash_table, Input, Output, State
import plotly.express as px
import plotly.figure_factory as ff
import dash_bootstrap_components as dbc

# ===========================================
# Load and preprocess data
# ===========================================
df = pd.read_csv("students.csv")

# Ensure all required columns exist
if 'Attendance (%)' not in df.columns:
    df['Attendance (%)'] = np.random.randint(50, 100, len(df))
if 'Study Hours/Week' not in df.columns:
    df['Study Hours/Week'] = np.random.randint(1, 12, len(df))

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
df['Result'] = ['Pass' if a >= 40 else 'Fail' for a in df['Average']]

# ===========================================
# App Setup
# ===========================================
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
app.title = "🎓 Student Performance Dashboard"

# ===========================================
# KPI Card Helper
# ===========================================
def kpi_card(title, value, color):
    return dbc.Card(
        dbc.CardBody([
            html.H6(title, className="text-muted"),
            html.H3(value, className="fw-bold text-dark")
        ]),
        className=f"border-{color} shadow-sm text-center p-3 m-2 rounded-4"
    )

# ===========================================
# Layout
# ===========================================
app.layout = dbc.Container([
    # Top Bar
    dbc.NavbarSimple(
        brand="🎓 Student Performance Dashboard",
        color="primary",
        dark=True,
        className="mb-4 shadow-sm rounded-3"
    ),

    # KPI Cards
    dbc.Row([
        dbc.Col(kpi_card("Total Students", len(df), "primary"), width=2),
        dbc.Col(kpi_card("Average Marks", f"{df['Average'].mean():.2f}", "success"), width=2),
        dbc.Col(kpi_card("Pass %", f"{(df['Result'].value_counts().get('Pass',0)/len(df))*100:.1f}%", "info"), width=2),
        dbc.Col(kpi_card("Fail %", f"{(df['Result'].value_counts().get('Fail',0)/len(df))*100:.1f}%", "danger"), width=2),
        dbc.Col(kpi_card("Top Performer", df.loc[df['Average'].idxmax(), 'Name'], "warning"), width=2),
        dbc.Col(kpi_card("Most Common Grade", df['Grade'].mode()[0], "secondary"), width=2),
    ], justify="center"),

    html.Hr(),

    # Filters
    dbc.Row([
        dbc.Col([
            html.Label("🎯 Filter by Grade:"),
            dcc.Dropdown(
                options=[{'label': g, 'value': g} for g in sorted(df['Grade'].unique())],
                id='grade-filter', placeholder="Select Grade"
            )
        ], width=3),

        dbc.Col([
            html.Label("👩‍🎓 Filter by Gender:"),
            dcc.Dropdown(
                options=[{'label': g, 'value': g} for g in sorted(df['Gender'].unique())],
                id='gender-filter', placeholder="Select Gender"
            )
        ], width=3),

        dbc.Col([
            html.Button("📥 Download Filtered Data", id="download-btn", n_clicks=0, className="btn btn-outline-primary mt-4"),
            dcc.Download(id="download-dataframe-csv")
        ], width=3),
    ], className="my-3"),

    html.Hr(),

    # Charts Grid
    dbc.Row([
        dbc.Col(dcc.Graph(id="subject-bar"), width=6),
        dbc.Col(dcc.Graph(id="grade-pie"), width=6),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id="gender-bar"), width=6),
        dbc.Col(dcc.Graph(id="attendance-scatter"), width=6),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id="heatmap"), width=6),
        dbc.Col(dcc.Graph(id="average-trend"), width=6),
    ]),

    html.Hr(),

    html.H4("🏆 Top 5 Students", className="text-center mt-4 text-success fw-bold"),

    dash_table.DataTable(
        id='top5-table',
        columns=[{"name": i, "id": i} for i in ["Name", "Gender", "Average", "Grade"]],
        style_header={'backgroundColor': '#198754', 'color': 'white', 'fontWeight': 'bold', 'textAlign': 'center'},
        style_cell={'textAlign': 'center', 'padding': '8px'},
        style_data={'backgroundColor': '#f9f9f9'},
        style_data_conditional=[
            {'if': {'row_index': 'odd'}, 'backgroundColor': '#f2f2f2'},
            {'if': {'column_id': 'Grade'}, 'fontWeight': 'bold'},
        ],
    ),

    html.Hr(),
    html.H4("📋 Interactive Student Data Table", className="mt-4 mb-3 text-primary text-center fw-bold"),

    dash_table.DataTable(
        id='data-table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records'),
        filter_action="native",
        sort_action="native",
        page_size=10,
        style_table={'overflowX': 'auto', 'borderRadius': '10px'},
        style_header={'backgroundColor': '#0d6efd', 'color': 'white', 'fontWeight': 'bold'},
        style_cell={'textAlign': 'center', 'padding': '8px'},
        style_data_conditional=[
            {'if': {'filter_query': '{Result} = "Fail"'}, 'backgroundColor': '#ffcccc'},
            {'if': {'row_index': 'odd'}, 'backgroundColor': '#f8f9fa'}
        ],
    ),

    html.Footer("© 2025 Student Analytics Dashboard | Educational Insights", 
                className="text-center mt-5 mb-2 text-muted")
], fluid=True)

# ===========================================
# Callbacks
# ===========================================
@app.callback(
    [
        Output('subject-bar', 'figure'),
        Output('grade-pie', 'figure'),
        Output('gender-bar', 'figure'),
        Output('attendance-scatter', 'figure'),
        Output('heatmap', 'figure'),
        Output('average-trend', 'figure'),
        Output('top5-table', 'data'),
        Output('data-table', 'data')
    ],
    [Input('grade-filter', 'value'),
     Input('gender-filter', 'value')]
)
def update_dashboard(selected_grade, selected_gender):
    dff = df.copy()
    if selected_grade:
        dff = dff[dff['Grade'] == selected_grade]
    if selected_gender:
        dff = dff[dff['Gender'] == selected_gender]

    # Charts
    subject_avg = dff[['Maths', 'Science', 'English', 'History']].mean().reset_index()
    subject_avg.columns = ['Subject', 'Average']
    fig1 = px.bar(subject_avg, x='Subject', y='Average', color='Subject', title='📚 Subject-wise Average Marks')

    fig2 = px.pie(dff, names='Grade', title='🎯 Grade Distribution', 
                  color_discrete_sequence=px.colors.qualitative.Pastel)

    fig3 = px.bar(dff.groupby('Gender')['Average'].mean().reset_index(),
                  x='Gender', y='Average', color='Gender', title='👩‍🎓 Gender-wise Average Comparison')

    fig4 = px.scatter(dff, x='Attendance (%)', y='Average', color='Result',
                      size='Study Hours/Week', title='📈 Attendance vs Average Marks')

    corr = dff[['Maths', 'Science', 'English', 'History', 'Average']].corr()
    fig5 = px.imshow(corr, text_auto=True, title='🔥 Subject Correlation Heatmap', color_continuous_scale='Blues')

    sorted_avg = dff.sort_values('Average')
    fig6 = px.line(sorted_avg, x='Name', y='Average', title='📊 Average Marks Trend by Student',
                   markers=True)
    fig6.update_xaxes(showticklabels=False)

    top5 = dff.sort_values('Average', ascending=False).head(5)
    return fig1, fig2, fig3, fig4, fig5, fig6, top5.to_dict('records'), dff.to_dict('records')

# Download CSV
@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("download-btn", "n_clicks"),
    State('grade-filter', 'value'),
    State('gender-filter', 'value'),
    prevent_initial_call=True,
)
def download_filtered_data(n_clicks, selected_grade, selected_gender):
    dff = df.copy()
    if selected_grade:
        dff = dff[dff['Grade'] == selected_grade]
    if selected_gender:
        dff = dff[dff['Gender'] == selected_gender]
    return dcc.send_data_frame(dff.to_csv, "filtered_students.csv")

# ===========================================
# Run App
# ===========================================
if __name__ == "__main__":
    app.run(debug=True)
