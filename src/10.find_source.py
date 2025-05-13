import pandas as pd
import requests
import time
import os

# Ensure directory exists
os.makedirs('result', exist_ok=True)

# Read CSV file
try:
    # Read CSV with all original formatting
    df = pd.read_csv('result/final.csv')
except FileNotFoundError:
    print("Error: File 'result/final.csv' not found")
    exit(1)

# Ensure IP Address column exists
if 'IP Address' not in df.columns:
    print("Error: Column 'IP Address' not found")
    exit(1)

# Add Source column without modifying existing data
df['Source'] = 'NULL'  # Default value for all rows

# Iterate through IP addresses
print("Starting IP geolocation lookup...")
for i, ip in enumerate(df['IP Address']):
    # Check progress
    if i % 10 == 0:
        print(f"Processing: {i}/{len(df)}")
    
    # Only process non-NULL IP addresses
    if not pd.isna(ip) and ip != 'NULL':
        try:
            # Call IP-API to get geolocation information
            # Using ip-api.com's free API
            url = f'http://ip-api.com/json/{ip}?fields=status,message,country,regionName,city,district,isp'
            response = requests.get(url, timeout=5)
            data = response.json()
            
            if data['status'] == 'success':
                # Build detailed geolocation information
                location_parts = []
                for field in ['country', 'regionName', 'city', 'district', 'isp']:
                    if field in data and data[field]:
                        location_parts.append(data[field])
                
                location = ', '.join(location_parts)
                df.at[i, 'Source'] = location
            else:
                df.at[i, 'Source'] = 'Query failed'
            
            # Avoid too frequent API requests (ip-api.com free version limits to 45 requests per minute)
            time.sleep(1.5)
        except Exception as e:
            print(f"Error processing IP {ip}: {e}")
            df.at[i, 'Source'] = 'Query error'

# Save results to a new CSV file - preserving all original data plus the new column
df.to_csv('result/source.csv', index=False)
print(f"Done! Results saved to 'result/source.csv'")