#!/usr/bin/env python3

# Copyright (c) 2017-2020 Richard Hull and contributors
# Copyright (c) 2021 Future Corporation
# SPDX-License-Identifier: MIT License

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
import PIL
from PIL import ImageFont
import psutil
import os, sys, time
from pathlib import Path
from datetime import datetime
import multiprocessing
import distro
import platform

REFRESH_INTERVAL = 1
SCREEN_TIMEOUT = 20

# Use a custom font
font_path = str(Path(__file__).resolve().parent.joinpath('../fonts', 'CCRedAlert.ttf'))
font2 = ImageFont.truetype(font_path, 12)

def bytes2human(n):
    """
    >>> bytes2human(10000)
    '9K'
    >>> bytes2human(100001221)
    '95M'
    """
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = int(float(n) / prefix[s])
            return '%s%s' % (value, s)
    return "%sB" % n

def cpu_usage():
    # load average, uptime
    uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
    av1, av2, av3 = os.getloadavg()
    return "Ld:%.1f %.1f %.1f Up: %s" \
        % (av1, av2, av3, str(uptime).split('.')[0])

def mem_usage():
    usage = psutil.virtual_memory()
    return "Mem: %s %.0f%%" \
        % (bytes2human(usage.used), 100 - usage.percent)

def disk_usage(dir):
    usage = psutil.disk_usage(dir)
    return "Disk:  %s %.0f%%" \
        % (bytes2human(usage.used), usage.percent)

def ip_addr(intf):
    ip = psutil.net_if_addrs()[intf][0][1]
    return "%s: %s" % (intf, ip)

def displaystats(device):
    with canvas(device) as draw:
        draw.text((0, 0), cpu_usage(), font=font2, fill="white")
        draw.text((0, 14), mem_usage(), font=font2, fill="white")
        draw.text((0, 26), disk_usage('/'), font=font2, fill="white")
        try:
            draw.text((0, 38), ip_addr('eth0'), font=font2, fill="white")
        except KeyError:
            # No network
            pass

        try:
            draw.text((0, 50), ip_addr('wlp5s0'), font=font2, fill="white")
        except KeyError:
            pass

def displaytemps(device):
    with canvas(device) as draw:
        draw.text((0, 0), "System Temperatures", font=font2, fill="white")
        try:
            draw.text((0, 24), "CPU: %s°C" % (str(psutil.sensors_temperatures()['tmp451'][1][1])), font=font2, fill="white")
        except:
            pass

        try:
            draw.text((0, 36), "NVMe: %s°C" % (str(psutil.sensors_temperatures()['nvme'][2][1])), font=font2, fill="white")
        except:
            pass

        try:
            draw.text((0, 48), "GPU: %s°C" % (str(psutil.sensors_temperatures()['nouveau'][0][1])), font=font2, fill="white")
        except:
            pass

def init_histogram():
    # HistogramSettings
    histogramResolution = 100
    histogramTime = []
    histogramData = []
    x = 106
    # Filling up the arrays for the histogram
    for pix in range(0, histogramResolution):
        x -= 2
        if x > 2:
            histogramTime.append(x)

    for timeLen in range(0, len(histogramTime)):
        histogramData.append(60)

    return histogramData, histogramTime

