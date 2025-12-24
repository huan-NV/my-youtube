"""
Module Timeline - parse và quản lý sự kiện timeline cho scenes.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class EventType(Enum):
    """Các loại sự kiện timeline."""

    SPAWN = "spawn"
    MOVE = "move"
    DIALOG = "dialog"
    IDLE = "idle"
    EXIT = "exit"


@dataclass
class TimelineEvent:
    """Đại diện cho một sự kiện timeline đơn."""

    event_type: EventType
    actor_id: str
    start_time: float
    duration: float
    data: Dict[str, Any]

    @property
    def end_time(self) -> float:
        """Lấy thời điểm kết thúc của sự kiện này."""
        return self.start_time + self.duration


class Timeline:
    """Quản lý sự kiện timeline cho một scene."""

    def __init__(self, events: List[TimelineEvent]):
        """
        Khởi tạo timeline với các sự kiện.

        Args:
            events: Danh sách sự kiện timeline (nên được sắp xếp theo start_time)
        """
        self.events = sorted(events, key=lambda e: e.start_time)
        self._actor_events: Dict[str, List[TimelineEvent]] = {}

        # Nhóm sự kiện theo actor
        for event in self.events:
            if event.actor_id not in self._actor_events:
                self._actor_events[event.actor_id] = []
            self._actor_events[event.actor_id].append(event)

    def get_events_for_actor(self, actor_id: str) -> List[TimelineEvent]:
        """Lấy tất cả sự kiện cho một actor cụ thể, được sắp xếp theo start_time."""
        return self._actor_events.get(actor_id, [])

    def get_events_at_time(self, t: float) -> List[TimelineEvent]:
        """Lấy tất cả sự kiện đang hoạt động tại thời điểm t."""
        return [e for e in self.events if e.start_time <= t < e.end_time]

    def get_dialog_events(self) -> List[TimelineEvent]:
        """Lấy tất cả sự kiện dialog."""
        return [e for e in self.events if e.event_type == EventType.DIALOG]

    def get_total_duration(self) -> float:
        """Lấy tổng thời lượng của timeline."""
        if not self.events:
            return 0.0
        return max(e.end_time for e in self.events)

    @staticmethod
    def from_json(timeline_data: List[Dict[str, Any]]) -> "Timeline":
        """
        Tạo Timeline từ dữ liệu JSON.

        Args:
            timeline_data: Danh sách dictionary sự kiện

        Returns:
            Instance Timeline
        """
        events = []

        for event_data in timeline_data:
            event_type = EventType(event_data["type"].lower())
            actor_id = event_data["actor_id"]
            start_time = float(event_data["start_time"])
            duration = float(event_data.get("duration", 0.0))

            # Trích xuất dữ liệu cụ thể cho sự kiện
            data = {
                k: v
                for k, v in event_data.items()
                if k not in ["type", "actor_id", "start_time", "duration"]
            }

            event = TimelineEvent(
                event_type=event_type,
                actor_id=actor_id,
                start_time=start_time,
                duration=duration,
                data=data,
            )

            events.append(event)

        return Timeline(events)
