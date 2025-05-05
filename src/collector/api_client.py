import requests
import json
import base64

class VirusTotalClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://www.virustotal.com/api/v3"

    def get_ip_report(self, ip_address):
        """Fetch a VirusTotal report for a given IP address."""
        headers = {"x-apikey": self.api_key}
        try:
            response = requests.get(f"{self.base_url}/ip_addresses/{ip_address}", headers=headers)
            response.raise_for_status()
            data = response.json()
            return f"IP {ip_address} Report: {json.dumps(data['data']['attributes'], indent=2)}"
        except requests.RequestException as e:
            return f"Error fetching VirusTotal report for {ip_address}: {e}"

class GitHubClient:
    def __init__(self, token):
        self.token = token
        self.base_url = "https://api.github.com"

    def get_repo_readme(self, repo):
        """Fetch the README from a GitHub repository."""
        headers = {"Authorization": f"token {self.token}"}
        try:
            response = requests.get(f"{self.base_url}/repos/{repo}/readme", headers=headers)
            response.raise_for_status()
            data = response.json()
            content = base64.b64decode(data['content']).decode('utf-8')
            return {'content': content, 'source': data['html_url']}
        except requests.RequestException as e:
            return {'content': f"Error fetching README for {repo}: {e}", 'source': ''}
