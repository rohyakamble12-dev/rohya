from veda.utils.logger import logger

class ServiceRegistry:
    def __init__(self):
        self._services = {}

    def register(self, name, service):
        self._services[name] = service
        logger.info(f"Service registered: {name}")

    def get(self, name):
        if name not in self._services:
            logger.warning(f"Service requested but not found: {name}")
            return None
        return self._services[name]

    def has(self, name):
        return name in self._services

# Global Registry
registry = ServiceRegistry()
