#!/usr/bin/env python3
import os
with open(r'D:\TRAINPULSE\static\style.css', 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace('color: #ffc9c9;', 'color: #c9213a;')
content = content.replace('color: #ffffff;', 'color: #c9213a;')
with open(r'D:\TRAINPULSE\static\style_new.css', 'w', encoding='utf-8') as f:
    f.write(content)
print('Created style_new.css')
