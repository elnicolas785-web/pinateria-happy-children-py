import os
import re
from bs4 import BeautifulSoup, Comment

def migrate_html_file(filepath):
    print(f"Migrating {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Pre-process some thymeleaf expressions with regex before BS4 due to non-standard attributes
    # Convert th:href="@{/path}" -> href="{{ url_for('static', filename='path') }}" if it ends in css/js/png/jpg
    html = re.sub(r'th:href="@\{/(.*?)\.css\}"', r'href="{{ url_for(\'static\', filename=\'\1.css\') }}"', html)
    html = re.sub(r'th:src="@\{/(.*?(\.png|\.jpg|\.jpeg|\.gif|\.js))\}"', r'src="{{ url_for(\'static\', filename=\'\1\') }}"', html)
    
    # Generic th:href for routes
    html = re.sub(r'th:href="@\{/(.*?)\}"', r'href="/\1"', html)

    # th:text="${user.name}" -> replace tag content
    # For BS4, doing it directly on the soup is cleaner.
    
    soup = BeautifulSoup(html, 'html.parser')

    # Convert th:text
    for tag in soup.find_all(attrs={"th:text": True}):
        expr = tag['th:text'].replace('${', '').replace('}', '')
        tag.string = f'{{{{ {expr} }}}}'
        del tag['th:text']

    # Convert th:value
    for tag in soup.find_all(attrs={"th:value": True}):
        expr = tag['th:value'].replace('${', '').replace('}', '')
        tag['value'] = f'{{{{ {expr} }}}}'
        del tag['th:value']
        
    # Convert th:each
    for tag in soup.find_all(attrs={"th:each": True}):
        each_expr = tag['th:each'] # e.g. "prod : ${productos}"
        parts = each_expr.split(':')
        if len(parts) == 2:
            item = parts[0].strip()
            collection = parts[1].replace('${', '').replace('}', '').strip()
            # Insert before tag
            tag.insert_before(f'{{% for {item} in {collection} %}}')
            # Insert after tag
            tag.insert_after('{% endfor %}')
        del tag['th:each']
        
    # Convert th:if
    for tag in soup.find_all(attrs={"th:if": True}):
        if_expr = tag['th:if'].replace('${', '').replace('}', '')
        tag.insert_before(f'{{% if {if_expr} %}}')
        tag.insert_after('{% endif %}')
        del tag['th:if']
        
    # Security/CSRF th:action
    for tag in soup.find_all(attrs={"th:action": True}):
        action_expr = tag['th:action'].replace('@{', '').replace('}', '')
        tag['action'] = action_expr
        del tag['th:action']

    with open(filepath, 'w', encoding='utf-8') as f:
        # Avoid escaping Jinja tags
        result = str(soup)
        result = result.replace('&lt;%', '{%').replace('%&gt;', '%}')
        result = result.replace('&lt;{', '{{').replace('}&gt;', '}}')
        f.write(result)

if __name__ == '__main__':
    template_dir = 'templates'
    if not os.path.exists(template_dir):
        print("Template directory not found!")
    else:
        for root, dirs, files in os.walk(template_dir):
            for file in files:
                if file.endswith('.html'):
                    migrate_html_file(os.path.join(root, file))
        print("Migration complete.")
