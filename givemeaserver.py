#!/usr/bin/env python2.7
from datetime import datetime
from ConfigParser import ConfigParser
import argparse
import os
import sys

from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

import iwantaserver
from iwantaserver import db, Event, Server


def get_creds(config=os.path.join(iwantaserver.__path__[0],
                                  "config/libcloud.conf")):
    parser = ConfigParser()
    parser.read(config)

    username = parser.get("rackspace", "username")
    apikey = parser.get("rackspace", "apikey")
    region = parser.get("rackspace", "region")

    return username, apikey, region


def create_servers(size_id, image_id, num, event_id):
    username, apikey, region = get_creds()

    Driver = get_driver(Provider.RACKSPACE)
    driver = Driver(username, apikey, region=region)

    size = list(filter(lambda size: size.id == size_id, driver.list_sizes()))[0]
    image = list(filter(lambda img: img.id == image_id, driver.list_images()))[0]

    for i in range(num):
        node = driver.create_node(
            name=datetime.strftime(datetime.now(), "gmas-%Y%m%d%H%M%S"),
            image=image, size=size)
        password = node.extra["password"]

        _, ip = driver.wait_until_running([node])[0]
        server = Server(ip[0], password, event_id)
        server.available = True
        db.session.add(server)
        db.session.commit()

        event = Event.query.filter(Event.id.is_(event_id)).scalar()
        if not event:
            continue
        event.image_name = image.name
        event.size_name = size.name
        db.session.add(event)
        db.session.commit()
    return i


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--size")
    parser.add_argument("--image")
    parser.add_argument("--num", default=1, type=int)
    parser.add_argument("--event", type=int)

    args = parser.parse_args()

    if args.size is None or args.image is None:
        print("Missing server arguments")
        return -1
    if args.event is None:
        print("Must provide event ID")
        return -2

    rv = create_servers(args.size, args.image, args.num, args.event)
    return rv

if __name__ == "__main__":
    sys.exit(main())
