# -*- coding: utf-8 -*-

# Per default generic views are deactivated on all hosts except the local host
# therefore specific generics for JSON data have to be enabled.
# WARNING: This can be a security risk, better to include all necessary views
#          explicitly.
#response.generic_patterns=['*.json']
