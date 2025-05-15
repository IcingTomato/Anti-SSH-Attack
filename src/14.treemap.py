import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# Read CSV file - changed to source.csv
csv_path = os.path.join('result', 'source.csv')
df = pd.read_csv(csv_path)

# Keep needed columns, including Source column
df = df[['Date', 'Time', 'IP Address', 'Username', 'Scenario', 'Source']]

# Solve datetime parsing issues
try:
    df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], format="%Y-%m-%d %H:%M:%S")
except:
    # If format doesn't match, fall back to automatic detection
    df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], errors='coerce')

df['DateOnly'] = df['DateTime'].dt.date

# Use static treemap
# Add Source column to grouping
counts = df.groupby(['IP Address', 'Source', 'Scenario', 'Username']).size().reset_index(name='Count')

# Create static treemap, add Source to path
fig = px.treemap(
    counts,
    path=['IP Address', 'Source', 'Scenario', 'Username'],  # Modified hierarchy, added Source
    values='Count',
    color='Scenario',
    title='Analysis of SSH Attack Attempts',
    hover_data=['Count']
)

# Optimize layout
fig.update_layout(
    autosize=True,
    margin=dict(t=50, l=25, r=25, b=25)
)

# Save as HTML file for interactive browsing
output_file = "img/ssh_attacks_treemap.html"
fig.write_html(output_file)
print(f"Visualization file generated: {output_file}")

# Display chart
fig.show()

# If you want to view different visualizations by date, you can add this code
# Create multiple HTML files filtered by date
import plotly.io as pio

for date in df['DateOnly'].unique():
    date_str = str(date)
    daily_df = df[df['DateOnly'] == date]
    
    # Calculate daily statistics
    # Add Source column to grouping
    daily_counts = daily_df.groupby(['IP Address', 'Source', 'Scenario', 'Username']).size().reset_index(name='Count')
    
    # Skip dates with no data
    if len(daily_counts) == 0:
        continue
    
    # Create daily treemap, add Source to path
    daily_fig = px.treemap(
        daily_counts,
        path=['IP Address', 'Source', 'Scenario', 'Username'],  # Modified hierarchy, added Source
        values='Count',
        color='Scenario',
        title=f'SSH Attack Attempts on {date_str}',
        hover_data=['Count']
    )
    
    daily_fig.update_layout(
        autosize=True,
        margin=dict(t=50, l=25, r=25, b=25)
    )
    