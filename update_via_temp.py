#!/usr/bin/env python3
import shutil
import tempfile

src = r'D:\TRAINPULSE\static\style.css'
with open(src, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('color: #ffc9c9;', 'color: #c9213a;')
content = content.replace('color: #ffffff;', 'color: #c9213a;')

# Write to temp file first
with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, dir=r'D:\TRAINPULSE\static') as tmp:
    tmp.write(content)
    tmp_name = tmp.name

# Replace original with temp
shutil.move(tmp_name, src, copy_function=shutil.copy2)
print('✓ Heading colors updated to #c9213a')
