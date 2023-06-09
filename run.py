#!/usr/bin/python3
import os

cwd = os.getcwd()

os.chdir("/home/sawa/mainShare/devenv/gitrepos/riotMatchHistory/flask/")
os.system("nohup python3 routes.py > routes.logs 2>&1 &")

os.chdir("/home/sawa/mainShare/devenv/gitrepos/riotMatchHistory/")
os.system("nohup python3 bot.py > bot.logs 2>&1 &")

