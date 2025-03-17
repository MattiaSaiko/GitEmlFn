## Extract Emails from GitHub Repository  

## Description
**GitEmlFn** is a Python script that, in a few simple steps, downloads and analyzes the patch of the **first commit** of a GitHub project to extract the commit author’s email. It’s designed to provide insights into the origins of a repository for OSINT analytics.

---

## Installation & Requirements
- **Python 3.6 or higher**  
- **Required packages**:
  - `requests`
  - `beautifulsoup4`
  - `colorama`

---

### How to install:
```bash
pip install requests beautifulsoup4 colorama
```

---

### Quick Start:
- Clone or download this repository.
- Install the required packages (see above).
- Run the Python script, passing the target GitHub repository URL.

---

### Example:
```bash
python GitEmlFn.py https://github.com/author/repository
```

---

## Disclaimer
This tool is provided **for educational purposes only**. We are not responsible for the misuse of any extracted information. Usage must comply with applicable laws and regulations.
