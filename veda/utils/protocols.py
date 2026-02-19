import json
import os

class VedaProtocols:
    def __init__(self, config_path="veda_protocols.json"):
        self.config_path = config_path
        self.default_protocols = {
            "deep_research": False,
            "private_mode": False,
            "restricted_knowledge": False,
            "document_learning": True
        }
        self.protocols = self._load_protocols()

    def _load_protocols(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    return {**self.default_protocols, **json.load(f)}
            except:
                return self.default_protocols
        return self.default_protocols

    def save_protocols(self):
        with open(self.config_path, 'w') as f:
            json.dump(self.protocols, f, indent=4)

    def toggle_protocol(self, name):
        if name in self.protocols:
            self.protocols[name] = not self.protocols[name]
            self.save_protocols()
            return self.protocols[name]
        return None

    def get_status(self):
        return self.protocols

    def is_allowed(self, protocol_name):
        return self.protocols.get(protocol_name, False)
