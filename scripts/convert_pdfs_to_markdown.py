#!/usr/bin/env python3
"""
Script para convertir PDFs a Markdown
Convierte la documentación PDF a formato Markdown más liviano
"""

import os
import pdfplumber
import re
from pathlib import Path

def clean_text(text):
    """Limpia y formatea el texto extraído del PDF"""
    if not text:
        return ""

    # Reemplazar múltiples espacios con uno solo
    text = re.sub(r'\s+', ' ', text)

    # Reemplazar líneas vacías múltiples
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)

    # Detectar posibles títulos (texto en mayúsculas seguido de contenido)
    lines = text.split('\n')
    formatted_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            formatted_lines.append('')
            continue

        # Si la línea está en mayúsculas y es corta, probablemente es un título
        if len(line) < 100 and line.isupper() and len(line.split()) > 1:
            formatted_lines.append(f'# {line.title()}')
        elif len(line) < 80 and line[0].isupper() and not line.endswith('.'):
            # Posible subtítulo
            formatted_lines.append(f'## {line}')
        else:
            formatted_lines.append(line)

    return '\n'.join(formatted_lines)

def pdf_to_markdown(pdf_path, output_path):
    """Convierte un PDF a Markdown"""
    print(f"Convirtiendo {pdf_path} -> {output_path}")

    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = []

            for page_num, page in enumerate(pdf.pages, 1):
                print(f"  Procesando página {page_num}/{len(pdf.pages)}")

                # Extraer texto de la página
                text = page.extract_text()
                if text:
                    # Agregar encabezado de página
                    full_text.append(f'## Página {page_num}\n')
                    full_text.append(clean_text(text))
                    full_text.append('\n---\n')

            # Unir todo el texto
            markdown_content = '\n'.join(full_text)

            # Agregar encabezado del documento
            filename = Path(pdf_path).stem
            header = f'# {filename.replace("_", " ").title()}\n\n'
            header += f'*Convertido desde: {Path(pdf_path).name}*\n\n'
            header += f'*Fecha de conversión: {os.popen("date").read().strip()}*\n\n'
            header += '---\n\n'

            final_content = header + markdown_content

            # Guardar el archivo Markdown
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(final_content)

            print(f"✓ Convertido exitosamente: {output_path}")

    except Exception as e:
        print(f"✗ Error convirtiendo {pdf_path}: {str(e)}")
        return False

    return True

def main():
    """Función principal"""
    assets_dir = Path('assets')
    docs_dir = Path('docs')

    # Crear directorio docs si no existe
    docs_dir.mkdir(exist_ok=True)

    # PDFs a convertir
    pdfs = [
        'BC292382016572en-000201.pdf',
        'EMISOR IK3.pdf',
        'Manual Gama TM70 Pupitre.pdf',
        'RECEPTOR R13 F.pdf'
    ]

    converted_count = 0

    for pdf_name in pdfs:
        pdf_path = assets_dir / pdf_name
        md_name = pdf_name.replace('.pdf', '.md')
        md_path = docs_dir / md_name

        if pdf_path.exists():
            if pdf_to_markdown(str(pdf_path), str(md_path)):
                converted_count += 1
        else:
            print(f"⚠ PDF no encontrado: {pdf_path}")

    print(f"\n{'='*50}")
    print(f"Conversión completada: {converted_count}/{len(pdfs)} PDFs convertidos")
    print(f"Los archivos Markdown están en: {docs_dir}/")
    print(f"{'='*50}")

if __name__ == '__main__':
    main()