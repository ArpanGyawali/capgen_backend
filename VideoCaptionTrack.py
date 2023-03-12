import asyncio
import datetime
import multiprocessing
import pickle
import queue
import random
import threading
from queue import Queue
from threading import Thread

import cv2
import dill
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


def print_square(*args):
    """
    function to print square of given num
    """
    print(f"Square: {100 * 100}")


qimages: multiprocessing.Queue = multiprocessing.Queue(maxsize=5)
captionQueue: multiprocessing.Queue = multiprocessing.Queue(maxsize=10)


class VideoCaptionTrack:
    """
    A video stream track that transforms frames from an another track of frames with captions.
    """

    def __init__(self, track: MediaStreamTrack):
        self._track: MediaStreamTrack = track
        self._count: int = 0
        self._frames: list = []
        self._process: multiprocessing.Process = None

        self._caption: str = ""

        # self._setCaptionState = multiprocessing.Value("i", 0)

    @staticmethod
    def test_function():
        for i in range(100):
            print(i)

    @property
    def isNewCap(self):
        return self._isNewCap

    @property
    def caption(self):
        return self._caption

    @isNewCap.setter
    def isNewCap(self, value):
        self._isNewCap = value

    @staticmethod
    def mythreadFunc(images, captionQueue: multiprocessing.Queue):
        print("PROCESSING IMAGES")

        while 1:
            print("inside thread")
        # caption = predict.test(images)
        # a = caption
        captionQueue.put("new caption")

        # self._isNewCap = True
        # setCaptionState(CapStatus.NEW_CAP)
        print("CAPTION SET")
        # self._caption = caption

    @staticmethod
    def multiProcessingFunction(
        qimages: multiprocessing.Queue, captionQueue: multiprocessing.Queue
    ):
        while 1:
            # if it is empty block until next istem is available
            print("WAITING FOR IMAGES")
            images = qimages.get()
            print("GOT IMAGES FROM QUEUE")
            thread = Thread(
                target=VideoCaptionTrack.mythreadFunc, args=(images, captionQueue)
            )
            # thread = Thread(target=self.fn, args=())
            thread.start()

    def startMultiProcessing(self):
        self._process = multiprocessing.Process(
            target=VideoCaptionTrack.multiProcessingFunction,
            args=(
                qimages,
                captionQueue,
            ),
        )
        print("PROCESS STARTING")
        self._process.start()
        print("PROCESS STARTED")

    def killMultiProcesses(self):
        print("TERMINTING THE PROCESSES")
        self._process.terminate()
        print("PROCESSES TERMINATED")

    async def receive(self, setCaptionState):
        if captionQueue.qsize() > 0:
            print("CAPTION CHANGED")
            self._caption = captionQueue.get()
            # self._isNewCap = True
            setCaptionState(CapStatus.NEW_CAP)
            print("CAPTION SET")
            # self._caption = caption

        try:
            frame = await self._track.recv()
        except MediaStreamError as e:
            # print("exception thrown")
            # TODO:  Kill all the incomplete running threads

            # print("TERMINATING THE PROCCESS(ALL THREADS)")
            # self.killMultiProcesses()

            print(e)
            return
        self._count += 1
        # print('**********' + str(self.count) + '*********')
        # frame.to_image().save("frame.jpg")
        img: np.ndarray = frame.to_ndarray(format="rgb24")
        # print(img)
        # cv2.imshow("frame", img)

        if self._count <= 80:
            print(img.shape)
            # image = cv2.resize(img, (224, 224))
            # frame = cv2.resize(frame, (224, 224, 3))
            self._frames.append(img)
        elif self._count == 81:
            self._count = 0
            images = np.array(self._frames)
            self._frames = []
            # await asyncio.sleep(3)
            # self._isNewCap = True
            # random_num = random.randint(0, 3)
            # sel9f._caption = captionList[random_num]

            # thread = Thread(target=self.mythreadFunc, args=(images,))

            # store images in the queue
            # Qimages.put(images)
            qimages.put(images)
            print(qimages.qsize())
            # thread.start()
        print("COUNT", self._count)
