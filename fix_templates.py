import os
import re

def fix_html_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. param.xxx -> request.args.get('xxx')
    html = re.sub(r'param\.([a-zA-Z0-9_]+)', r"request.args.get('\1')", html)

    # 2. #lists.isEmpty(X) -> not X
    html = re.sub(r'#lists\.isEmpty\(([^)]+)\)', r"not \1", html)

    # 3. #numbers.formatDecimal(X, ...) -> X (simplificando el formato)
    html = re.sub(r'#numbers\.formatDecimal\(([^,]+)(.*?)\)', r"\1", html)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)

if __name__ == '__main__':
    for root, dirs, files in os.walk('templates'):
        for file in files:
            if file.endswith('.html'):
                fix_html_file(os.path.join(root, file))
    print("Fixed templates.")
