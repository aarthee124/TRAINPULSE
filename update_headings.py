from pathlib import Path
p = Path('static/style.css')
text = p.read_text(encoding='utf-8')

# Replace h1 color
text = text.replace('    color: #ffc9c9;', '    color: #c9213a;')

# Replace card heading colors (the #ffffff that appears in the .card-blue h3 block)
# More specific replacement to avoid changing other whites
old_h3 = '''    margin-bottom: 16px;
    font-size: 18px;
    color: #ffffff;'''
new_h3 = '''    margin-bottom: 16px;
    font-size: 18px;
    color: #c9213a;'''
text = text.replace(old_h3, new_h3)

p.write_text(text, encoding='utf-8')
print('✓ Headings updated to #c9213a')
