from dataclasses import dataclass


@dataclass
class AttendanceRecord:
    id: str
    date: str
    status: str
