#!/usr/bin/env python3
"""Demonstrates manual operation of up to 8 sprinkler valves via a web interface using an OpenSprinkler Pi board."""

__author__ = "Carlos Adrian Gomez"

from sys import argv, exit
from http.server import BaseHTTPRequestHandler, HTTPServer
import RPi.GPIO as GPIO
import urllib.parse
import os
import atexit

MAX_STATIONS = 8
server, stationControl = None, None;
ON, OFF = 1, 0

class StationControl(object):
    # GPIO Pins (BCM numbering). OSPI uses 4 pins for shift register.
    clock_pin =  4
    out_pin = 17
    data_pin = 27
    latch_pin = 22

    def __init__(self, stations):
        self.numStations = stations
        self.stationIds = []
        for i in range(0, self.numStations):
            self.stationIds.append(i)
        print("StationControl instantiated with stations: {} ".format(self.stationIds))
        self.stationStatus = [OFF] * self.numStations
        self.setupPinOutput();

    def setStation(self, station, signal):
        if station in self.stationIds and signal in [OFF, ON]:
            self.stationStatus[station] = signal
            print("Set Station {} to {}".format(station + 1, 'ON' if signal else 'OFF'))
            return True
        else:
            return False

    def resetStations(self):
        self.stationsStatus = [OFF] * self.numStations

    def toggleShiftRegisterOutput(self, value):
        if value:
            GPIO.output(StationControl.out_pin, False)
        else:
            GPIO.output(StationControl.out_pin, True)

    def setShiftRegisterValues(self):
        GPIO.output(StationControl.clock_pin, False)
        GPIO.output(StationControl.latch_pin, False)
        for station in range(0, self.numStations):
            GPIO.output(StationControl.clock_pin, False)
            GPIO.output(StationControl.data_pin, self.stationStatus[self.numStations - 1 - station])
            GPIO.output(StationControl.clock_pin, True)
        GPIO.output(StationControl.latch_pin, True)

    def setupPinOutput(self):
        # clean up after any previous applications
        GPIO.cleanup()
        # setup GPIO pins to interface with shift register
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(StationControl.clock_pin, GPIO.OUT)
        GPIO.setup(StationControl.out_pin, GPIO.OUT)
        self.toggleShiftRegisterOutput(False)
        GPIO.setup(StationControl.data_pin, GPIO.OUT)
        GPIO.setup(StationControl.latch_pin, GPIO.OUT)
        self.setShiftRegisterValues()
        self.toggleShiftRegisterOutput(True)

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith('.js') or self.path.endswith('.css'):
                # send client the assets requested
                self.send_response(200)
                if self.path.endswith('.js'):
                    print ("Sending JS to client")
                    self.send_header('Content-type','text/html')
                else:
                    print ("Sending CSS to client")
                    self.send_header('Content-type','text/css')
                self.end_headers()
                asset = open('.' + self.path)
                self.wfile.write(asset.read().encode('utf-8'))
                asset.close()
                return
            elif '/req?' in self.path:
                print ("Processing Button click")
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()
                parsed=urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
                stationId = int(parsed['stationId'][0])
                signal  = int(parsed['signal'][0])
                if stationControl.setStation(stationId, signal):
                    stationControl.setShiftRegisterValues()
                # send client back to index
                self.wfile.write('<script>window.location=\".\";</script>'.encode('utf-8'))
            else:
                # client requested '/' or any other path; write stations to page
                self.send_response(200)
                print ("Writing stations to page")
                self.send_header('Content-type','text/html')
                self.end_headers()
                self.wfile.write('<script>\nvar numStations='.encode('utf-8'))
                self.wfile.write(str(stationControl.numStations).encode('utf-8'))
                self.wfile.write(', stations=['.encode('utf-8'))
                for station in range(0, stationControl.numStations):
                    self.wfile.write(str(stationControl.stationStatus[station]).encode('utf-8'))
                    self.wfile.write(','.encode('utf-8'))
                self.wfile.write('0];\n</script>\n'.encode('utf-8'))
                self.wfile.write('<script src=\'page.js\'></script>'.encode('utf-8'))
        except IOError:
            self.send_error(404, 'File not found')

def setNumStations(argv):
    numStations = 0
    try:
        numStations = int(argv[1])
        if numStations > MAX_STATIONS:
            numStations = MAX_STATIONS
    except (IndexError, ValueError):
        pass
    if numStations == 0:
        numStations = MAX_STATIONS
    return numStations

def progexit():
    print("\nCleaning up...")
    GPIO.cleanup()
    global stationControl, server
    stationControl.resetStations()
    server.socket.close()

def main(argv):
    atexit.register(progexit)
    GPIO.setwarnings(False);
    global stationControl, server
    numStations = setNumStations(argv)
    stationControl = StationControl(numStations)
    try:
        server_address = ('0.0.0.0', 8080)
        server = HTTPServer(server_address, MyHandler)
        print('Cloudwater listening on port {}...'.format(server_address[1]))
        server.serve_forever()
    except KeyboardInterrupt:
        exit() 

if __name__ == '__main__':
    main(argv)
