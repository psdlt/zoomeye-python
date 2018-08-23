#!/usr/bin/env python3

from ZoomEye import ZoomEye
import signal


def signal_handler(signal, frame):
    print('Aborting..')
    quit()


signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    zm = ZoomEye("memcached +port:'11211'", "YOUR_ZOOMEYE_EMAIL", "YOUR_ZOOMEYE_PASSWORD", page=1, verbose=True)
    resource = zm.resource_info()
    print("Search hits remaining: %s" % resource)

    try:
        token = zm.login()
        while 1:
            result = zm.next_page()
            if not result:
                print("EOF")
                quit()

            for item in result:
                print("%s:%s (%s)" % (item["ip"], item["port"], item["country"]))

    except ConnectionError as err:
        print("Connection error: %s" % err)
        quit()
