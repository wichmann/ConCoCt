# -*- coding: utf-8 -*-

import logging, logging.handlers

def get_configured_logger(name):
    """
    Check if application logger has been initialized yet and creates a new
    logger if necessary.

    Source: http://www.web2pyslices.com/slice/show/1416/logging
    """
    logger = logging.getLogger(name)
    if (len(logger.handlers) == 0):
        # check whether logger has no handlers because it hasn't been configured yet
        import os
        formatter="%(asctime)s %(levelname)s %(process)s %(thread)s %(funcName)s():%(lineno)d %(message)s"
        handler = logging.handlers.RotatingFileHandler(os.path.join(request.folder,'private/app.log'),
                                                       maxBytes=1024, backupCount=2)
        handler.setFormatter(logging.Formatter(formatter))
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        logger.debug(name + ' logger created')
    else:
        logger.debug(name + ' already exists')
    return logger

# assign application logger to global var
logger = get_configured_logger(request.application)
