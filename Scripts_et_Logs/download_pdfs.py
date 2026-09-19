import requests
import json
import time
import os
import re
from urllib.parse import quote

# Re-use our XRD protocol from before to be consistent
import datetime
def log_xrd(task, level, p, e, i, v, action, result, soldier='S9', rollback=False):
    c_norm = (p * (1+e) * (1+i) * (1+v)) / 8.0
    entry = {
        'ts': datetime.datetime.now().isoformat(),
        'id': 'T1',
        'task': task,
        'level': level,
        'P': p, 'E': e, 'I': i, 'V': v, 'C_norm': c_norm,
        'zone': 'GREEN' if c_norm < 0.3 else 'UNGREEN',
        'action': action,
        'result': result,
        'soldier': soldier,
        'rollback': rollback
    }
    with open('xorondom_scores.ljson', 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry) + '\n')

log_xrd('PDF download process', 'L0', 0.1, 0.1, 0.1, 0.1, 'Init', 'Start')

bib_dir = "Bibliographie"
pdf_dir = "PDFs"
os.makedirs(pdf_dir, exist_ok=True)

report = "# Rapport de Téléchargement des Articles\n\n"
report += "| Fichier | Statut | Lien PDF |\n|---|---|---|\n"

headers = {
    'User-Agent': 'mailto:test@example.com' # Polite pool
}

files = [f for f in os.listdir(bib_dir) if f.endswith('.md') and f != '00_index.md']
files.sort()

success_count = 0
fail_count = 0

for filename in files:
    filepath = os.path.join(bib_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract title
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if not title_match:
        continue
    title = title_match.group(1).strip()
    
    # Extract year
    year_match = re.search(r'\*\*Année :\*\*\s+(\d{4})', content)
    year = year_match.group(1).strip() if year_match else ''
    
    print(f"Searching PDF for: {title}")
    
    # Search OpenAlex
    # We use a broad search first, then filter locally for exact/near match
    query_title = quote(title.replace(':', ' ').replace('-', ' ').replace('?', ''))
    url = f"https://api.openalex.org/works?filter=title.search:{query_title}"
    if year:
        url += f",publication_year:{year}"
        
    try:
        res = requests.get(url, headers=headers, timeout=10)
        data = res.json()
        
        pdf_url = None
        if data.get('results'):
            for work in data['results']:
                # Basic check to ensure it's not a completely unrelated paper
                # (sometimes search brings up weird stuff)
                if work.get('open_access') and work['open_access'].get('is_oa') and work['open_access'].get('oa_url'):
                    # Prefer pdf if it ends with .pdf
                    oa_url = work['open_access']['oa_url']
                    pdf_url = oa_url
                    if oa_url.endswith('.pdf'):
                        break # Perfect
                        
        if pdf_url:
            print(f" -> Found OA link: {pdf_url}")
            # Try to download
            pdf_filename = filename.replace('.md', '.pdf')
            pdf_path = os.path.join(pdf_dir, pdf_filename)
            
            try:
                pdf_res = requests.get(pdf_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
                if pdf_res.status_code == 200 and len(pdf_res.content) > 10000:
                    with open(pdf_path, 'wb') as pf:
                        pf.write(pdf_res.content)
                    print(" -> Downloaded!")
                    report += f"| {filename} | ✅ Téléchargé | [Lien]({pdf_url}) |\n"
                    success_count += 1
                else:
                    print(" -> Download failed or file too small.")
                    report += f"| {filename} | ⚠️ Échec téléchargement | [Lien]({pdf_url}) |\n"
                    fail_count += 1
            except Exception as e:
                print(f" -> Download error: {e}")
                report += f"| {filename} | ⚠️ Erreur téléchargement | [Lien]({pdf_url}) |\n"
                fail_count += 1
        else:
            print(" -> No Open Access PDF found.")
            report += f"| {filename} | ❌ Introuvable (Paywall / Pas en OA) | N/A |\n"
            fail_count += 1
            
    except Exception as e:
        print(f" -> OpenAlex API error: {e}")
        report += f"| {filename} | ❌ Erreur API | N/A |\n"
        fail_count += 1
        
    time.sleep(0.5)

report += f"\n**Bilan :** {success_count} téléchargés, {fail_count} introuvables ou échecs.\n"

with open(os.path.join(bib_dir, '00_rapport_telechargement.md'), 'w', encoding='utf-8') as f:
    f.write(report)
    
log_xrd('PDF download process', 'L3', 0.1, 0.1, 0.1, 0.1, 'Finish', f'{success_count} DL')
print("Finished.")
