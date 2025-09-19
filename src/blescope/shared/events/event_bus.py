import logging
from typing import List, Callable, Dict, Any
from dataclasses import dataclass
import asyncio

@dataclass
class Event:
    name: str
    data: Dict[str, Any]

class EventBus:
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def subscribe(self, event_name: str, handler: Callable):
        if event_name not in self._handlers:
            self._handlers[event_name] = []
        self._handlers[event_name].append(handler)

        self.logger.debug(
            f"Handler {handler.__name__} subscribed to event '{event_name}'"
        )

    async def publish(self, event: Event):
        event_name = event.__class__.__name__
        event_data = {
            k: v for k, v in event.__dict__.items()
            if not k.startswith('_')
        }

        self.logger.info(f"Published event: {event_name}")
        self.logger.debug(f"Event data: {event_data}")

        if event_name in self._handlers:
            handlers = self._handlers.get(event_name)
            self.logger.debug(f"Found {len(handlers)} handlers for event '{event_name}'")

            # Create event wrapper
            wrapped_event = Event(name=event_name, data=event_data)

            # Execute all handlers
            tasks = []
            for handler in handlers:
                try:
                    self.logger.debug(f"Calling handler {handler.__name__}")
                    tasks.append(handler(wrapped_event))
                except Exception as e:
                    self.logger.error(
                        f"Error occurred while calling handler {handler.__name__} for event {event}",
                        exec_info=True
                    )

            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        self.logger.error(
                            f"Handler {handlers[i].__name__} failed: {result}"
                        )
        else:
            self.logger.warning(f"No handlers for event '{event_name}'")