def histogram(device, histogramData, histogramTime):
    # Getting system uptime
    sysUptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())

    # RAM bar
    minRamBarH = 15
    maxRamBarH = 25
    minRamBarW = 3
    maxRamBarW = 105
    ramStat = psutil.virtual_memory()
    ramTot = ramStat.total >> 20
    ramUsd = ramStat.used >> 20
    ramPerc = (ramUsd / ramTot) * 100
    ramBarWidth = (((100 - ramPerc) * (minRamBarW - maxRamBarW)) / 100) + maxRamBarW

    # Temp bar
    maxBarHeight = 60
    minBarHeight = 3

    try:
        tmpCel = int(psutil.sensors_temperatures()['tmp451'][1][1])
    except Exception as e:
        tmpCel = 0

    #with open("/sys/class/thermal/thermal_zone0/temp", "r") as temp:
    #tmpCel = int(temp.read()[:2])
    tmpPercent = (tmpCel / 55) * 100

    height = (((100 - tmpPercent) * (maxBarHeight - minBarHeight)) / 100) + minBarHeight

    # Histogram graph
    cpuLoad = os.getloadavg()
    cpuPercent = (cpuLoad[0] / multiprocessing.cpu_count()) * 100
    minHistHeight = 60
    maxHistHeight = 30
    minHistLenght = 3
    maxHistLenght = 105
    histogramHeight = (((100 - cpuPercent) * (minHistHeight - maxHistHeight)) / 100) + maxHistHeight

    # Starting the canvas for the screen
    try:
        with canvas(device, dither=True) as draw:
            # Print
            # Drawing the outlines and legends:
            # Main Outline
            draw.rectangle(device.bounding_box, outline="white")

            # Histogram Outline
            draw.rectangle((minHistLenght, maxHistHeight, maxHistLenght, minHistHeight), outline="white")
            draw.rectangle((110, minBarHeight, 124, maxBarHeight), outline="white")
            draw.rectangle((104, minBarHeight, 110, minBarHeight + 8), fill="white")

            # Thermometer outline and legend
            draw.text((105, minBarHeight - 1), 'C', fill="black")

            # RAM bar outline and legend
            draw.rectangle((minRamBarW, minRamBarH, maxRamBarW, maxRamBarH))
            draw.text((maxRamBarW - 18, minRamBarH), 'RAM', fill="white")

            # System Uptime
            draw.text((3, 2), "Uptime: " + str(sysUptime)[:7], fill="white")

            # RAM usage bar
            if ramBarWidth < maxRamBarW:
                draw.rectangle((minRamBarW, minRamBarH, ramBarWidth, maxRamBarH), fill="white")
                if ramUsd < 100:
                    draw.text((ramBarWidth - 11, minRamBarH), str(ramUsd), fill="black")
                else:
                    draw.text((ramBarWidth - 17, minRamBarH), str(ramUsd), fill="black")
            else:
                draw.rectangle((minRamBarW, minRamBarH, maxRamBarW, maxRamBarH), fill="red")

            # Histogram
            histogramData.insert(0, histogramHeight)
            for htime in range(0, len(histogramTime) - 1):
                timePlusOne = htime + 1
                if histogramData[0] > maxHistHeight:
                    draw.line((histogramTime[timePlusOne], histogramData[timePlusOne], histogramTime[htime], histogramData[htime]), fill="orange")
                else:
                    histogramData[0] = maxHistHeight
                    draw.text(((minHistLenght + maxHistLenght) / 2, (maxHistHeight + minHistHeight) / 2), "WARNING!", fill="white")
                    draw.line((histogramTime[timePlusOne], histogramData[timePlusOne], histogramTime[htime], histogramData[htime]), fill="orange")

            histogramData.pop(len(histogramTime) - 1)
            draw.rectangle((minHistLenght, maxHistHeight, minHistLenght + 27, maxHistHeight + 13), fill="black", outline="white")
            draw.text((minHistLenght + 2, maxHistHeight + 2), "{0:.2f}".format(cpuLoad[0]), fill="white")

            # CPU Temperature
            if height > minBarHeight:
                draw.rectangle((112, height, 122, maxBarHeight), fill="gray")
                draw.rectangle((110, height, 124, height + 10), fill="white")
                draw.text((112, height), str(tmpCel), fill="black")
            else:
                draw.rectangle((110, minBarHeight, 124, maxBarHeight), outline="white")
                if blnk == 1:
                    draw.rectangle((112, minBarHeight, 122, maxBarHeight), fill="gray")
                    draw.rectangle((110, minBarHeight, 124, minBarHeight + 10), fill="white")
                    draw.text((112, minBarHeight), str(tmpCel), fill="black")
                    blnk = 0
                else:
                    draw.rectangle((110, minBarHeight, 124, minBarHeight + 10), fill="black", outline="white")
                    draw.text((112, minBarHeight), str(tmpCel), fill="white")
                    blnk = 1

    except Exception as e:
        pass

def system_info(device):
    with canvas(device) as draw:
        draw.text((0, 0), "Future RISC-V PC", font=font2, fill="white")
        draw.text((0, 14), "{0} {1}".format(distro.os_release_info()['name'], distro.os_release_info()['version']), font=font2, fill="white")
        draw.text((0, 26), platform.platform(), font=font2, fill="white")

def main():
    serial = i2c(port=0, address=0x3C)
    device = ssd1306(serial)

    histogramData, histogramTime = init_histogram()

    while True:
        displaystats(device)
        time.sleep(SCREEN_TIMEOUT)

        i = 0
        while i < 10:
            histogram(device, histogramData, histogramTime)
            time.sleep(1)
            i = i + 1

        system_info(device)
        time.sleep(SCREEN_TIMEOUT)
        displaytemps(device)
        time.sleep(SCREEN_TIMEOUT)

if __name__ == '__main__':
    main()
