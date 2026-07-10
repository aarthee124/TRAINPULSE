import os
import shutil
src = r'D:\TRAINPULSE\static\style_new.css'
dst = r'D:\TRAINPULSE\static\style.css'
try:
    shutil.copy(src, dst)
    print('✓ CSS updated with #c9213a headings')
except Exception as e:
    print(f'Error: {e}')
    os.remove(dst) if os.path.exists(dst) else None
    shutil.copy(src, dst)
    print('✓ CSS replaced successfully')
