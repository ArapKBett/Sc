import configparser
import json

class Config:
    def __init__(self, config_path='config/config.ini', sources_path='config/sources.json'):
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        with open(sources_path, 'r') as f:
            self.sources = json.load(f)

    def get(self, section, key):
        """Get a configuration value."""
        return self.config[section][key]

    def get_sources(self):
        """Get the list of content sources."""
        return self.sources
