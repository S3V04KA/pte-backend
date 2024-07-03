import os
import glob

for file in glob.glob('./backend/docs/**/*.html', recursive=True):
    file = file.replace('\\', '/')
    print(file)
    with open(f'{file}', 'r', encoding='utf-8') as f:
      html = f.read()
    html = html.replace("""src="images/""", """src="/images/""")
    with open(f'{file}', 'w', encoding='utf-8') as f:
      f.write(html)