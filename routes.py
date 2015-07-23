# -*- coding: utf-8 -*-

#
#  Router for ConCoct application
#

routers = dict(
    BASE = dict(
        default_application = 'ConCoct',
        default_controller = 'default',
        default_function = 'index',
        )
)

default_application = 'ConCoct'
default_controller = 'default'
default_function = 'index'

# set path to favicon files
routes_in=(
  ('.*:/favicon.ico','/ConCoct/static/images/favicon.ico'),
)
