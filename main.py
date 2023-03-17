import argparse
import asyncio
import enum
import json
import logging
import os
import ssl
import uuid
from typing import Literal

import aiohttp_cors
import PIL
from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRelay
import settings

from components import UseState
from enums import CapStatus, DataChannelStatus, PeerConnectionStatus
from exceptions import ConnectionClosed
from VideoCaptionTrack import VideoCaptionTrack

ROOT = os.path.dirname(__file__)

logger = logging.getLogger("pc")
pcs = set()
relay = MediaRelay()
settings.init()


# Define the states of the application
dataChannelState, setDataChannelState = UseState(DataChannelStatus.CLOSED).init()
captionState, setCaptionState = UseState(CapStatus.NO_CAP).init()


async def offer(request):
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()
    pc_id = "PeerConnection(%s)" % uuid.uuid4()
    # create a data channel

    channel = pc.createDataChannel("chat")

    @channel.on("open")
    def on_open():
        print("channel opened")
        setDataChannelState(DataChannelStatus.OPEN)
        # channel.send("Hello from backend via Datachannel")

    @channel.on("close")
    def on_close():
        print("channel closed")
        setDataChannelState(DataChannelStatus.CLOSED)

    pcs.add(pc)

    def log_info(msg, *args):
        logger.info(pc_id + " " + msg, *args)

    log_info("Created for %s", request.remote)

    # prepare local media
    player = MediaPlayer(os.path.join(ROOT, "demo-instruct.wav"))
    recorder = MediaBlackhole()

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        log_info("Connection state is %s", pc.connectionState)
        if pc.connectionState == "failed":
            await pc.close()
            pcs.discard(pc)

    # A  ------------------------->B

    @pc.on("track")
    async def on_track(track):
        log_info("Track %s received", track.kind)

        if track.kind == "audio":
            pc.addTrack(player.audio)
            recorder.addTrack(track)
        elif track.kind == "video":
            print("track added")

            videoTrack = VideoCaptionTrack(track)
            

            while 1:
                # print(
                #     pc.connectionState == PeerConnectionStatus.CONNECTED
                #     and dataChannelState == DataChannelStatus.CLOSED
                # )
                communicationState = [pc.connectionState, dataChannelState]
                if (
                    pc.connectionState == PeerConnectionStatus.CONNECTED
                    and dataChannelState == DataChannelStatus.CLOSED
                ):
                    
                    break

                await videoTrack.receive(setCaptionState)
                
                # waits for 0.8 seconds
                await asyncio.sleep(0.4)

                # print(captionState)

                if captionState == CapStatus.NEW_CAP:
                    setCaptionState(CapStatus.NO_CAP)
                    channel.send(videoTrack.caption)

 

        print("track subscribed")


        @track.on("ended")
        async def on_ended():
            log_info("Track %s ended", track.kind)
            await recorder.stop()

    # handle offer
    await pc.setRemoteDescription(offer)
    await recorder.start()

    # send answer
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
        ),
    )


async def on_shutdown(app):
    # close peer connections
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()


app = web.Application()
cors = aiohttp_cors.setup(app)
app.on_shutdown.append(on_shutdown)
app.router.add_post("/offer", offer)

for route in list(app.router.routes()):
    cors.add(
        route,
        {
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*",
            )
        },
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="WebRTC audio / video / data-channels demo"
    )
    parser.add_argument("--cert-file", help="SSL certificate file (for HTTPS)")
    parser.add_argument("--key-file", help="SSL key file (for HTTPS)")
    parser.add_argument(
        "--host", default="0.0.0.0", help="Host for HTTP server (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", type=int, default=8080, help="Port for HTTP server (default: 8080)"
    )
    parser.add_argument("--record-to", help="Write received media to a file."),
    parser.add_argument("--verbose", "-v", action="count")
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if args.cert_file:
        ssl_context = ssl.SSLContext()
        ssl_context.load_cert_chain(args.cert_file, args.key_file)
    else:
        ssl_context = None

    web.run_app(
        app, access_log=None, host=args.host, port=args.port, ssl_context=ssl_context
    )
