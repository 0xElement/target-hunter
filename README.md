# Target Hunter — GitHub Actions.

A reusable, scope-controlled GitHub Actions pipeline for **authorized** security testing.

## Pipeline

```text
GitHub Actions
├── Recon Engine
│   ├── subfinder
│   ├── crt.sh
│   ├── dnsx
│   ├── httpx
│   └── Katana JS/endpoint discovery
│
├── Public Repo Hunter
│   ├── GitHub organization/repository discovery
│   ├── secret-pattern detection
│   └── endpoint/internal-host pattern detection
│
├── AI Multi-Model Analysis
│   └── OpenCode models (optional)
│
├── Candidate Leads
│
├── Second AI Triage
│
├── Passive Verification
│
└── VALID / HOLD / INVALID
       ↓
   Manual Burp validation
```

## Important

Only use this against assets and GitHub organizations explicitly authorized by the applicable program. Review automation/rate-limit rules before enabling scheduled runs. This project intentionally avoids destructive testing, credential attacks, SQL injection automation, fuzzing, account creation, privilege escalation, and denial-of-service testing.

Do not commit API keys, cookies, JWTs, passwords, private keys, customer data, or unredacted secrets.

## 1. Configure the target

Edit `scope.yml`:

```yaml
target: target.com
allowed_domains:
  - target.com
  - "*.target.com"
excluded_domains: []
github_orgs: []
```

For a public GitHub organization that is explicitly in scope:

```yaml
github_orgs:
  - example-org
```

## 2. GitHub setup

Create a repository, upload this project, and enable Actions.

For public repository hunting, create an optional GitHub Personal Access Token with the **minimum read-only public-repository access required by the program** and store it as:

`Settings → Secrets and variables → Actions → New repository secret → GITHUB_TOKEN_HUNTER`

The pipeline also works without it, but GitHub API rate limits will be lower.

No LLM secret is required by the default configuration if OpenCode's configured free model/provider is available. Provider availability can change; the AI jobs fail closed if the model cannot be reached.

## 3. Run

Go to:

`Actions → Recon Engine → Run workflow`

Then:

`Actions → Repo Hunter → Run workflow`

Then:

`Actions → AI Analyze → Run workflow`

Finally:

`Actions → Triage & Passive Verify → Run workflow`

You can also enable the scheduled workflows after confirming that the target program permits recurring automation.

## Results

- `results/latest/` — latest recon
- `results/repo-hunt/latest/` — latest public repository scan
- `leads/` — AI candidate leads
- `triage/` — triage decisions
- `knowledge/` — persistent, sanitized context

GitHub Actions artifacts are also uploaded for each run.

## Safety design

The automated verifier is limited to low-impact GET/HEAD requests against URLs already discovered by the pipeline. It does not submit exploit payloads. AI output is treated as a hypothesis and must be manually validated before reporting.
