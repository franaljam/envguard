# envguard

> CLI tool to validate and diff .env files across environments before deployment

---

## Installation

```bash
pip install envguard
```

Or with pipx:

```bash
pipx install envguard
```

---

## Usage

Validate a `.env` file against a `.env.example` template:

```bash
envguard validate --env .env --template .env.example
```

Diff two environment files to spot missing or changed keys:

```bash
envguard diff .env.staging .env.production
```

Run a pre-deployment check across multiple environments:

```bash
envguard check --envs .env.staging .env.production --strict
```

**Example output:**

```
[✓] All required keys present in .env.staging
[✗] .env.production is missing: DATABASE_URL, REDIS_HOST
[!] Value mismatch for LOG_LEVEL: staging=debug, production=debug (ok)
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| `0`  | All checks passed |
| `1`  | One or more keys are missing or mismatched |
| `2`  | Invalid arguments or file not found |

This makes `envguard` easy to integrate into CI pipelines — a non-zero exit code will fail the pipeline automatically.

---

## Features

- Detects missing or undefined keys before deployment
- Side-by-side diff of environment files
- Strict mode to fail on any discrepancy (useful in CI pipelines)
- Supports `.env`, `.env.example`, and named environment files

---

## License

[MIT](LICENSE) © envguard contributors
