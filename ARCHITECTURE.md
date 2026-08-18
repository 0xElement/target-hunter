# Architecture

```text
YOUR GITHUB
    |
GitHub Actions
    |
+---+----------------+
|                    |
Recon Engine      Repo Hunter
|                    |
subfinder          GitHub org/repos
crt.sh             secret patterns (sanitized)
dnsx               endpoint/internal-host patterns
httpx
Katana JS discovery
|                    |
+---------+----------+
          |
   AI Multi-Model
          |
   Candidate Leads
          |
   Second AI Triage
          |
 Passive Verification
          |
    VALID / HOLD
          |
    Manual Burp Test
          |
      Submission
```

The automated pipeline intentionally stops before exploit execution. Manual testing remains the final validation stage.
