#!/usr/bin/env python3
import json, os, re, subprocess, time
from pathlib import Path
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parents[1]
scope=ROOT/'scope.yml'
text=scope.read_text()
orgs=[]
in_g=False
for line in text.splitlines():
    if line.strip()=='github_orgs:': in_g=True; continue
    if in_g:
        if line.startswith('  - '): orgs.append(line.split('  - ',1)[1].strip())
        elif line and not line.startswith(' '): in_g=False

out=ROOT/'results/repo-hunt/latest'
out.mkdir(parents=True, exist_ok=True)
for p in out.iterdir():
    if p.is_file(): p.unlink()

if not orgs:
    (out/'summary.txt').write_text('No GitHub organizations configured in scope.yml.\n')
    raise SystemExit(0)

token=os.getenv('GH_TOKEN','')
headers={'Accept':'application/vnd.github+json','User-Agent':'authorized-recon'}
if token: headers['Authorization']='Bearer '+token

patterns={
 'aws_access_key': r'AKIA[0-9A-Z]{16}',
 'github_token': r'gh[pousr]_[A-Za-z0-9_]{20,}',
 'private_key': r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
 'jwt': r'eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}',
 'api_key_hint': r'(?i)(api[_-]?key|client[_-]?secret|access[_-]?token)\s*[:=]\s*["\'][^"\']{12,}["\']',
 'internal_host': r'(?i)https?://(?:localhost|127\.0\.0\.1|[^/\s]+\.(?:internal|local|corp|staging|dev)(?::\d+)?)'
}

def api(url):
    req=Request(url,headers=headers)
    with urlopen(req,timeout=15) as r: return json.load(r)

def redact(s):
    s=re.sub(r'(gh[pousr]_[A-Za-z0-9_]{10,})', lambda m:'REDACTED:'+str(abs(hash(m.group(1)))), s)
    s=re.sub(r'(AKIA[0-9A-Z]{16})', lambda m:'REDACTED:'+str(abs(hash(m.group(1)))), s)
    return s

hits=[]
for org in orgs:
    try:
        repos=api(f'https://api.github.com/orgs/{org}/repos?per_page=30&type=public&sort=updated')
    except Exception as e:
        hits.append({'org':org,'error':str(e)[:200]}); continue
    for repo in repos[:20]:
        full=repo.get('full_name','')
        try:
            branch=repo.get('default_branch','main')
            raw=api(f'https://api.github.com/repos/{full}/git/trees/{branch}?recursive=1')
            paths=[x.get('path','') for x in raw.get('tree',[]) if x.get('type')=='blob']
            interesting=[p for p in paths if re.search(r'(?i)(\.env|config|secret|credential|token|auth|api|key|\.json$|\.ya?ml$)',p)][:80]
            for p in interesting:
                if len(p)>180: continue
                try:
                    req=Request(f'https://raw.githubusercontent.com/{full}/{branch}/{p}',headers={'User-Agent':'authorized-recon'})
                    with urlopen(req,timeout=10) as rr: data=rr.read(500000).decode('utf-8','ignore')
                except Exception: continue
                for name,pat in patterns.items():
                    if re.search(pat,data):
                        hits.append({'repository':full,'path':p,'pattern':name,'note':'Potential match; secret material intentionally not stored.'})
        except Exception as e:
            hits.append({'repository':full,'error':str(e)[:200]})

(out/'hits.json').write_text(json.dumps(hits,indent=2))
(out/'summary.txt').write_text(f'Organizations: {", ".join(orgs)}\nPotential sanitized hits: {len([x for x in hits if "pattern" in x])}\nNo secret values are stored.\n')
