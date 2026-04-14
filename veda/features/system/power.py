from veda.features.base import VedaPlugin, PermissionTier
import subprocess

class PowerControlPlugin(VedaPlugin):
    def setup(self):
        self.register_intent("shutdown", self.shutdown_pc, PermissionTier.CONFIRM_REQUIRED)
        self.register_intent("restart", self.restart_pc, PermissionTier.CONFIRM_REQUIRED)
        self.register_intent("lock_pc", self.lock_pc, PermissionTier.SAFE)
        self.register_intent("sleep", self.system_sleep, PermissionTier.CONFIRM_REQUIRED)

    def lock_pc(self, params):
        subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], capture_output=True)
        return "System locked."

    def system_sleep(self, params):
        subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"], capture_output=True)
        return "Suspending system."

    def shutdown_pc(self, params):
        subprocess.run(["shutdown", "/s", "/t", "30"], capture_output=True)
        return "System shutdown sequence initiated (30s delay)."

    def restart_pc(self, params):
        subprocess.run(["shutdown", "/r", "/t", "30"], capture_output=True)
        return "System restart sequence initiated (30s delay)."
