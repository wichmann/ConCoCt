# -*- coding: utf-8 -*-

import os
from zipfile import ZipFile

def view():
    """
    Shows all tasks if no argument is given or details of a specific task.

    /task/list -> lists all tasks (includes a button to download task template as ZIP file)
    /task/view/[task id] -> view detailed information about a specific task
    /task/add -> add a new task by uploading a ZIP file with all information
    """
    if request.args:
        from gluon.contrib.markdown import markdown2
        length = len(request.args[0])
        # TODO Make argument tasks id instead of its name.
        # TODO Check whether the given task number is valid!
        # take task name from raw arguments because there could be umlauts
        task_to_be_shown = request.raw_args[0:length]
        task_description_path = os.path.join(request.folder, 'private', 'tasks', task_to_be_shown, 'description.md')
        with open(task_description_path, 'r') as task_description:
            description = XML(markdown2.markdown(task_description.read()))
        back_button = A(T('Back'), _href=URL(f='list'), _class='btn btn-primary', _id='back_button')
        #<div id="back_button" class="btn btn-primary"><a href="{{=URL(f='tasks')}}">{{=T('Back')}}</a></div>
        submit_entry_button = A(T('Submit entry'), _href=URL(c='entry',f='add', args=(task_to_be_shown)), _class='btn btn-primary', _id='submit_entry_button')
        return dict(description=description, back_button=back_button,
                    submit_entry_button=submit_entry_button)
    else:
        raise HTTP(404, T('No task number given.'))


def list():
    tasks_path = os.path.join(request.folder, 'private', 'tasks')
    # get all subdirectories of tasks directory
    #tasks_directories = [x[1] for x in os.walk(tasks_path)]
    #tasks_directories = filter(os.path.isdir, [os.path.join(tasks_path,f) for f in os.listdir(tasks_path)])
    tasks_directories = [d for d in os.listdir(tasks_path) if os.path.isdir(os.path.join(tasks_path, d))]
    task_links_list = []
    for task in tasks_directories:
        task_links_list.append(LI(A(task, _href=URL(c='task', f='view', args=(task,)))))
    task_table = UL(task_links_list, _id='task_table')
    return dict(task_table=task_table)


def add():
    """
    Adds a new task to the system. The task consists of a single ZIP file
    containing a single directory with the tasks data.

    Task data:
     - description.md -> task description and information about functions that should be implemented
     - config.json    -> task configuration, e.g. information what libraries to link against
     - src/main.c     -> main program to run the functions that should be implemented
     - src/tests.c    -> unit tests to check if task was sucessfully completed
     - src/solution.c -> code file that should be implemented
     - src/solution.h -> header with prototypes of the functions that should be implemented
    """
    form = SQLFORM(db.Tasks)
    # validate and process the form
    if form.process().accepted:
        name, data_path = store_task_archive(response)
        if data_path:
            response.flash = T('Task submitted!')
            # store task directory path in database
            #if form.vars.id:
            new_task_entry = db(db.Tasks.id == form.vars.id).select().first()
            new_task_entry.update_record(DataPath=data_path)
            new_task_entry.update_record(Name=name)
        else:
            response.flash = T('Task could not be submitted!')
    return locals()


def store_task_archive(response):
    """
    Stores a task inside a given ZIP file on disk.

    If the task archive contains more than one directory or if some of the
    necessary files are missing, no files will be written to disk.

    Returns an tuple with empty strings if task archive was not valid or
    another error occured. Otherwise the name and path of the new task is
    returned.
    """
    task_name = ''
    new_task_directory_path = ''
    with ZipFile(request.vars.SubmittedTask.file) as task_archive:
        # find common prefix of all paths in ZIP file
        task_name = os.path.commonprefix([x.filename for x in task_archive.infolist()]).replace('/', '')
        # a task archive can only contain a single task directory!!!
        if not task_name:
            return ('', '')
        # check if task directory already exists (task name must be unique!!!!)
        tasks_store_path = os.path.join(request.folder, 'private/tasks/')
        new_task_directory_path = os.path.join(tasks_store_path, task_name)
        if os.path.exists(new_task_store_path):
            return ('', '')
        os.mkdir(new_task_store_path)
        task_archive.extract(task_name + '/description.md', path=tasks_store_path)
        #task_archive.extract(task_name + '/config.json', path=tasks_store_path)
        for filename in task_archive.namelist():
            #source_store_path = os.path.join(tasks_store_path, 'src')
            if filename.startswith(task_name + '/src/'):
                task_archive.extract(filename, path=tasks_store_path)
        # create directory to store submissions
        os.mkdir(os.path.join(new_task_directory_path, 'submissions'))
    return task_name, new_task_directory_path
