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
if 'Username' not in df.columns:
    print("Error: No 'Username' column in the CSV file")
    print(f"Available columns: {df.columns.tolist()}")
    exit(1)

# Extract Username column and filter out NaN values
usernames = df['Username'].dropna().tolist()
# Convert all items to strings to ensure compatibility with wordcloud
usernames = [str(username) for username in usernames]
username_freq = Counter(usernames)

# Remove any 'nan' entries that might have slipped through
if 'nan' in username_freq:
    print("Notice: Removed 'nan' values from the data")
    del username_freq['nan']

# Also remove 'None' or empty string if present
if 'None' in username_freq:
    del username_freq['None']
if '' in username_freq:
    del username_freq['']

username_freq_dict = dict(username_freq)

# Debug information
print(f"Total unique usernames: {len(username_freq_dict)}")
print(f"Sample of data: {list(username_freq_dict.items())[:3]}")

# Check for empty dictionary
if not username_freq_dict:
    print("Error: No username data found")
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
    max_font_size=200,      # Limit maximum font size
    min_font_size=5,        # Set minimum font size
    # relative_scaling=0.7,   # Increase contrast of relative sizes
    prefer_horizontal=0.7,  # Prefer horizontal text, but not all
    margin=2,               # Reduce space between words
    colormap='jet'       # Use a different colormap from IP word cloud
).generate_from_frequencies(username_freq_dict)

# Display word cloud
plt.figure(figsize=(15, 10))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')  # Hide axes

# Save image
output_path = 'img/wordcloud_username.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
plt.close()

print(f"Word cloud successfully generated and saved to {output_path}")