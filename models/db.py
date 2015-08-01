# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()


## get application configuration
from gluon.contrib.appconfig import AppConfig
## once in production, remove reload=True to gain full speed
concoct_conf = AppConfig(reload=True)

db = DAL(concoct_conf.take('db.uri'), pool_size=concoct_conf.take('db.pool_size', cast=int), check_reserved=['all'])

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
#response.generic_patterns=['*.json']
response.generic_patterns = ['*'] if request.is_local else []
## choose a style for forms
response.formstyle = concoct_conf.take('forms.formstyle')  # or 'bootstrap3_stacked' or 'bootstrap2' or other
response.form_label_separator = concoct_conf.take('forms.separator')

## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'

from gluon.tools import Auth, Service, PluginManager

auth = Auth(db)
service = Service()
plugins = PluginManager()

## create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False)

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else concoct_conf.take('smtp.server')
mail.settings.sender = concoct_conf.take('smtp.sender')
mail.settings.login = concoct_conf.take('smtp.login')

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)

#from gluon.contrib.populate import populate
#if db(db.auth_user).isempty():
#     populate(db.auth_user,10)

def initialize_admin():
    if not db(db.auth_user).select().first():
        # create administrator group if not already there
        new_admin_group = auth.add_group('administrator')
        # create new administrator and add him to admin group
        new_user_id = db.auth_user.insert(
            password = db.auth_user.password.validate('1234')[0],
            email = 'null@null.com',
            first_name = 'System',
            last_name = 'Administrator',
        )
        auth.add_membership(new_admin_group, new_user_id)
        # create teacher group
        new_teacher_group = auth.add_group('teacher')
        auth.add_membership(new_teacher_group, new_user_id)

# initialize administrator account
initialize_admin()
