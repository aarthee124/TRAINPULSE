from pathlib import Path
p = Path('static/style.css')
text = p.read_text(encoding='utf-8-sig')
start = text.find('h1 {')
end = text.find('label {', start)
print(text[start:end])
