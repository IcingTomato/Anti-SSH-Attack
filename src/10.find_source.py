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

# Create a cache to store already looked up IP addresses
ip_cache = {}

# Iterate through IP addresses
print("Starting IP geolocation lookup...")
for i, ip in enumerate(df['IP Address']):
    # Check progress
    if i % 10 == 0:
        print(f"Processing: {i}/{len(df)}")
    
    # Only process non-NULL IP addresses
    if not pd.isna(ip) and ip != 'NULL':
        print(f"Processing IP: {ip}")
        
        # Check if this IP is already in our cache
        if ip in ip_cache:
            source = ip_cache[ip]
            df.at[i, 'Source'] = source
            print(f"Using cached result for IP {ip}: {source}")
            continue
        
        max_attempts = 2  # Initial attempt + 1 retry
        attempt = 0
        
        while attempt < max_attempts:
            try:
                # Call IP-API to get geolocation information
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
                    # Cache the result for future use
                    ip_cache[ip] = location
                    print(f"Result for IP {ip}: {location}")
                    break  # Successfully obtained data, exit retry loop
                else:
                    if attempt < max_attempts - 1:
                        print(f"Query failed for IP {ip}, retrying in 60 seconds...")
                        time.sleep(60)  # Wait 1 minute before retrying
                        attempt += 1
                    else:
                        df.at[i, 'Source'] = 'Query failed'
                        # Cache the failure result
                        ip_cache[ip] = 'Query failed'
                        print(f"Query failed for IP {ip} after retry")
            except Exception as e:
                if attempt < max_attempts - 1:
                    print(f"Error processing IP {ip}: {e}, retrying in 60 seconds...")
                    time.sleep(60)  # Wait 1 minute before retrying
                    attempt += 1
                else:
                    print(f"Error processing IP {ip} after retry: {e}")
                    df.at[i, 'Source'] = 'Query error'
                    # Cache the error result
                    ip_cache[ip] = 'Query error'
                    break
            
        # After processing the current IP, avoid too frequent API requests
        if attempt < max_attempts:  # If not exiting because retry limit reached
            time.sleep(10)

# Save results to a new CSV file - preserving all original data plus the new column
df.to_csv('result/source.csv', index=False, na_rep='NULL')
print(f"Done! Results saved to 'result/source.csv'")