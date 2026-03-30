import os
import re

def fix_html_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. {{ #authentication.principal.username }} -> {{ current_user.nombre_usuario if current_user.is_authenticated else '' }}
    html = re.sub(r'\{\{\s*#authentication\.principal\.username\s*\}\}', r"{{ current_user.nombre_usuario if current_user.is_authenticated else '' }}", html)

    # 2. {{ #authentication.principal.authorities[0].authority }} -> {{ current_user.rol.nombre_rol if current_user.is_authenticated else '' }}
    html = re.sub(r'\{\{\s*#authentication\.principal\.authorities\[0\]\.authority\s*\}\}', r"{{ current_user.rol.nombre_rol if current_user.is_authenticated else '' }}", html)

    # 3. Any other {{ #... }}
    html = re.sub(r'\{\{\s*#(.*?)\s*\}\}', r"{{ \1 }}", html)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)

if __name__ == '__main__':
    for root, dirs, files in os.walk('templates'):
        for file in files:
            if file.endswith('.html'):
                fix_html_file(os.path.join(root, file))
    print("Fixed authentication expressions.")
