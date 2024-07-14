import os
import glob

for file in glob.glob('./backend/docs/**/*.html', recursive=True):
    file = file.replace('\\', '/')
    print(file)
    with open(f'{file}', 'r', encoding='utf-8') as f:
      html = f.read()
    html = html.replace("""</body>""", """

		<p class=MsoNormal><span lang=RU>&nbsp;</span></p>

		<p class=MsoNormal><span lang=RU>&nbsp;</span></p>

		<p class=MsoNormal><span lang=RU>&nbsp;</span></p>

		<p class=MsoNormal><span lang=RU>&nbsp;</span></p>

		<p class=MsoNormal><span lang=RU>&nbsp;</span></p>

<p class=MsoNormal><span lang=RU>&nbsp;</span></p>

<p class=MsoNormal><span lang=RU>&nbsp;</span></p>

<p class=MsoNormal><span lang=RU>&nbsp;</span></p>

<p class=MsoNormal><span lang=RU>&nbsp;</span></p>

<p class=MsoNormal><span lang=RU>&nbsp;</span></p>
</body>""")
    with open(f'{file}', 'w', encoding='utf-8') as f:
      f.write(html)