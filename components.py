from functools import partial
from typing import Literal

from enums import CapStatus, DataChannelStatus

newStatusType = Literal[CapStatus.NEW_CAP, CapStatus.NO_CAP]
dataChannelStatusType = Literal[DataChannelStatus.OPEN, DataChannelStatus.CLOSED]


class UseState:
    """
    A class to store the state of the application.
    This class tries to mimic the useState hook of React.
    """

    def __init__(self, status: str):
        self._status = status
        # return self.status, self.setStatus

    def init(self):
        return self, self.setStatus

    # @property
    # def status(self):
    #     return self._status

    # @status.setter
    # def status(self, value):
    #     self._status = value

    def setStatus(self, value):
        self._status = value

    def __repr__(self):
        return self._status

    def __eq__(self, other):
        return self._status == other


if __name__ == "__main__":
    state1, setState1 = UseState(CapStatus.NEW_CAP).init()
    state2, setState2 = UseState(DataChannelStatus.OPEN).init()
    print(state1, state2)
    setState1(CapStatus.NO_CAP)
    setState2(DataChannelStatus.CLOSED)
    if state1 == "NO_CAP":
        print("new cap")
    print(state1, state2)
