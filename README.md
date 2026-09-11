# GitEmlFn

Estrae l'email dell'autore del **commit iniziale** (root commit) di un repository GitHub, utile per analisi OSINT sull'origine di un progetto.

A differenza dello scraping HTML della pagina `/commits` (che mostra i commit più recenti per primi ed è fragile ai cambi di markup), GitEmlFn usa la **GitHub REST API** per risalire con certezza al primo commit della storia, seguendo la paginazione fino all'ultima pagina.

---

## Installazione

Richiede **Python 3.8+**.

```bash
pip install -r requirements.txt
```

Dipendenze:
- `requests`
- `rich`

---

## Uso

```bash
python GitEmlFn.py https://github.com/author/repository
```

### Opzioni

| Flag | Descrizione |
|---|---|
| `-t`, `--token` | Token GitHub (o variabile `GITHUB_TOKEN`) per alzare il rate limit API |
| `-a`, `--all-emails` | Mostra tutte le email trovate nella patch del commit (author, committer, co-author, ecc.) |
| `--json` | Output in formato JSON, comodo per pipeline/script |
| `--no-color` | Disabilita colori e formattazione |

### Esempi

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

---

## Output

Lo script mostra SHA, data, autore e committer del commit iniziale, con evidenza se un'email è un indirizzo `@users.noreply.github.com` (l'email reale è nascosta dietro le impostazioni privacy di GitHub).

---

## Limitazioni

- Repository privati non sono supportati (serve un token con permessi adeguati, non testato).
- Senza token, l'API GitHub limita a **60 richieste/ora** per IP.
- Se GitHub ha rimosso o modificato la cronologia (rebase/squash della history iniziale), il "primo commit" restituito è quello attualmente più vecchio raggiungibile dalla API, non necessariamente il commit storico originale se la history è stata riscritta.

---

## Disclaimer

Questo tool è fornito **esclusivamente a scopo educativo/OSINT difensivo**. Non siamo responsabili per l'uso improprio delle informazioni estratte. L'utilizzo deve rispettare le leggi e i regolamenti applicabili, inclusi i termini di servizio di GitHub.
