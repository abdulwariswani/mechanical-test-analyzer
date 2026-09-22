# SSH Failed Login Analyser
 Lightweight ,memory-efficient python script designed to parse Linux authentication logs ,extract malicious login attempts and aggregate attack metrics by IP address. 

 # requirements
- Python 3.6+
- A log file in the format of `/var/log/auth.log` (standard Linux SSH logs).

 # How to run 
 python log_analyser.py <filename>

 
## Sample terminal output
__main__ - INFO - {
  '10.0.0.15': {
    'count': 2, 
    'users': {'root'}, 
    'timestamps': ['Feb  8 01:25:12', 'Feb 12 14:11:22']
  }
}

# Core Functions 
1. 1. `parsed_failed_log(filename)` – Yields parsed entries from the auth log.  
   Matches lines with *Failed password for* and extracts timestamp, username, IP, and optional port using a verbose regular expression.
2. IP_count(parsed_log) Groups the extracted details by IP address, accumulating hit counts, lists of targeted usernames 

3. Import Guard( if__name__ == '__main__')
    - when directly run __name__ resolves to '__main'
    - When imported __name__ resolves to 'log_analyser'. The excution blocks are skipped entirely , allowing you to borrow the processing fucntions saftely in an external dashboard application

## Features
- Reads standard `/var/log/auth.log` format
- Extracts timestamp, username, attacker IP, and port from failed SSH attempts
- Groups attempts by IP with hit count, targeted usernames, and attack timeline
- Generator‑based parsing for low memory usage
- Safe to import as a module (no side‑effects when imported)