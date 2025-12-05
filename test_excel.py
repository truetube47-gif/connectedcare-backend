import pandas as pd
print('Testing different methods to read drugs.xlsx...')

# Method 1: Try openpyxl with different options
try:
    df = pd.read_excel('drugs.xlsx', engine='openpyxl')
    print(f"openpyxl success: {len(df)} rows")
    print("Columns:", df.columns.tolist())
    print("First 3 rows:")
    print(df.head(3))
except Exception as e:
    print(f"openpyxl failed: {e}")

# Method 2: Try with xlrd (for xls files)
try:
    df = pd.read_excel('drugs.xlsx', engine='xlrd')
    print(f"xlrd success: {len(df)} rows")
except Exception as e:
    print(f"xlrd failed: {e}")

# Method 3: Try reading as CSV with different encodings
encodings = ['utf-8', 'latin1', 'cp1252', 'iso-8859-1']
for enc in encodings:
    try:
        df = pd.read_csv('drugs.xlsx', encoding=enc)
        print(f"CSV success with {enc}: {len(df)} rows")
        print("Columns:", df.columns.tolist())
        break
    except Exception as e:
        print(f"CSV with {enc} failed: {e}")

# Method 4: Check file info
import os
print(f"File size: {os.path.getsize('drugs.xlsx')} bytes")
