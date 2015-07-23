from gluon.storage import Storage
settings = Storage()

settings.migrate = True
settings.title = 'ConCoct'
settings.subtitle = ''
settings.author = 'Christian Wichmann'
settings.author_email = 'christian@freenono.org'
settings.keywords = ''
settings.description = ''
settings.layout_theme = 'Default'
settings.database_uri = 'sqlite://storage.sqlite'
settings.security_key = '59df4826-8a75-45fb-a66a-5871036188f5'
settings.login_method = 'local'
settings.login_config = ''
settings.plugins = []
