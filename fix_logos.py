import os
import glob

# Directorio de plantillas
template_dir = r"j:\Desktop\pinateria- happy children\templates"
files = glob.glob(os.path.join(template_dir, "*.html"))

target1 = '="/images/logo_happychildren.jpg"'
replacement1 = '="{{ url_for(\'static\', filename=\'images/logo_happychildren.jpg\') }}"'

for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    new_content = content.replace(target1, replacement1)
    
    if new_content != content:
        with open(file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {os.path.basename(file)}")

print("Done.")
