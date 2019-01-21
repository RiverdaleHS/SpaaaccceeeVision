#!/bin/bash
v4l2-ctl -d /dev/video0 -c brightness=40
v4l2-ctl -d /dev/video0 -c backlight_compensation=0
v4l2-ctl -d /dev/video0 -c white_balance_temperature_auto=0
v4l2-ctl -d /dev/video0 -c sharpness=50
v4l2-ctl -d /dev/video0 -c saturation=50
v4l2-ctl -d /dev/video0 -c contrast=0
v4l2-ctl -d /dev/video0 -c exposure_auto=1
v4l2-ctl -d /dev/video0 -c exposure_absolute=5

