ConCoCt
=======

Description
-----------
ConCoCt is a web application to automatically compile and test simple programs
written in the C programming language.


Deployment
----------
1) Create an web2py directory to be used by your web server.

2) Clone ConCoCt repository from Github [1] to web2py/applications/.

3) Change database and mail configuration in ConCoCt/private/appconfig.ini.

4) Clone libConCoCt repository from Github [2] and add symbolic links for files
   (celery_tasks.py and libConCoCt.py) to ConCoct/modules.

5) Go to http://[server address]/admin and reload routes.

6) Go to http://[server address]/ConCoct and log in as null@null.com with the
   admin password "1234".

7) Change the name, password and email address of the administrator account.

8) Create new accounts for teachers and students under /ConCoCt/appadmin.

9) Import example tasks from directory ConCoCt/private/examples.

10) Remove logging.py from model in production???

[1] https://github.com/wichmann/ConCoCt.git
[2] https://github.com/wichmann/libConCoCt.git


License
-------
ConCoCt is released under the MIT License.


Translations
------------
Translations were provided by:
* German translation by Christian Wichmann


Requirements
------------
ConCoct runs with web2py 2.11.2 under Python 2.7.9.


Problems
--------
Please go to http://github.com/wichmann/ConCoct to submit bug reports, request
new features, etc.


Third party software
--------------------
ConCoct includes parts of or links with the following software packages and
programs, so give the developers lots of thanks sometime!

* web2py - Best Python Web Framework (http://www.web2py.com/)
* SQLite (http://sqlite.org/) is a software library that implements a self-
  contained, serverless, zero-configuration, transactional SQL database engine.
  SQLite is in the public domain. No claim of ownership is made to any part of
  the code.
* Ace - The High Performance Code Editor for the Web. http://ace.c9.io/.
  Released under the BSD license.
* Some cliparts from opencliparts.org:
   - https://openclipart.org/detail/212046/emblem-gear
