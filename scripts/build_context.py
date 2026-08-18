from pathlib import Path
root=Path(__file__).resolve().parents[1]
parts=[]
for f in [root/'results/latest/summary.txt',root/'results/latest/live.txt',root/'results/latest/js-endpoints.txt',root/'results/repo-hunt/latest/hits.json']:
    if f.exists():
        parts.append(f'\n===== {f.relative_to(root)} =====\n'+f.read_text(errors='ignore')[:120000])
(root/'knowledge').mkdir(exist_ok=True)
(root/'knowledge/context.md').write_text('# Sanitized hunting context\n'+''.join(parts))
