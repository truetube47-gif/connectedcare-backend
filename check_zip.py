import zipfile
import zipfile

try:
    zf = zipfile.ZipFile('drugs.xlsx')
    print('Files in archive:')
    for f in zf.namelist():
        print(f)
    
    # Try to read workbook.xml
    try:
        content = zf.read('xl/workbook.xml').decode('utf-8')
        print('Workbook XML content (first 500 chars):')
        print(content[:500])
    except Exception as e:
        print(f'Error reading workbook.xml: {e}')
        
except Exception as e:
    print(f'Error opening zip: {e}')
