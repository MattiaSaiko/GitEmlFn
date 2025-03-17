import sys
import requests
from bs4 import BeautifulSoup
import re
import time
from colorama import Fore, Style, init

init(autoreset=True)

BANNER = f"""{Fore.CYAN}
   _____ _ _   ______           _ ______     
  / ____(_) | |  ____|         | |  ____|    
 | |  __ _| |_| |__   _ __ ___ | | |__ _ __  
 | | |_ | | __|  __| | '_ ` _ \| |  __| '_ \ 
 | |__| | | |_| |____| | | | | | | |  | | | |
  \_____|_|\__|______|_| |_| |_|_|_|  |_| |_|
{Style.RESET_ALL}                {Fore.YELLOW}Author: Saiko{Style.RESET_ALL}
"""

def main():
    print(BANNER)
    
    if len(sys.argv) != 2:
        print(f"{Fore.RED}[ERROR] {Style.RESET_ALL}Usage: python {sys.argv[0]} <GitHub Repository URL>")
        sys.exit(1)

    url = sys.argv[1]

    try:
        author = url.split('/')[3]
    except IndexError:
        print(f"{Fore.RED}[ERROR] {Style.RESET_ALL}Invalid GitHub repository URL.")
        sys.exit(1)

    commits_url = f"{url}/commits"
    
    headers = {'User-Agent': 'Mozilla/5.0'}

    print(f"{Fore.GREEN}[INFO] {Style.RESET_ALL}Fetching commit history...")

    try:
        response = requests.get(commits_url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        print(f"{Fore.RED}[ERROR] {Style.RESET_ALL}Failed to retrieve commit history.")
        sys.exit(1)

    soup = BeautifulSoup(response.text, 'html.parser')
    commit_links = soup.select('a[href*="/commit/"]')

    if not commit_links:
        print(f"{Fore.RED}[ERROR] {Style.RESET_ALL}No commits found.")
        sys.exit(1)

    first_commit_link = commit_links[0]['href']
    patch_url = f"https://github.com{first_commit_link}.patch"

    print(f"{Fore.GREEN}[INFO] {Style.RESET_ALL}Fetching first commit patch...")

    try:
        patch_response = requests.get(patch_url, headers=headers)
        patch_response.raise_for_status()
        patch_content = patch_response.content.decode('utf-8', errors='ignore')
    except requests.exceptions.RequestException:
        print(f"{Fore.RED}[ERROR] {Style.RESET_ALL}Failed to retrieve commit patch.")
        sys.exit(1)

    email_regex = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    emails = re.findall(email_regex, patch_content)

    if emails:
        print(f"{Fore.GREEN}[SUCCESS] {Style.RESET_ALL}Email found: {Fore.YELLOW}{emails[0]}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}[ERROR] {Style.RESET_ALL}No email found.")
        sys.exit(1)

if __name__ == "__main__":
    main()