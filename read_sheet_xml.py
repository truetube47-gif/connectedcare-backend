import zipfile
import xml.etree.ElementTree as ET

try:
    zf = zipfile.ZipFile('drugs.xlsx')
    
    # Read the worksheet XML
    sheet_content = zf.read('xl/worksheets/sheet1.xml').decode('utf-8')
    
    # Parse XML
    root = ET.fromstring(sheet_content)
    
    # Define namespace
    ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    
    # Find all rows
    rows = root.findall('.//main:row', ns)
    print(f'Found {len(rows)} rows')
    
    # Extract first few rows to see structure
    for i, row in enumerate(rows[:5]):
        cells = row.findall('.//main:c', ns)
        print(f'Row {i+1}: {len(cells)} cells')
        for j, cell in enumerate(cells[:3]):  # Show first 3 cells
            cell_value = cell.find('.//main:v', ns)
            if cell_value is not None:
                print(f'  Cell {j+1}: {cell_value.text}')
    
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
