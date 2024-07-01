import os
import glob

for file in glob.glob('./backend/docs/**/*.html', recursive=True):
    file = file.replace('\\', '/')
    print(file)
    with open(f'{file}', 'r', encoding='utf-8') as f:
      html = f.read()
    html = html.replace("""mark { background-color: yellow !important; } mark.current { background-color: green !important; }""", 
                        """mark { background-color: var(--main-second-select-color) !important; } mark.current { background-color: var(--main-select-color) !important; }""")
    with open(f'{file}', 'w', encoding='utf-8') as f:
      f.write(html)