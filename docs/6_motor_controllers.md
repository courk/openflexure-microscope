# Motor controller boards

The motorised version of the microscope uses a motor controller based on an Arduino and some very simple Darlington pair driver chips.  There are several options for how to build this, which should all work equally well.  In all cases, you need to upload the [Sangaboard arduino sketch] using the Arduino IDE.

Three "official" designs for the Sangaboard exist, and these are described below.

## Board designs

### Simple controller using Arduino Nano

Most recommended [motors](./5_motors.md) will come packaged with a simple driver board. These can be connected to an Arduino Nano and a power supply following the diagram below.

![Simple motor controller with Arduino](./images/sangaboard_simple.png)

Then, use the Arduino IDE to upload the [Sangaboard arduino sketch], and connect the Arduino to your microscope's Raspberry Pi via its USB port.

> **Warning:** Do not attempt to power the motors from the Raspberry Pi's pins. They can draw far more than the maximum current the Pi will safely supply. Always use a separate power supply for the motors.

When you boot up the Raspberry Pi, the microscope software should recognise a supported Sangaboard is connected, and enable motorised control of the microscope stage.

[Sangaboard arduino sketch]: https://gitlab.com/bath_open_instrumentation_group/sangaboard/tree/master/arduino_code

### PCB + Arduino Nano (Sangaboard v0.2)

This option aims to be a super-simple motor controller board, based on an Arduino Nano and a couple of Darlington pair ICs. Electrically, it is more or less identical to the previous option, but replaces the messy wiring with a PCB.  It owes quite a bit to [Fergus Riche's motor board](https://github.com/fr293/motor_board), the hardware developed by [OpenScope](http://2015.igem.org/Team:Cambridge-JIC) and the Arduino-based motor controller used by a number of summer students working with Richard Bowman in Cambridge, particularly James Sharkey.

The PCB design, bill of materials, and purchase links for both are available via [Kitspace](https://kitspace.org/boards/github.com/rwb27/openflexure_nano_motor_controller/).  You can see an image of the [circuit schematic](./images/sangaboard_v2_schematic.png ':ignore')


### Fully integrated board (Sangaboard v0.3)

A fully-custom, Arduino-like board can also be used to drive the microscope motors. The Sangabord v0.3 design integrates everything onto a single PCB, removing the need to plug in a separate Arduino.  It uses the same Arduino sketch as the other options, but the Arduino is now integrated into the PCB.  This is easier to use if you are having boards made externally.

The PCB design, bill of materials, and purchase links for both are also available via [Kitspace](https://kitspace.org/boards/gitlab.com/bath_open_instrumentation_group/sangaboard/).

If building or ordering your own custom board, you will first need to burn the [custom bootloader], before uploading the [Sangaboard arduino sketch].

[custom bootloader]: https://gitlab.com/bath_open_instrumentation_group/sangaboard/blob/master/Bootloader/README.md

## Arduino code

All of the motor board options are Arduino-compatible, and use the same [Sangaboard arduino sketch].  This is referred to as the "firmware" in various places.  If you are using a purchased Arduino, it should have a bootloader on it already, so all you need to do is upload the sketch, and you should be good to go.

> **N.B.** some people have reported that the sketch won't upload properly to cheap Arduino Nano clones.  There are a couple of issues here - firstly, you may need to install USB-to-serial drivers for the CH340 chip used in these clones (the FTDI chip used by genuine Arduinos has drivers built in to Windows, the cheaper chips don't).  Secondly, if you are using a new version of the Arduino IDE, you may need to select the "old bootloader" option (in the board menu where you select the processor).

If you are using one of the boards with an integrated microcontroller rather than a discrete Arduino Nano board, your microcontroller may not come with a preinstalled bootloader.  You must flash either the Arduino bootloader, or our [custom bootloader].  The [custom bootloader] makes the motor board show up as a "Sangaboard" rather than an Arduino, but it is otherwise identical to the Arduino bootloader.
