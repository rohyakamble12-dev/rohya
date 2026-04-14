from veda.features.base import VedaPlugin, PermissionTier
try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    import pythoncom
except:
    AudioUtilities = None

class AudioControlPlugin(VedaPlugin):
    def setup(self):
        self.register_intent("set_volume", self.set_volume, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {"level": {"type": "integer", "minimum": 0, "maximum": 100}}, "required": ["level"]})
        self.register_intent("mute_toggle", self.toggle_mute, PermissionTier.SAFE)

    def set_volume(self, params):
        if not AudioUtilities: return "Audio control unavailable."
        level = params.get("level", 50)
        try:
            pythoncom.CoInitialize()
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMasterVolumeLevelScalar(float(level) / 100, None)
            return f"Volume set to {level}%."
        except Exception as e: return f"Volume control failed: {e}"
        finally:
            try: pythoncom.CoUninitialize()
            except: pass

    def toggle_mute(self, params):
        if not AudioUtilities: return "Audio control unavailable."
        try:
            pythoncom.CoInitialize()
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            is_muted = volume.GetMute()
            volume.SetMute(not is_muted, None)
            return "Mute toggled: " + ("OFF" if is_muted else "ON")
        except Exception as e: return f"Mute control failed: {e}"
        finally:
            try: pythoncom.CoUninitialize()
            except: pass
