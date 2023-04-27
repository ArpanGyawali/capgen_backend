import asyncio
import datetime
import multiprocessing
import pickle
import queue
import random
import threading
import time
from queue import Queue
from threading import Thread
from typing import Callable

import av
import cv2
import numpy as np
import torch
from aiortc import MediaStreamTrack
from aiortc.mediastreams import MediaStreamError
from av import VideoFrame

import initialization
from components import UseState
from config import HyperParameters as HP
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

initialization.init()


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
        self._duration: int = 0
        self._startTime: float = time.time()
        self._endTime: float = None
        self._isReceiving: bool = False

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
        pass

    @staticmethod
    def multiProcessingFunction(
        qimages: multiprocessing.Queue, captionQueue: multiprocessing.Queue
    ):
        while 1:
            # if it is empty block until next istem is available

            images = qimages.get()

            thread = Thread(
                target=VideoCaptionTrack.mythreadFunc, args=(images, captionQueue)
            )

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

    def _sample_incides(self, clip_len, seg_len, frame_sample_rate=4):
        indices = np.linspace(0, seg_len, num=clip_len)
        indices = np.clip(indices, 0, seg_len - 1).astype(np.int64)
        return indices

    def _sample_frames(self, frames):
        # seg_len = len(frames)
        # clip length = model.config.num_image_with_embedding(=6)
        indices = self._sample_incides(clip_len=6, seg_len=len(frames))
        # print(indices)

        return np.array(frames)[indices]

    def _predict_caption(self, pixel_values: np.array, setCaptionState: Callable):
        """
        This function will be running on thread to get the caption
        """

        generated_ids = initialization.model.generate(
            pixel_values=pixel_values, max_length=20
        )
        caption = (
            initialization.processor.batch_decode(
                generated_ids, skip_special_tokens=True
            ),
        )
        # print(caption)
        self._caption = caption[0][0]
        print("DONEEEEEEEEEEEEE")
        print(self._caption)
        setCaptionState(CapStatus.NEW_CAP)

    async def receive(self, setCaptionState):
        if time.time() - self._startTime <= HP.NO_OF_SECONDS:  # 3 seconds
            try:
                frame = await self._track.recv()
                self._startTime = (
                    time.time() if not self._isReceiving else self._startTime
                )
                self._isReceiving = True
            except MediaStreamError as e:
                # print("exception thrown")
                # TODO:  Handle the media exception
                print(e)
                return
            self._count += 1

            # frame.to_image().save(f"frames/frame{self._count}.jpg")
            # img: np.ndarray = frame.to_ndarray(format="rgb24")
            img: np.ndarray = frame.to_ndarray(format="rgb24")

            self._frames.append(img)
            # print(time.time() - self._startTime)

        else:
            # print(len(self._frames), self._frames[0].shape)
            # sample the collected frames
            frames = self._sample_frames(self._frames)




            # # np array without any elements initial-ly
            # frames2 = []
            # for frame in frames:
            #     frame = av.VideoFrame.from_ndarray(frame, format="rgb24")
            #     # frame.decode(video=0)
            #     print("converted av frame: ", type(frame))
            #     cv2.imwrite(f"frames/frame2_{count}.jpg", frames[count])
            #     frames2.append(frame)
            #     # create an "av" package VideoFrame object from the numpy array
            #     count += 1


            # convert each frame into the "av" package VideoFrame object
            frames = np.stack(
                [
                    av.VideoFrame.from_ndarray(frame, format="rgb24").to_ndarray(
                        format="rgb24"
                    )
                    for frame in frames
                ]
            )
            # print(type(frames))
            # print(
            #     frames.shape,
            # )



            start = time.time()

            pixel_values = initialization.processor(
                images=list(frames), return_tensors="pt"
            ).pixel_values

            # frames = torch.tensor(frames).to(device)
            pixel_values = pixel_values.to(initialization.device)

            # ##### THREADING:  THIS IS MOVED INTO THE NEW METHOD AND WILL BE CALLED IN NEW THREAD #####
            # start prediction
            # generated_ids = initialization.model.generate(pixel_values=pixel_values, max_length=20)
            # caption = initialization.processor.batch_decode(generated_ids, skip_special_tokens=True),
            # # print(caption)
            # self._caption = caption[0][0]
            # print("CAPTION: ",self._caption)
            # setCaptionState(CapStatus.NEW_CAP)
            print("new thread started")
            thread = Thread(
                target=self._predict_caption, args=(pixel_values, setCaptionState)
            )

            thread.start()

            # print(time.time() - start)

            # ? Reset all attributes
            self._count = 0
            # frames = np.stack(frame for frame in self._frames)
            # sample the frames
            self._frames = []
            self._startTime = time.time()

        # print("COUNT", self._count)
