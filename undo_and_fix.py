import os
import re

def fix_span_ternaries(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    # The corrupted pattern looks like:
    # <span>('Detalles del Producto' if readonly else 'Editar Producto') if {{ producto.id_producto != None else 'Nuevo Producto' }}</span>
    # We want:
    # <span>{{ ('Detalles del Producto' if readonly else 'Editar Producto') if producto.id_producto != None else 'Nuevo Producto' }}</span>

    # A generic regex for this specific corruption:
    pattern = r"\('Detalles(.*?)\'\s*if readonly else\s*\'Editar(.*?)\'\)\s*if\s*\{\{\s*(.*?)\s*!=\s*None\s*else\s*\'Nuevo(.*?)\'\s*\}\}"
    
    def repl(m):
        detalles_suffix = m.group(1)
        editar_suffix = m.group(2)
        condition = m.group(3)
        nuevo_suffix = m.group(4)
        return f"{{{{ ('Detalles{detalles_suffix}' if readonly else 'Editar{editar_suffix}') if {condition} != None else 'Nuevo{nuevo_suffix}' }}}}"

    html = re.sub(pattern, repl, html)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)

if __name__ == '__main__':
    template_dir = 'templates'
    if os.path.exists(template_dir):
        for root, dirs, files in os.walk(template_dir):
            for file in files:
                if file.endswith('.html'):
                    fix_span_ternaries(os.path.join(root, file))
        print("Ternary Spans fixed.")
