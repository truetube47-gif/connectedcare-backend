import zipfile
import xml.etree.ElementTree as ET

try:
    zf = zipfile.ZipFile('drugs.xlsx')
    
    # Read shared strings
    shared_strings = zf.read('xl/sharedStrings.xml').decode('utf-8')
    root = ET.fromstring(shared_strings)
    
    ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    
    # Extract all shared strings
    strings = []
    for si in root.findall('.//main:si', ns):
        t = si.find('.//main:t', ns)
        if t is not None:
            strings.append(t.text if t.text else '')
        else:
            strings.append('')
    
    print(f'Found {len(strings)} shared strings')
    print('First 20 strings:')
    for i, s in enumerate(strings[:20]):
        print(f'{i+1}: "{s}"')
        
    # Check if these look like our column headers
    expected_headers = ['Trade Name', 'Price', 'Strength', 'Dosage Form', 'Manufacturer', 'Pack Size', 'Composition']
    found_headers = [s for s in strings if s in expected_headers]
    print(f'\nFound expected headers: {found_headers}')
    
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
