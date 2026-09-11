# GitEmlFn

*[English version below]*

---

## 🇮🇹 Italiano

Estrae l'email dell'autore del **commit iniziale** (root commit) di un repository GitHub, utile per analisi OSINT sull'origine di un progetto.

A differenza dello scraping HTML della pagina `/commits` (che mostra i commit più recenti per primi ed è fragile ai cambi di markup), GitEmlFn usa la **GitHub REST API** per risalire con certezza al primo commit della storia, seguendo la paginazione fino all'ultima pagina.

### Installazione

Richiede **Python 3.8+**.

```bash
pip install -r requirements.txt
```

Dipendenze:
- `requests`
- `rich`

### Uso

```bash
python GitEmlFn.py https://github.com/author/repository
```

#### Opzioni

| Flag | Descrizione |
|---|---|
| `-t`, `--token` | Token GitHub (o variabile `GITHUB_TOKEN`) per alzare il rate limit API |
| `-a`, `--all-emails` | Mostra tutte le email trovate nella patch del commit (author, committer, co-author, ecc.) |
| `--json` | Output in formato JSON, comodo per pipeline/script |
| `--no-color` | Disabilita colori e formattazione |

#### Esempi

```bash
# Uso base
python GitEmlFn.py https://github.com/author/repository

# Con token per evitare rate limit (60 req/h da anonimo, 5000 req/h autenticato)
python GitEmlFn.py https://github.com/author/repository --token ghp_xxx
export GITHUB_TOKEN=ghp_xxx && python GitEmlFn.py https://github.com/author/repository

# Tutte le email trovate nella patch
python GitEmlFn.py https://github.com/author/repository --all-emails

# Output JSON per script
python GitEmlFn.py https://github.com/author/repository --json
```

### Output

Lo script mostra SHA, data, autore e committer del commit iniziale, con evidenza se un'email è un indirizzo `@users.noreply.github.com` (l'email reale è nascosta dietro le impostazioni privacy di GitHub).

### Limitazioni

- Repository privati non sono supportati (serve un token con permessi adeguati, non testato).
- Senza token, l'API GitHub limita a **60 richieste/ora** per IP.
- Se GitHub ha rimosso o modificato la cronologia (rebase/squash della history iniziale), il "primo commit" restituito è quello attualmente più vecchio raggiungibile dalla API, non necessariamente il commit storico originale se la history è stata riscritta.

### Disclaimer

Questo tool è fornito **esclusivamente a scopo educativo/OSINT difensivo**. Non siamo responsabili per l'uso improprio delle informazioni estratte. L'utilizzo deve rispettare le leggi e i regolamenti applicabili, inclusi i termini di servizio di GitHub.

---

## 🇬🇧 English

Extracts the email of the author of the **initial commit** (root commit) of a GitHub repository, useful for OSINT analysis on a project's origin.

Unlike HTML scraping of the `/commits` page (which shows the most recent commits first and is fragile to markup changes), GitEmlFn uses the **GitHub REST API** to reliably trace back to the first commit in the history, following pagination through to the last page.

### Installation

Requires **Python 3.8+**.

```bash
pip install -r requirements.txt
```

Dependencies:
- `requests`
- `rich`

### Usage

```bash
python GitEmlFn.py https://github.com/author/repository
```

#### Options

| Flag | Description |
|---|---|
| `-t`, `--token` | GitHub token (or `GITHUB_TOKEN` variable) to raise the API rate limit |
| `-a`, `--all-emails` | Show all emails found in the commit patch (author, committer, co-author, etc.) |
| `--json` | JSON output, convenient for pipelines/scripts |
| `--no-color` | Disable colors and formatting |

#### Examples

```bash
# Basic usage
python GitEmlFn.py https://github.com/author/repository

# With token to avoid rate limiting (60 req/h anonymous, 5000 req/h authenticated)
python GitEmlFn.py https://github.com/author/repository --token ghp_xxx
export GITHUB_TOKEN=ghp_xxx && python GitEmlFn.py https://github.com/author/repository

# All emails found in the patch
python GitEmlFn.py https://github.com/author/repository --all-emails

# JSON output for scripting
python GitEmlFn.py https://github.com/author/repository --json
```

### Output

The script displays SHA, date, author, and committer of the initial commit, highlighting whether an email is a `@users.noreply.github.com` address (the real email is hidden behind GitHub's privacy settings).

### Limitations

- Private repositories are not supported (would need a token with appropriate permissions, not tested).
- Without a token, the GitHub API is limited to **60 requests/hour** per IP.
- If GitHub history has been removed or altered (rebase/squash of the initial history), the "first commit" returned is the oldest one currently reachable via the API, not necessarily the original historical commit if the history has been rewritten.

### Disclaimer

This tool is provided **exclusively for educational/defensive OSINT purposes**. We are not responsible for misuse of the extracted information. Use must comply with applicable laws and regulations, including GitHub's terms of service.
