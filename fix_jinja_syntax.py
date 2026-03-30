import os
import re

def fix_jinja_expressions(match):
    expr = match.group(0)
    
    # Replace ?. with .
    expr = expr.replace('?.', '.')
    
    # Replace null with None
    expr = re.sub(r'\bnull\b', 'None', expr)
    
    # Replace !var with not var (be careful not to hit !=)
    # Using a negative lookahead to only match ! followed by a word character
    expr = re.sub(r'!(?=[a-zA-Z_])', 'not ', expr)

    # Simplified ternary Replacement (A ? B : C) -> (B if A else C)
    # This regex is a bit simplistic and might struggle with nested ternaries
    # Let's handle the specific nested one we saw:
    # producto.id_producto != None ? (readonly ? 'Detalles del Producto' : 'Editar Producto') : 'Nuevo Producto'
    if '?' in expr and ':' in expr:
        # We will just write a custom fix for the known patterns to be safe, 
        # or use a regex for simple non-nested ternaries.
        # Known pattern:
        if "readonly ? 'Detalles" in expr:
            expr = expr.replace("(readonly ? 'Detalles del Producto' : 'Editar Producto')", "('Detalles del Producto' if readonly else 'Editar Producto')")
            expr = expr.replace("(readonly ? 'Detalles de Categoría' : 'Editar Categoría')", "('Detalles de Categoría' if readonly else 'Editar Categoría')")
            expr = expr.replace("(readonly ? 'Detalles de Empleado' : 'Editar Empleado')", "('Detalles de Empleado' if readonly else 'Editar Empleado')")
            expr = expr.replace("(readonly ? 'Detalles de Rol' : 'Editar Rol')", "('Detalles de Rol' if readonly else 'Editar Rol')")
            expr = expr.replace("(readonly ? 'Detalles de Usuario' : 'Editar Usuario')", "('Detalles de Usuario' if readonly else 'Editar Usuario')")
        
        # Then the outer ternary: A ? B : 'Nuevo...'
        expr = re.sub(r'(.*?)\s*\?\s*(.*?)\s*:\s*(\'Nuevo.*?\'|".*?")', r'\2 if \1 else \3', expr)

    return expr

def migrate_html_file(filepath):
    print(f"Fixing Jinja syntax in {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    # Find all {{ ... }} and {% ... %} and fix inside them
    html = re.sub(r'\{\{.*?\}\}', fix_jinja_expressions, html)
    html = re.sub(r'\{%.*?%\}', fix_jinja_expressions, html)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)

if __name__ == '__main__':
    template_dir = 'templates'
    if not os.path.exists(template_dir):
        print("Template directory not found!")
    else:
        for root, dirs, files in os.walk(template_dir):
            for file in files:
                if file.endswith('.html'):
                    migrate_html_file(os.path.join(root, file))
        print("Syntax fixing complete.")
