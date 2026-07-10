#!/usr/bin/env python3
import os
os.chdir(r'D:\TRAINPULSE')
with open(r'D:\TRAINPULSE\static\style.css', 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace('color: #ffc9c9;', 'color: #c9213a;')
content = content.replace('color: #ffffff;', 'color: #c9213a;')
with open(r'D:\TRAINPULSE\static\style.css', 'w', encoding='utf-8') as f:
    f.write(content)
print('✓ Heading colors updated to #c9213a')
