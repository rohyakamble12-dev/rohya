import collections

class VedaEventBus:
    def __init__(self):
        self.subscribers = collections.defaultdict(list)

    def subscribe(self, event_type, callback):
        self.subscribers[event_type].append(callback)

    def publish(self, event_type, data=None):
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    from veda.utils.logger import logger
                    logger.error(f"EventBus callback error on {event_type}: {e}")

# Global event bus
bus = VedaEventBus()

# Event Types Constants
class Events:
    USER_INPUT = "user_input"
    ASSISTANT_RESPONSE = "assistant_response"
    SYSTEM_ALERT = "system_alert"
    STATE_CHANGE = "state_change" # idle, thinking, speaking
    ACTION_COMPLETED = "action_completed"
    CONTEXT_CHANGE = "context_change"
    PROTOCOL_UPDATE = "protocol_update"
