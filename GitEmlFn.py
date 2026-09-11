#!/usr/bin/env python3
"""GitEmlFn - estrae l'email dell'autore del commit iniziale di un repo GitHub."""

import argparse
import json
import os
import re
import sys
import time
from urllib.parse import urlparse

import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

BANNER = r"""
   _____ _ _   ______           _ ______
  / ____(_) | |  ____|         | |  ____|
 | |  __ _| |_| |__   _ __ ___ | | |__ _ __
 | | |_ | | __|  __| | '_ ` _ \| |  __| '_ \
 | |__| | | |_| |____| | | | | | | |  | | | |
  \_____|_|\__|______|_| |_| |_|_|_|  |_| |_|
"""

API_ROOT = "https://api.github.com"
EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
LINK_LAST_RE = re.compile(r'<[^>]*[?&]page=(\d+)[^>]*>;\s*rel="last"')
NOREPLY_SUFFIX = "@users.noreply.github.com"
TIMEOUT = 15
MAX_RETRIES = 3


class GitEmlFnError(Exception):
    pass


def parse_args():
    parser = argparse.ArgumentParser(
        prog="GitEmlFn",
        description="Estrae l'email dell'autore del commit iniziale (root commit) di un repository GitHub.",
    )
    parser.add_argument("url", help="URL del repository GitHub, es. https://github.com/author/repo")
    parser.add_argument(
        "-t", "--token",
        default=os.environ.get("GITHUB_TOKEN"),
        help="Token GitHub (o variabile d'ambiente GITHUB_TOKEN) per alzare il rate limit",
    )
    parser.add_argument(
        "-a", "--all-emails",
        action="store_true",
        help="Mostra tutte le email trovate nella patch, non solo quella dell'autore/committer",
    )
    parser.add_argument("--json", action="store_true", help="Output in formato JSON")
    parser.add_argument("--no-color", action="store_true", help="Disabilita colori/formattazione")
    return parser.parse_args()


def parse_github_url(url):
    parsed = urlparse(url if "://" in url else f"https://{url}")
    if parsed.netloc.lower() not in {"github.com", "www.github.com"}:
        raise GitEmlFnError("L'URL deve puntare a github.com.")

    parts = [p for p in parsed.path.split("/") if p]
    if len(parts) < 2:
        raise GitEmlFnError("URL repository non valido. Formato atteso: https://github.com/author/repo")

    owner, repo = parts[0], parts[1]
    if repo.endswith(".git"):
        repo = repo[:-4]
    return owner, repo


def request_with_retries(method, url, **kwargs):
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.request(method, url, timeout=TIMEOUT, **kwargs)
        except requests.exceptions.RequestException as exc:
            last_error = exc
            time.sleep(attempt)
            continue

        if response.status_code == 403 and "rate limit" in response.text.lower():
            raise GitEmlFnError(
                "Rate limit GitHub superato. Usa --token / variabile GITHUB_TOKEN per un limite più alto."
            )
        if response.status_code == 404:
            raise GitEmlFnError("Repository non trovato (404). Controlla che l'URL sia corretto e pubblico.")
        if response.status_code >= 500:
            last_error = GitEmlFnError(f"Errore server GitHub ({response.status_code}).")
            time.sleep(attempt)
            continue

        return response

    raise last_error or GitEmlFnError("Richiesta fallita dopo diversi tentativi.")


def get_root_commit(owner, repo, token):
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    commits_url = f"{API_ROOT}/repos/{owner}/{repo}/commits"
    first_page = request_with_retries("GET", commits_url, headers=headers, params={"per_page": 1, "page": 1})
    first_page.raise_for_status()

    link_header = first_page.headers.get("Link", "")
    match = LINK_LAST_RE.search(link_header)
    last_page = int(match.group(1)) if match else 1

    if last_page == 1:
        data = first_page.json()
    else:
        last_response = request_with_retries(
            "GET", commits_url, headers=headers, params={"per_page": 1, "page": last_page}
        )
        last_response.raise_for_status()
        data = last_response.json()

    if not data:
        raise GitEmlFnError("Nessun commit trovato nel repository.")

    commit = data[0]
    return {
        "sha": commit["sha"],
        "author_name": commit["commit"]["author"]["name"],
        "author_email": commit["commit"]["author"]["email"],
        "committer_name": commit["commit"]["committer"]["name"],
        "committer_email": commit["commit"]["committer"]["email"],
        "date": commit["commit"]["author"]["date"],
    }


