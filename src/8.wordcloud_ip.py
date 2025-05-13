import pandas as pd
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os
import numpy as np

# Ensure img directory exists
os.makedirs('img', exist_ok=True)

# Read CSV file
try:
    df = pd.read_csv('result/final.csv')
except FileNotFoundError:
    print("Error: File 'result/final.csv' not found")
    exit(1)

# Check if column name exists
if 'IP Address' not in df.columns:
    print("Error: No 'IP Address' column in the CSV file")
    print(f"Available columns: {df.columns.tolist()}")
    exit(1)

# Extract IP addresses column and filter out NaN values
ip_addresses = df['IP Address'].dropna().tolist()
# Convert all items to strings to ensure compatibility with wordcloud
ip_addresses = [str(ip) for ip in ip_addresses]
ip_freq = Counter(ip_addresses)

# Remove any 'nan' entries that might have slipped through
if 'nan' in ip_freq:
    print("Notice: Removed 'nan' values from the data")
    del ip_freq['nan']

# Also remove 'None' or empty string if present
if 'None' in ip_freq:
    del ip_freq['None']
if '' in ip_freq:
    del ip_freq['']

ip_freq_dict = dict(ip_freq)

# Debug information
print(f"Total unique IP addresses: {len(ip_freq_dict)}")
print(f"Sample of data: {list(ip_freq_dict.items())[:3]}")

# Check for empty dictionary
if not ip_freq_dict:
    print("Error: No IP address data found")
    exit(1)

# Check if font file exists
font_path = 'font/UbuntuMono-R.ttf'
if not os.path.exists(font_path):
    print(f"Error: Font file '{font_path}' not found")
    exit(1)

# Generate word cloud with adjusted parameters
wordcloud = WordCloud(
    font_path=font_path,
    width=800, 
    height=500, 
    background_color='white',
    max_words=500,
    max_font_size=200,       # Limit maximum font size
    min_font_size=5,         # Set minimum font size
    # relative_scaling=0.7,    # Increase contrast of relative sizes
    prefer_horizontal=0.6,   # Prefer horizontal text, but not all
    margin=2,                # Reduce space between words
    colormap='jet'
).generate_from_frequencies(ip_freq_dict)

# Display word cloud
plt.figure(figsize=(15, 10))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')  # Hide axes

# Save image
output_path = 'img/wordcloud_ip.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
plt.close()

print(f"Word cloud successfully generated and saved to {output_path}")