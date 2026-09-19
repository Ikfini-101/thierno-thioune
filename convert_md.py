import os
import re

src_dir = "Bibliographie"
dest_dir = "src/content/publications"
os.makedirs(dest_dir, exist_ok=True)

files = [f for f in os.listdir(src_dir) if f.endswith('.md') and f != '00_index.md' and f != '00_rapport_telechargement.md']

for filename in files:
    with open(os.path.join(src_dir, filename), 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract title
    title_m = re.search(r'^# (.*)$', content, re.MULTILINE)
    title = title_m.group(1).strip().replace('"', '\\"') if title_m else ''
    
    # Extract year
    year_m = re.search(r'\*\*Année :\*\*\s*(.*)$', content, re.MULTILINE)
    year = year_m.group(1).strip() if year_m else ''

    # Extract authors
    authors_m = re.search(r'\*\*Auteurs :\*\*\s*(.*)$', content, re.MULTILINE)
    authors = authors_m.group(1).strip().replace('"', '\\"') if authors_m else ''
    
    # Extract journal
    journal_m = re.search(r'\*\*Revue / Support :\*\*\s*(.*)$', content, re.MULTILINE)
    journal = journal_m.group(1).strip().replace('"', '\\"') if journal_m else ''

    # Extract vol
    vol_m = re.search(r'\*\*Volume / Numéro / Pages :\*\*\s*(.*)$', content, re.MULTILINE)
    vol = vol_m.group(1).strip().replace('"', '\\"') if vol_m else ''

    # Extract cites
    cites_m = re.search(r'\*\*Citations \(Google Scholar\) :\*\*\s*(.*)$', content, re.MULTILINE)
    cites = cites_m.group(1).strip() if cites_m else '0'

    # Extract link
    link_m = re.search(r'\*\*Lien / DOI :\*\*\s*(.*)$', content, re.MULTILINE)
    link = link_m.group(1).strip() if link_m else ''
    
    # Extract abstract
    abstract_m = re.search(r'## Résumé\s+(.*?)\s+## Thématique', content, re.DOTALL)
    abstract = abstract_m.group(1).strip() if abstract_m else ''

    # Extract theme
    theme_m = re.search(r'## Thématique\s+(.*?)\s+## Référence', content, re.DOTALL)
    theme = theme_m.group(1).strip() if theme_m else ''
    
    # Extract PDF if available
    pdf_path = f"/PDFs/{filename.replace('.md', '.pdf')}"
    has_pdf = os.path.exists(os.path.join("PDFs", filename.replace('.md', '.pdf')))
    pdf_field = f'pdf: "{pdf_path}"' if has_pdf else 'pdf: null'
    
    # Create frontmatter
    frontmatter = f"""---
title: "{title}"
year: {year if year.isdigit() else 0}
authors: "{authors}"
journal: "{journal}"
volume: "{vol}"
citations: {cites}
link: "{link}"
theme: "{theme}"
{pdf_field}
---
"""
    
    with open(os.path.join(dest_dir, filename), 'w', encoding='utf-8') as f:
        f.write(frontmatter + "\n" + abstract)
        
print("Conversion completed.")
