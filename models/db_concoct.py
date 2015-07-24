# -*- coding: utf-8 -*-

# get current date to be used when an upload is stored
import datetime
now=datetime.datetime.now()


# create table to store tasks
db.define_table(
    'Tasks',
    Field('Name', 'string', writable=False, readable=False),
    Field('Teacher', db.auth_user, required=True, label=T('Teacher')),
    Field('OpenForSubmission','boolean', label=T('OpenForSubmission')),
    Field('SubmittedTask', 'upload', label=T('Task to be uploaded')),
    Field('DataPath', 'string', writable=False, readable=False),
    auth.signature,
)

db.Tasks.Teacher.default = auth.user_id
db.Tasks.Teacher.requires = IS_NOT_EMPTY()
#db.Tasks.Name.requires = IS_NOT_EMPTY()
#db.Tasks.DataPath.requires = IS_NOT_EMPTY()


# create table to store all entries for tasks
db.define_table(
    'Entries',
    Field('Submitter', db.auth_user, writable=False, readable=False, label=T('Submitter')),
    Field('Task', db.Tasks, writable=False, readable=False, label=T('Task')),
    Field('IPAddress', 'string', writable=False, readable=False, label=T('IP Address')),
    Field('SubmittedFile', 'upload', label=T('File to be uploaded')),
    Field('OnDiskPath', 'string', writable=False, readable=False),
    Field('CeleryUUID', 'string', writable=False, readable=False),
    Field('SubmissionTime', 'datetime', writable=False, readable=False, default=now),
    auth.signature,
)

db.Entries.Submitter.default = auth.user_id
db.Entries.SubmittedFile.requires = [IS_LENGTH(concoct_conf.take('handling.max_file_length', cast=int), 0,
                                               error_message=T('File size is to large!')),
                                     IS_NOT_EMPTY(error_message=T('Choose a file to be uploaded!')),
                                     IS_UPLOAD_FILENAME(extension='c')]


# create table to store information about builds
db.define_table(
    'Builds',
    Field('Task', db.Tasks, writable=False, readable=False, label=T('Task')),
    Field('Entry', db.Entries, writable=False, readable=False, label=T('Entry')),
    Field('CeleryUUID', 'string', writable=False, readable=False),
    Field('Finished', 'boolean', writable=False, readable=True, default=False),
    Field('Report', 'string', writable=False, readable=True),
    auth.signature,
)
