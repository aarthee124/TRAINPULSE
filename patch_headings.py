from pathlib import Path
p = Path('static/style.css')
text = p.read_text(encoding='utf-8-sig')
old = '''h1 {
    color: #ffc9c9;
    font-size: 34px;
    margin-bottom: 10px;
}

.subtitle {
    color: #d6c2c2;
    line-height: 1.6;
    max-width: 540px;
}

.card,
.card-info,
.card-blue,
.section-card,
.history-card {
    background: rgba(30, 10, 10, 0.96);
    border-radius: 24px;
    padding: 22px;
    margin-bottom: 18px;
    border: 1px solid rgba(205, 92, 92, 0.18);
}

.card-form {
    padding: 26px;
}

.card-blue {
    background: linear-gradient(135deg, rgba(135, 35, 35, 0.96), rgba(190, 45, 45, 0.94));
    border-color: rgba(239, 68, 68, 0.30);
}

.card-blue h3,
.section-title,
.card h3 {
    margin-bottom: 16px;
    font-size: 18px;
    color: #ffffff;
}
'''
new = '''h1 {
    color: #ffdcdc;
    font-size: 34px;
    margin-bottom: 10px;
}

h2,
h3,
.section-title,
.card h3,
.card-blue h3 {
    color: #ffe8e8;
}

.subtitle {
    color: #f2d4d4;
    line-height: 1.6;
    max-width: 540px;
}

.card,
.card-info,
.card-blue,
.section-card,
.history-card {
    background: rgba(30, 10, 10, 0.96);
    border-radius: 24px;
    padding: 22px;
    margin-bottom: 18px;
    border: 1px solid rgba(205, 92, 92, 0.18);
}

.card-form {
    padding: 26px;
}

.card-blue {
    background: linear-gradient(135deg, rgba(135, 35, 35, 0.96), rgba(190, 45, 45, 0.94));
    border-color: rgba(239, 68, 68, 0.30);
}

.card-blue h3,
.section-title,
.card h3 {
    margin-bottom: 16px;
    font-size: 18px;
    color: #ffe8e8;
}
'''
if old not in text:
    raise SystemExit('old block not found')
text = text.replace(old, new)
p.write_text(text, encoding='utf-8')
print('patched headings')
