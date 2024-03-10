#!/bin/bash
rpicam-vid -t 0 -n --inline -o - | cvlc stream:///dev/stdin --sout '#rtp{sdp=rtsp://:8080/stream1}' :demux=h264
