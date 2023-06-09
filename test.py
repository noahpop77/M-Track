import threading
import time

event = threading.Event()

def myfunction():
    print("Waiting for event to trigger...")
    event.wait()
    print("Performing event action!...")

t1 = threading.Thread(target=myfunction)
t1.start()

x = input("Wanna trigger the event? (y/n)")
if x == "y":
    event.set()