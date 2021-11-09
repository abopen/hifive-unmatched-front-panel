# HiFive Unmatched Front Panel

![Custom Front Panel](/images/Front_Panel_1_1024w.jpg)

A custom front panel for the [SiFive HiFive Unmatched](https://www.sifive.com/boards/hifive-unmatched),
designed in KiCAD and featuring:

* OLED display
* Power button
* Reset button
* 2x GPIO buttons

With Python examples to drive the OLED display.

## Details

The display interfaces via I2C and operates on 3v3 logic levels, with the HiFive
Unmatched using 1v8 on its GPIO header, hence the board includes level shifting.

Power and reset buttons are connected to the Front Panel header.

An additional two buttons are provided for general use — e.g. screen pagination
— and these are connected to the GPIO header.

All the buttons are illuminated, however, this is not under software control and
the buttons simply illuminate when the HiFive Unmatched is powered on.

## Licence

HiFive Unmatched Front Panel is copyright 2021 Future Corporation.

The PCB design is published under the CERN Open Hardware Licence Version 2 -
Weakly Reciprocal (CERN-OHL-W).

The Python examples are published under the MIT License.

## About Future Corporation

[Future Corporation](https://www.future.co.jp/en/) in Japan is a company that conducts "IT Consulting & Service
Business" and "Innovation Business" through the use of latest technology. 
Since the founding in 1989, we have designed and improved the business of our
clients through developing systems that integrates business management with IT.
Our clients are from various industries including Finance, Manufacturing,
Distribution and Logistics. 
We have also created our own new services based on the know-how we have
accumulated in this process.
We are contributing to the society by promoting innovation and creating new
values for clients that is based on the strengths of "connoisseurship" and
"implementation ability" of latest technologies such as AI and robotics.
