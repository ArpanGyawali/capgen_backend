import enum


class CapStatus(str, enum.Enum):
    NEW_CAP = "NEW_CAP"
    NO_CAP = "NO_CAP"


class DataChannelStatus(str, enum.Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class PeerConnectionStatus(str, enum.Enum):
    CONNECTED = "connected"
    CONNECTING = "connecting"
    CLOSED = "closed"
    FAILED = "failed"
    NEW = "new"
