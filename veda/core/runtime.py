import multiprocessing
import time
import os
import signal
from veda.utils.logger import logger

class IsolatedResult:
    def __init__(self, success, data=None, error=None, timeout=False):
        self.success = success
        self.data = data
        self.error = error
        self.timeout = timeout

class VedaRuntime:
    def __init__(self, default_timeout=15, llm_timeout=45):
        self.default_timeout = default_timeout
        self.llm_timeout = llm_timeout
        self._active_processes = []
        self._pool = None
        # Lazy initialization to avoid process spawning on import

    def _get_pool(self):
        if self._pool is None:
             # Pre-warm worker processes with plugin discovery
             self._pool = multiprocessing.get_context('spawn').Pool(
                 processes=2,
                 initializer=self._initialize_worker
             )
        return self._pool

    def _initialize_worker(self):
        """Pre-loads core logic in worker processes."""
        try:
            from veda.core.plugins import discover_and_load
            discover_and_load()
        except Exception: pass

    def execute_intent(self, plugin_obj, method_name, params, timeout=None):
        """Strategic Execution: Executes a tactical intent in the current process to maintain assistant state access."""
        # Note: We keep the method signature similar to avoid large-scale refactoring,
        # but we shift from multiprocessing back to direct calls for "real life" functional depth.
        # Background threading in VedaController still prevents UI blocking.
        try:
            method = getattr(plugin_obj, method_name)
            result = method(params)
            return IsolatedResult(success=True, data=result)
        except Exception as e:
            logger.error(f"Tactical Fault: {e}")
            return IsolatedResult(success=False, error=str(e))

    def _worker_target(self, plugin_name, method_name, params):
        """Standardized worker target for pooled processes."""
        try:
            from veda.core.plugins import get_plugin_class
            plugin_cls = get_plugin_class(plugin_name)
            if not plugin_cls: return {"success": False, "error": f"Plugin {plugin_name} not found."}

            plugin = plugin_cls(None)
            method = getattr(plugin, method_name)
            result = method(params)
            return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def execute_llm(self, method, timeout=None, *args, **kwargs):
        """Neural Link execution with Governed timeouts."""
        timeout = timeout or self.llm_timeout
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(method, *args, **kwargs)
            try:
                result = future.result(timeout=timeout)
                return IsolatedResult(success=True, data=result)
            except concurrent.futures.TimeoutError:
                logger.error(f"Neural Link: Timeout after {timeout}s")
                return IsolatedResult(success=False, error="Neural Link Timeout", timeout=True)
            except Exception as e:
                return IsolatedResult(success=False, error=str(e))

    def shutdown(self):
        """Tactical purge of worker pool and orphaned processes."""
        logger.info("Veda Runtime: Purging isolated execution sectors.")
        try:
            if self._pool:
                self._pool.close()
                self._pool.terminate()
                self._pool.join()
        except Exception: pass

        # Comprehensive process cleanup
        for p in self._active_processes:
            if p.is_alive():
                try:
                    p.terminate()
                    p.join(1)
                    if p.is_alive(): p.kill()
                except Exception: pass

runtime = VedaRuntime()
