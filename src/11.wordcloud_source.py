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
    df = pd.read_csv('result/source.csv')
except FileNotFoundError:
    print("Error: File 'result/source.csv' not found")
    exit(1)

# Check if column name exists
if 'Source' not in df.columns:
    print("Error: No 'Source' column in the CSV file")
    print(f"Available columns: {df.columns.tolist()}")
    exit(1)

# Extract Source column and filter out NaN values
sources = df['Source'].dropna().tolist()
# Convert all items to strings to ensure compatibility with wordcloud
sources = [str(source) for source in sources]
source_freq = Counter(sources)

# Remove any 'nan' entries that might have slipped through
if 'nan' in source_freq:
    print("Notice: Removed 'nan' values from the data")
    del source_freq['nan']

# Also remove 'None' or empty string if present
if 'None' in source_freq:
    del source_freq['None']
if '' in source_freq:
    del source_freq['']

source_freq_dict = dict(source_freq)

# Debug information
print(f"Total unique sources: {len(source_freq_dict)}")
print(f"Sample of data: {list(source_freq_dict.items())[:3]}")

# Check for empty dictionary
if not source_freq_dict:
    print("Error: No source data found")
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
    colormap='inferno'      # Use a different colormap from other word clouds
).generate_from_frequencies(source_freq_dict)

# Display word cloud
plt.figure(figsize=(15, 10))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')  # Hide axes

# Save image
output_path = 'img/wordcloud_source.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
plt.close()

print(f"Word cloud successfully generated and saved to {output_path}")