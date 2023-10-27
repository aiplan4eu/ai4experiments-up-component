import os
import json
import logging

from server import UnifiedPlanningServer


def main():
    configfile = "config.json"
    config = json.load(open(configfile, 'rt'))
    grpcport = config['grpcport']

    server = UnifiedPlanningServer(grpcport)

    server.logger.info("starting unified planning server on port %s" % grpcport)
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    main()
