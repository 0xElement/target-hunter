import re, urllib.request, urllib.parse
from pathlib import Path
root=Path(__file__).resolve().parents[1]
out=root/'triage'; out.mkdir(exist_ok=True)
leads=list((root/'leads').glob('*.md'))
text='\n'.join(p.read_text(errors='ignore') for p in leads if p.name!='README.md')
urls=sorted(set(re.findall(r'https?://[^\s\]\)>,"\']+', text)))[:12]
rows=[]
for u in urls:
    try:
        req=urllib.request.Request(u,method='HEAD',headers={'User-Agent':'authorized-passive-verifier/1.0'})
        with urllib.request.urlopen(req,timeout=8) as r: rows.append(f'PASSIVE {r.status} {u}')
    except Exception as e:
        rows.append(f'NO-CONFIRMATION {u} ({type(e).__name__})')

(out/'decision.md').write_text('''# Passive Triage\n\nAI leads remain **UNVALIDATED**. The automated verifier only performs low-impact HEAD requests against URLs present in the AI output. A successful HTTP response is not proof of a vulnerability.\n\n## Verification observations\n\n'''+('\n'.join('- '+x for x in rows) if rows else '- No candidate URLs were available.')+'\n\n## Decision\n\n**HOLD — manual validation required.**\n''')