def fetch_patch_emails(owner, repo, sha):
    patch_url = f"https://github.com/{owner}/{repo}/commit/{sha}.patch"
    response = request_with_retries("GET", patch_url, headers={"User-Agent": "GitEmlFn"})
    response.raise_for_status()
    patch_content = response.content.decode("utf-8", errors="ignore")

    seen = []
    for email in EMAIL_RE.findall(patch_content):
        if email not in seen:
            seen.append(email)
    return seen


def annotate(email):
    return f"{email}  (GitHub noreply, email reale nascosta)" if email.endswith(NOREPLY_SUFFIX) else email


def main():
    args = parse_args()
    console = Console(no_color=args.no_color, highlight=False)

    if not args.json:
        console.print(Panel(BANNER, style="cyan", subtitle="[yellow]Author: Saiko[/yellow]", expand=False))

    try:
        owner, repo = parse_github_url(args.url)

        with console.status("[green]Ricerca del commit iniziale su GitHub...[/green]", spinner="dots") if not args.json else _noop():
            commit = get_root_commit(owner, repo, args.token)

        patch_emails = []
        patch_warning = None
        if args.all_emails:
            try:
                with console.status("[green]Recupero patch del commit iniziale...[/green]", spinner="dots") if not args.json else _noop():
                    patch_emails = fetch_patch_emails(owner, repo, commit["sha"])
            except (GitEmlFnError, requests.exceptions.RequestException):
                patch_warning = "Patch non disponibile (diff troppo grande o non generabile da GitHub)."

    except GitEmlFnError as exc:
        _fail(console, args.json, str(exc))
    except requests.exceptions.RequestException as exc:
        _fail(console, args.json, f"Errore di rete: {exc}")

    result = {
        "owner": owner,
        "repo": repo,
        "commit_sha": commit["sha"],
        "commit_date": commit["date"],
        "author_name": commit["author_name"],
        "author_email": commit["author_email"],
        "committer_name": commit["committer_name"],
        "committer_email": commit["committer_email"],
        "all_emails_in_patch": patch_emails if args.all_emails else None,
        "patch_warning": patch_warning,
    }

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    table = Table(title=f"Commit iniziale — {owner}/{repo}", show_header=True, header_style="bold cyan")
    table.add_column("Campo", style="bold")
    table.add_column("Valore")
    table.add_row("SHA", commit["sha"][:12])
    table.add_row("Data", commit["date"])
    table.add_row("Autore", commit["author_name"])
    table.add_row("Email autore", annotate(commit["author_email"]))
    table.add_row("Committer", commit["committer_name"])
    table.add_row("Email committer", annotate(commit["committer_email"]))
    console.print(table)

    if args.all_emails:
        if patch_warning:
            console.print(f"\n[yellow][WARN][/yellow] {patch_warning}")
        elif patch_emails:
            console.print("\n[bold]Tutte le email trovate nella patch:[/bold]")
            for email in patch_emails:
                console.print(f"  • {annotate(email)}")

    console.print(f"\n[bold green][SUCCESS][/bold green] Email principale: [yellow]{commit['author_email']}[/yellow]")


class _noop:
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _fail(console, as_json, message):
    if as_json:
        print(json.dumps({"error": message}, ensure_ascii=False))
    else:
        console.print(f"[bold red][ERROR][/bold red] {message}")
    sys.exit(1)


if __name__ == "__main__":
    main()
