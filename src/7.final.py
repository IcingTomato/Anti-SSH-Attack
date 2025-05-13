import csv
import os
from pathlib import Path
from datetime import datetime

def main():
    # Ensure output directory exists
    Path("result").mkdir(exist_ok=True)
    
    result_data = []
    
    # Read result.csv and add missing columns
    with open("result/result.csv", 'r') as result_file:
        reader = csv.reader(result_file)
        headers = next(reader)
        
        # Check if Scenario and Details columns are missing
        if "Scenario" not in headers and "Details" not in headers:
            headers.extend(["Scenario", "Details"])
        
        for row in reader:
            # Add default values for Scenario and Details if they don't exist
            if len(row) == len(headers) - 2:
                row.extend(["Dictionary Attack", "NULL"])
            result_data.append(row)
    
    # Read others.csv
    with open("result/others.csv", 'r') as others_file:
        reader = csv.reader(others_file)
        others_headers = next(reader)  # Skip header row
        
        # Ensure others.csv has the same header structure
        for row in reader:
            result_data.append(row)
    
    # Sort by Date and Time
    def parse_date_time(row):
        date_str = row[1]  # Date column
        time_str = row[2]  # Time column
        
        # Parse the date (e.g., "May 11" or "May  5")
        try:
            # Handle single-digit days with extra space
            if "  " in date_str:
                month, day = date_str.split("  ")
            else:
                month, day = date_str.split(" ")
            
            # Convert month name to number
            month_num = datetime.strptime(month, "%b").month
            day_num = int(day)
            
            # Parse time
            time_obj = datetime.strptime(time_str, "%H:%M:%S")
            
            # Combine date and time (assume current year)
            return datetime(2025, month_num, day_num, 
                            time_obj.hour, time_obj.minute, time_obj.second)
        except Exception:
            # Return a default datetime for rows with invalid date/time
            return datetime(2000, 1, 1)
    
    # Sort the combined data
    sorted_data = sorted(result_data, key=parse_date_time)
    
    # Write the sorted data to final.csv
    with open("result/final.csv", 'w', newline='') as output_file:
        writer = csv.writer(output_file)
        writer.writerow(headers)
        writer.writerows(sorted_data)
    
    print(f"Merged and sorted data written to result/final.csv")

if __name__ == "__main__":
    main()