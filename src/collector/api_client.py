import requests
import logging

class VirusTotalClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://www.virustotal.com/api/v3"

    def get_ip_report(self, ip_address):
        try:
            headers = {"x-apikey": self.api_key}
            response = requests.get(f"{self.base_url}/ip_addresses/{ip_address}", headers=headers)
            response.raise_for_status()
            report = response.json()['data']['attributes']
            report['ip'] = ip_address
            return report
        except Exception as e:
            logging.getLogger().error(f"Error fetching VirusTotal report for {ip_address}: {e}")
            return {}

class GitHubClient:
    def __init__(self, token):
        self.token = token
        self.base_url = "https://api.github.com"

    def get_repo_readme(self, repo):
        try:
            headers = {"Authorization": f"token {self.token}"}
            response = requests.get(f"{self.base_url}/repos/{repo}/readme", headers=headers)
            response.raise_for_status()
            content = response.json()['content']
            import base64
            decoded_content = base64.b64decode(content).decode('utf-8')[:500]
            summary = f"For penetration testing, explore tools and techniques described in the {repo} repository on GitHub."
            return {'content': summary, 'source': f"https://github.com/{repo}"}
        except Exception as e:
            logging.getLogger().error(f"Error fetching GitHub README for {repo}: {e}")
            return {'content': '', 'source': ''}

class OTXClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://otx.alienvault.com"

    def get_pulse(self):
        try:
            headers = {"X-OTX-API-KEY": self.api_key}
            response = requests.get(f"{self.base_url}/api/v1/pulses/subscribed", headers=headers)
            response.raise_for_status()
            pulses = response.json()['results']
            return pulses[0] if pulses else {}
        except Exception as e:
            logging.getLogger().error(f"Error fetching OTX pulse: {e}")
            return {}

class AbuseIPDBClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.abuseipdb.com/api/v2"

    def get_ip_report(self, ip_address):
        try:
            headers = {"Key": self.api_key, "Accept": "application/json"}
            params = {"ipAddress": ip_address, "maxAgeInDays": 90}
            response = requests.get(f"{self.base_url}/check", headers=headers, params=params)
            response.raise_for_status()
            return response.json()['data']
        except Exception as e:
            logging.getLogger().error(f"Error fetching AbuseIPDB report for {ip_address}: {e}")
            return {}