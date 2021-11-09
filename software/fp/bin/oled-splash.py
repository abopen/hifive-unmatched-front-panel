#!/usr/bin/env python3

# Copyright (c) 2017-2020 Richard Hull and contributors
# Copyright (c) 2021 Future Corporation
# SPDX-License-Identifier: MIT License

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from pathlib import Path
import PIL

serial = i2c(port=0, address=0x3C)
device = ssd1306(serial)

# Don't clear the display upon exit

def do_nothing(obj):
    pass

device.cleanup = do_nothing

# Display the splash image

img_file = str(Path(__file__).resolve().parent.joinpath('../images', 'splash.png'))
splash = PIL.Image.open(img_file).convert(device.mode)
device.display(splash)
