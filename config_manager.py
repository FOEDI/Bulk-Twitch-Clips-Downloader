import json
import os

class ConfigManager:
    def __init__(self):
        self.config_file = 'config.json'
        self.default_config = {
            'client_id': '',
            'client_secret': ''
        }
        self.config = self.load_config()

    def load_config(self):
        """Charge la configuration depuis le fichier config.json"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            else:
                self.save_config(self.default_config)
                return self.default_config
        except Exception as e:
            print(f"Erreur lors de la lecture de la configuration: {e}")
            return self.default_config

    def save_config(self, config):
        """Sauvegarde la configuration dans le fichier config.json"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la configuration: {e}")

    def get_client_id(self):
        """Récupère le Client ID"""
        return self.config.get('client_id', '')

    def get_client_secret(self):
        """Récupère le Client Secret"""
        return self.config.get('client_secret', '')

    def set_credentials(self, client_id, client_secret):
        """Définit les credentials Twitch"""
        self.config['client_id'] = client_id
        self.config['client_secret'] = client_secret
        self.save_config(self.config)