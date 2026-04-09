from veda.core.controller import VedaController

def start():
    """Package Entry Point."""
    controller = VedaController()
    controller.bootstrap()

if __name__ == "__main__":
    start()
