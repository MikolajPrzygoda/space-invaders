#!/bin/bash
#You must have pyinstaller (duh) and pygame to build the project
pyinstaller main.py -F --add-data assets:assets -n Space\ Invaders
