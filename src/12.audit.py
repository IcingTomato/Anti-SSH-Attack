import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import traceback
from matplotlib.font_manager import FontProperties
from mpl_toolkits.mplot3d import Axes3D
from datetime import datetime

# Set font
font_path = 'font/UbuntuMono-R.ttf'
if not os.path.exists(font_path):
    print(f"Warning: Font file '{font_path}' not found, will use default font")
    custom_font = FontProperties()
else:
    custom_font = FontProperties(fname=font_path)

# Read CSV file
csv_path = 'result/final.csv'
try:
    df = pd.read_csv(csv_path)
    print(f"Successfully read file: {csv_path}")
    print(f"File contains {len(df)} rows")
except FileNotFoundError:
    print(f"Error: File '{csv_path}' not found")
    exit(1)

# Check if required columns exist
if 'Date' not in df.columns or 'Time' not in df.columns:
    print("Error: Required columns 'Date' or 'Time' not found in the CSV file")
    exit(1)

try:
    # Process Date column
    current_year = datetime.now().year
    df['cleaned_date'] = df['Date'].str.strip()
    df['complete_date'] = df['cleaned_date'] + f", {current_year}"
    df['parsed_date'] = pd.to_datetime(df['complete_date'], format="%b %d, %Y", errors='coerce')
    print(f"Parsing dates with format: %b %d, %Y")
    
    # Check valid dates
    valid_dates = df['parsed_date'].notna().sum()
    print(f"Successfully parsed {valid_dates} dates (out of {len(df)} records)")
    if valid_dates == 0:
        print(f"Warning: Unable to parse dates. Sample value: {df['Date'].iloc[0]}")
        exit(1)
    
    # Extract date part only
    df['date_only'] = df['parsed_date'].dt.date
    
    # Process Time column
    df['parsed_time'] = pd.to_datetime(df['Time'], format='%H:%M:%S', errors='coerce')
    
    # Check valid times
    valid_times = df['parsed_time'].notna().sum()
    print(f"Successfully parsed {valid_times} times (out of {len(df)} records)")
    if valid_times == 0:
        print(f"Warning: Unable to parse times. Sample value: {df['Time'].iloc[0]}")
        exit(1)
    
    # Extract hour from time
    df['hour'] = df['parsed_time'].dt.hour
    
    # Group hours into 4-hour intervals (0-4, 4-8, 8-12, etc.)
    df['hour_interval'] = (df['hour'] // 4) * 4
    df['time_group'] = df['hour_interval'].apply(lambda x: f"{x:02d}-{(x+4):02d}")
    
    # Group by date and time interval
    grouped = df.groupby(['date_only', 'time_group']).size().reset_index(name='count')
    
    # Create a complete grid with all date-time combinations
    # Get unique dates and time intervals
    unique_dates = sorted(df['date_only'].unique())
    unique_time_groups = sorted([f"{h:02d}-{(h+4):02d}" for h in range(0, 24, 4)])
    
    # Create complete grid
    date_grid, time_grid = np.meshgrid(np.arange(len(unique_dates)), np.arange(len(unique_time_groups)))
    
    # Create 3D chart
    fig = plt.figure(figsize=(16, 12))
    ax = fig.add_subplot(111, projection='3d')
    
    # Create a mapping from date to index
    date_to_idx = {date: i for i, date in enumerate(unique_dates)}
    
    # Create a mapping from time group to index
    time_to_idx = {time: i for i, time in enumerate(unique_time_groups)}
    
    # Prepare the 3D data
    x_data = []
    y_data = []
    z_data = []
    
    # For each date-time combination, get the count
    for _, row in grouped.iterrows():
        date_idx = date_to_idx[row['date_only']]
        time_idx = time_to_idx[row['time_group']] if row['time_group'] in time_to_idx else 0
        count = row['count']
        
        x_data.append(date_idx)
        y_data.append(time_idx)
        z_data.append(count)
    
    # Add zero counts for missing combinations
    for date_idx, date in enumerate(unique_dates):
        for time_idx, time_group in enumerate(unique_time_groups):
            # Check if this combination already exists in our data
            combination_exists = False
            for i in range(len(x_data)):
                if x_data[i] == date_idx and y_data[i] == time_idx:
                    combination_exists = True
                    break
            
            if not combination_exists:
                x_data.append(date_idx)
                y_data.append(time_idx)
                z_data.append(0)
    
    x_data = np.array(x_data)
    y_data = np.array(y_data)
    z_data = np.array(z_data)
    
    # Bar width and depth
    dx = np.ones_like(z_data) * 0.7
    dy = np.ones_like(z_data) * 0.7
    
    # Set color gradient based on height (count)
    max_count = max(z_data) if z_data.size > 0 and max(z_data) > 0 else 1
    colors = plt.cm.plasma(z_data / max_count)
    
    # Create 3D bars
    bars = ax.bar3d(x_data, y_data, np.zeros_like(z_data), dx, dy, z_data, color=colors, shade=True, alpha=0.9)
    
    # Find top 5 values and add labels
    if len(z_data) > 0:
        # Get indices of top 5 values
        top_indices = np.argsort(z_data)[-5:]
        
        # Add text labels above the top 5 bars
        for idx in top_indices:
            if z_data[idx] > 0:  # Only label bars with actual data
                x_pos = x_data[idx] + dx[idx] / 2
                y_pos = y_data[idx] + dy[idx] / 2
                z_pos = z_data[idx]
                
                # Get date and time for this data point
                date_val = unique_dates[int(x_data[idx])]
                time_val = unique_time_groups[int(y_data[idx])]
                
                # Create label text
                label_text = f"{int(z_data[idx])}"
                
                # Add 3D text with white background
                ax.text(x_pos, y_pos, z_pos + max_count * 0.03, label_text, 
                       color='black', fontsize=10, fontweight='bold', 
                       ha='center', va='bottom', fontproperties=custom_font,
                       bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=2))
    
    # Set labels and title
    date_labels = [date.strftime('%b\n%d') for date in unique_dates]
    
    ax.set_xlabel('Date', fontproperties=custom_font, labelpad=10)
    ax.set_ylabel('Time Interval (Hours)', fontproperties=custom_font, labelpad=10)
    ax.set_zlabel('Attack Count', fontproperties=custom_font, labelpad=10)
    ax.set_title('SSH Attack Distribution by Date and Time', fontproperties=custom_font, pad=20, fontsize=16)
    
    # Set axis ticks and labels
    # X-axis (dates)
    if len(date_labels) > 10:
        step = max(1, len(date_labels) // 10)
        x_ticks = np.arange(0, len(date_labels), step)
        x_labels = [date_labels[i] for i in range(0, len(date_labels), step)]
    else:
        x_ticks = np.arange(len(date_labels))
        x_labels = date_labels
    
    ax.set_xticks(x_ticks)
    ax.set_xticklabels(x_labels, rotation=0, ha='center', fontproperties=custom_font)
    
    # Y-axis (time intervals)
    ax.set_yticks(np.arange(len(unique_time_groups)))
    ax.set_yticklabels(unique_time_groups, fontproperties=custom_font)
    
    # Add color bar
    cbar = fig.colorbar(plt.cm.ScalarMappable(cmap=plt.cm.plasma), ax=ax)
    cbar.set_label('Attack Frequency', rotation=270, labelpad=20, fontproperties=custom_font)
    
    # Set tick font
    for label in ax.get_xticklabels() + ax.get_yticklabels() + ax.get_zticklabels():
        label.set_fontproperties(custom_font)
    
    # Adjust view angle for better visibility
    ax.view_init(elev=35, azim=215)
    
    # Add grid lines
    ax.grid(True)
    
    # Save image and display
    plt.tight_layout()
    output_file = 'img/datetime_audit.png'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"3D histogram generated and saved as '{output_file}'")
    plt.show()
    
except Exception as e:
    print(f"Error processing data or generating chart: {e}")
    traceback.print_exc()