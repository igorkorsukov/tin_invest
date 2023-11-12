import os
import time
import signal

from tinkoff.invest import Client

import modules.bonds_divergence as bonds_divergence

TOKEN = os.environ["INVEST_TOKEN"]

running = True

def signal_handler(signum, frame):
    global running
    running = False

def main():

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    with Client(TOKEN) as client:   

        div = bonds_divergence.divergence(client) 
        print(div) 

        # loop
        counter = 0
        while(running):
            if counter % 5 == 0:
                div = bonds_divergence.divergence(client) 
                print(div) 

            time.sleep(1)
            counter += 1

if __name__ == "__main__":
    main()