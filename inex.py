import os
import glob

for file in glob.glob('./backend/docs/**/*.html', recursive=True):
    file = file.replace('\\', '/')
    print(file)
    with open(f'{file}', 'r', encoding='utf-8') as f:
      html = f.read()
    html = html.replace(""":root {
			--main-bg-color: #3F4C3d;
			--main-text-color: #5F5C5D;
			--main-select-color: #5F5C5D;
			--main-second-select-color: #5F5C5D;
		}""", """:root {
			--main-bg-color: #3F4C3d;
			--main-text-color: #5F5C5D;
			--main-select-color: #5F5C5D;
			--main-second-select-color: #5F5C5D;
      --second-text-color: #5F5C5D;
		}""")
    with open(f'{file}', 'w', encoding='utf-8') as f:
      f.write(html)