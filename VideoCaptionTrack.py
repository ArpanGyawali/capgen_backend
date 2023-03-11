import asyncio
import random
from threading import Thread
import multiprocessing


import cv2
import numpy as np
from aiortc import MediaStreamTrack
from aiortc.mediastreams import MediaStreamError
from av import VideoFrame

import predict
from components import UseState
from enums import CapStatus, DataChannelStatus, PeerConnectionStatus
from exceptions import ConnectionClosed

captionList = [
    "sdasd",
    "asdasdasdasdas",
    "asdasdasdasdasdasds",
    "asdasdsadasdasdasdasdadasdsa",
]


class VideoCaptionTrack:
    """
    A video stream track that transforms frames from an another track of frames with captions.
    """

    def __init__(self, track):
        self._track = track
        self._count = 0
        self._frames = []

        self._caption = ""
        # self._threads= []

    def mythreadFunc(self, images, setCaptionState):
        caption = predict.test(images)
        # self._isNewCap = True
        setCaptionState(CapStatus.NEW_CAP)
        self._caption = caption

    @property
    def isNewCap(self):
        return self._isNewCap

    @property
    def caption(self):
        return self._caption

    @isNewCap.setter
    def isNewCap(self, value):
        self._isNewCap = value

    async def receive(self, connectionState, setCaptionState):
        try:
            frame = await self._track.recv()
        except MediaStreamError as e:
            print("exception thrown")

            # TODO:  Kill all the incomplete running threads

            print(e)
            return
        self._count += 1
        # print('**********' + str(self.count) + '*********')
        # frame.to_image().save("frame.jpg")
        img = frame.to_ndarray(format="rgb24")
        # print(img)
        # cv2.imshow("frame", img)

        if self._count <= 80:
            image = cv2.resize(img, (224, 224))
            # frame = cv2.resize(frame, (224, 224, 3))
            self._frames.append(image)
        elif self._count == 81:
            self._count = 0
            images = np.array(self._frames)
            self._frames = []
            # await asyncio.sleep(3)
            # self._isNewCap = True
            # random_num = random.randint(0, 3)
            # sel9f._caption = captionList[random_num]
            print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
            print(images.shape)
            print('$&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
            thread = Thread(target=self.mythreadFunc, args=(images,))
            # self._threads.append(thread)
            thread.start()
        print(self._count)
