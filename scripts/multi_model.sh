#!/usr/bin/env bash
set -euo pipefail
CTX="knowledge/context.md"
mkdir -p leads
PROMPT='You are a security research triage assistant. Analyze the supplied reconnaissance context for authorized bug-bounty research. Produce only candidate leads that are plausibly security-relevant and in scope. Do not invent evidence. Do not print secrets, tokens, cookies, private keys, or sensitive personal data. Prefer IDOR/access-control hypotheses, exposed sensitive data, auth weaknesses, SSRF indicators, security-relevant endpoint exposure, and clearly actionable misconfigurations. Treat every item as UNVALIDATED. For each lead provide: title, evidence, affected URL/repository/path, why it may matter, safe passive validation idea, and confidence. Do not perform or recommend destructive actions.'

for model in ${MODELS:-opencode/nemotron-3-ultra-free}; do
  safe=$(echo "$model" | tr '/:' '__')
  echo "[+] $model"
  {
    echo "$PROMPT"
    echo
    cat "$CTX"
  } | opencode run --model "$model" > "leads/${safe}.md" 2>&1 || echo "Model unavailable: $model" > "leads/${safe}.md"
done

cat > leads/README.md <<'TXT'
These are AI-generated UNVALIDATED hypotheses. Confirm scope and manually reproduce through an authorized testing workflow before reporting.
TXT
