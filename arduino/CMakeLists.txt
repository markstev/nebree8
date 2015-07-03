#=============================================================================#
# Author: MarkStevens
# Date:   2012/04/17
#                                                                             #
# Description: Playing around with serial communication protocol              #
#                                                                             #
#=============================================================================#

cmake_minimum_required(VERSION 2.8)
#====================================================================#
#  Settings                                                          #
#====================================================================#

set(CMAKE_SOURCE_DIR /home/pi/nebree82/nebree8/arduino) # Source dir
set(CMAKE_TOOLCHAIN_FILE ${CMAKE_SOURCE_DIR}/cmake/ArduinoToolchain.cmake) # Arduino Toolchain

project(ArduinoExample C CXX)
set(ARDUINO_SDK /usr/share/arduino-1.0.6)
set(FIRMWARE_NAME uc_io_bank)


set(${FIRMWARE_NAME}_BOARD mega2560)               # Arduino Target board
set(${FIRMWARE_NAME}_SRCS  uc_io_bank.cc)

set(${FIRMWARE_NAME}_PORT /dev/ttyACM0)            # Serial upload port
link_directories(/home/pi/nebree82/nebree8/arduino)
link_directories(/home/pi/nebree82/nebree8/arduino/MS5803)
set(${FIRMWARE_NAME}_LIBS MS5803)  # Pressure sensor library.
set(${FIRMWARE_NAME}_NO_AUTOLIBS false)

#====================================================================#
#  Target generation                                                 #
#====================================================================#
generate_arduino_firmware(${FIRMWARE_NAME})
target_link_libraries(${FIRMWARE_NAME} LINK_PUBLIC MS5803)
