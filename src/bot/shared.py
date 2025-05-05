CATEGORIES = [
    'red_teaming',
    'blue_teaming',
    'soc_analysis',
    'ethical_hacking',
    'threat_intelligence',
    'forensics',
    'general'
]

def format_message(content, source):
    max_length = 1900
    try:
        import json
        if source in ['VirusTotal', 'AbuseIPDB', 'AlienVault OTX']:
            report = json.loads(content) if isinstance(content, str) else content
            if source == 'VirusTotal':
                ip = report.get('ip', 'Unknown IP')
                reputation = report.get('reputation', 'Unknown')
                cert_info = report.get('last_https_certificate', {})
                validity = cert_info.get('validity', {})
                not_after = validity.get('not_after', 'Unknown')
                domains = cert_info.get('extensions', {}).get('subject_alternative_name', [])
                summary = (
                    f"VirusTotal has information about the IP address {ip}. It has a reputation score of {reputation}, where higher scores indicate a safer IP. "
                    f"The SSL certificate associated with this IP is valid until {not_after}. "
                    f"It’s linked to domains like {', '.join(domains[:3]) if domains else 'none'}. "
                    f"This data comes from VirusTotal."
                )
            elif source == 'AbuseIPDB':
                ip = report.get('ipAddress', 'Unknown IP')
                abuse_score = report.get('abuseConfidenceScore', 'Unknown')
                reports = report.get('totalReports', 'Unknown')
                summary = (
                    f"The IP address {ip} has been checked by AbuseIPDB. It has an abuse confidence score of {abuse_score} percent, where lower scores are safer. "
                    f"There have been {reports} reports of suspicious activity. This information is provided by AbuseIPDB."
                )
            elif source == 'AlienVault OTX':
                title = report.get('name', 'Unknown Pulse')
                description = report.get('description', 'No description')[:200]
                summary = (
                    f"AlienVault OTX reports a threat intelligence pulse named {title}. This pulse describes {description.lower()}. "
                    f"The information is sourced from AlienVault OTX."
                )
        else:
            # Handle RSS, GitHub, and other text-based tips
            summary = (
                f"{content} This tip is provided by {source}."
            )
        if len(summary) > max_length:
            summary = summary[:max_length-3] + "..."
        return summary
    except Exception as e:
        return f"There was an issue processing this tip: {e}. It comes from {source}."