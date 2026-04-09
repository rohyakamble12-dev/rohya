import json
import os
import re
from veda.utils.logger import logger
from veda.core.security import capabilities, ContractValidator
from veda.utils.privacy import privacy
from veda.core.registry import registry

class VedaGovernance:
    def __init__(self, assistant=None):
        self.assistant = assistant
        self.policy_path = "veda/core/capabilities.json"
        self.privacy_blacklist = ["banking", "password", "crypto-wallet", "login", "auth", "secret"]
        self.policy = {}
        self._load_policy()
        registry.register("governance", self)

    def _load_policy(self):
        try:
            if os.path.exists(self.policy_path):
                with open(self.policy_path, 'r') as f:
                    self.policy = json.load(f)
            else:
                self.policy = {
                    "restricted_sectors": ["C:\\Windows", "/etc", "/var", "/root"],
                    "domain_whitelist": ["google.com", "wikipedia.org", "github.com", "microsoft.com", "duckduckgo.com"]
                }
        except Exception as e:
            logger.warning(f"Governance: Policy load failure: {e}")
            self.policy = {}

    def enforce(self, user_input, is_subcommand=False):
        """Mandatory Sovereign Enforcement Chain."""
        # Ensure we have the assistant reference
        if not self.assistant:
             self.assistant = registry.get("assistant")

        if not self.assistant:
            return "Error: Assistant core disconnected from governance.", "ERROR"

        # 1. Sanitization
        sanitized_input = self._sanitize(user_input)

        # 2. Intent Extraction
        intent_data = self.assistant.llm.extract_intent(sanitized_input)
        intent = intent_data.get("intent", "none")
        params = intent_data.get("params", {})

        if intent == "none":
             return self.assistant.llm.chat(sanitized_input), "CHAT"

        # 3. RBAC & Policy Check
        plugin = self.assistant.plugins.get_plugin_for_intent(intent)
        if not plugin:
            return f"Error: Tactical intent '{intent}' not mapped to any known sector.", "ERROR"

        authorized, reason = capabilities.authorize(plugin, intent, params)
        if not authorized:
            return f"Access Denied: {reason}", "ERROR"

        # 4. Impact Prediction
        impact = plugin.predict_impact(intent, params)
        logger.audit(intent, params, impact=impact)

        # 5. Contract Validation (JSON Schema)
        valid, msg = ContractValidator.validate_input(plugin, intent, params)
        if not valid:
            return f"Security Violation: Parameter mismatch for {intent}. {msg}", "ERROR"

        # 6. Success: Final tactical parameter validation
        valid_p, p_msg = plugin.validate_params(intent, params)
        if not valid_p:
            return f"Security Violation: {p_msg}", "ERROR"

        return {"intent": intent, "params": params, "impact": impact, "input": sanitized_input}, "INTENT_VERIFIED"

    def is_sector_authorized(self, path):
        abs_path = os.path.abspath(os.path.expanduser(str(path)))
        for sector in self.policy.get("restricted_sectors", []):
            if abs_path.startswith(os.path.abspath(sector)):
                return False
        return True

    def is_domain_authorized(self, url):
        from urllib.parse import urlparse
        domain = urlparse(url).netloc.lower()
        if not domain: return False
        whitelist = self.policy.get("domain_whitelist", [])
        return any(d in domain for d in whitelist)

    def _sanitize(self, text):
        if not text: return ""
        if len(text) > 1500: text = text[:1500]
        blocked = [";", "&&", "||", "`", "$( ", "rm -rf"]
        for b in blocked:
            text = text.replace(b, "[BLOCKED]")
        return text.strip()

    def scrub_output(self, result):
        return privacy.scrub(str(result))

# Global instance for easy access in features
governance = VedaGovernance()
