from pathlib import Path
p = Path('static/style.css')
text = p.read_text(encoding='utf-8-sig')
old = '''.status-grid {
    display: grid;
    gap: 14px;
    margin-top: 18px;
}

.status-card {
    display: grid;
    grid-template-columns: 1fr auto;
    align-items: center;
    gap: 12px;
    padding: 18px 20px;
    border-radius: 20px;
    border: 1px solid rgba(239, 68, 68, 0.28);
    background: rgba(255, 255, 255, 0.06);
}

.status-card strong {
    color: #ffffff;
    text-align: right;
    font-size: 15px;
}
'''
new = '''.status-grid {
    display: grid;
    gap: 10px;
    margin-top: 14px;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}

.status-card {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 10px;
    padding: 10px 14px;
    min-height: 46px;
    border-radius: 18px;
    border: 1px solid rgba(239, 68, 68, 0.28);
    background: rgba(255, 255, 255, 0.06);
}

.status-card span {
    font-size: 13px;
    color: #e4cac9;
}

.status-card strong {
    color: #ffffff;
    text-align: right;
    font-size: 14px;
    white-space: nowrap;
}
'''
if old not in text:
    raise SystemExit('old block not found')
text = text.replace(old, new)
p.write_text(text, encoding='utf-8')
print('patched')
