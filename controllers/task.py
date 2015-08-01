# -*- coding: utf-8 -*-

import os
import json
from zipfile import ZipFile

from gluon.contrib.markdown import markdown2

import libConCoCt


@auth.requires_login()
def view():
    """
    Shows all tasks if no argument is given or details of a specific task.

    TODO: Use bootstrap panel for displaying task description and other
          information.

    /task/list -> lists all tasks (includes a button to download task template as ZIP file)
    /task/view/[task id] -> view detailed information about a specific task
    /task/add -> add a new task by uploading a ZIP file with all information
    """
    if request.args:
        # check if argument is valid integer number
        try:
            task_to_be_shown = int(request.args[0])
        except ValueError:
            raise HTTP(404, T('Invalid argument given.'))
        # check whether argument is a valid task id
        row = db(db.Tasks.id == task_to_be_shown)
        if not row:
            raise HTTP(404, T('Invalid task id given.'))
        task_data_path = row.select().first()['DataPath']
        task_description_path = os.path.join(task_data_path, 'description.md')
        with open(task_description_path, 'r') as task_description:
            description = XML(markdown2.markdown(task_description.read()))
        back_button = A(T('Back'), _href=URL(f='list'), _class='btn btn-primary', _id='back_button')
        submit_entry_button = A(T('Submit entry'), _href=URL(c='entry',f='add', args=(task_to_be_shown)),
                                _class='btn btn-primary', _id='submit_entry_button')
        open_empty_file_button = A(T('Open empty file'), _href=URL(c='default', f='codeeditor', args=(task_to_be_shown,)),
                                   _class='btn btn-primary', _id='open_new_button')
        open_empty_project_button = A(T('Open empty CodeBlocks project'), _href=URL(c='task', f='download_project', args=(task_to_be_shown,)),
                                   _class='btn btn-primary', _id='open_project_button-{}'.format(task_to_be_shown))
        statistics = []
        statistics.append(DIV(A(T('Submitted entries: '), SPAN('{}'.format(count_entries(task_to_be_shown)), _class='badge'),
                                _id='submitted_entries_badge', _href=URL(c='entry',f='list', args=(task_to_be_shown))), _class='btn btn-primary'))
        statistics.append(DIV(T('Executed builds: '), SPAN('{}'.format(count_executed_builds(task_to_be_shown)), _class='badge'),  _class='btn btn-primary'))
        statistics.append(DIV(T('Successful builds: '), SPAN('{}'.format(count_successful_builds(task_to_be_shown)), _class='badge'),  _class='btn btn-primary'))
        statistics = DIV(*statistics)
        return dict(description=description, back_button=back_button, statistics=statistics,
                    submit_entry_button=submit_entry_button, open_empty_file_button=open_empty_file_button,
                    open_empty_project_button=open_empty_project_button, task_name=row.select().first()['Name'])
    else:
        raise HTTP(404, T('No task number given.'))


@auth.requires_login()
def list():
    task_links_list = []
    script_parts_list = ''
    for task in db(db.Tasks.id > 0).select():
        # build panel header for each task including the button group displayed
        # on the right side
        current_description_id = 'description-{}'.format(task.id)
        current_title_id = 'tasktitle-{}'.format(task.id)
        current_title_text = H3(T('Task: {}').format(task.Name), _class='panel-title pull-left')
        view_current_task_button = A(T('View task'), _href=URL(c='task', f='view', args=(task.id,)),
                                     _class='btn btn-primary', _id='view_button-{}'.format(task.id))
        upload_entry_for_task_button = A(T('Submit entry'), _href=URL(c='entry', f='add', args=(task.id,)),
                                         _class='btn btn-primary', _id='submit_button-{}'.format(task.id))
        open_empty_file_button = A(T('Open empty file'), _href=URL(c='default', f='codeeditor', args=(task.id,)),
                                   _class='btn btn-primary', _id='open_button-{}'.format(task.id))
        open_empty_project_button = A(T('Open empty CodeBlocks project'), _href=URL(c='task', f='download_project', args=(task.id,)),
                                   _class='btn btn-primary', _id='open_project_button-{}'.format(task.id))
        button_group = DIV(view_current_task_button, open_empty_project_button, open_empty_file_button, upload_entry_for_task_button, _class='btn-group pull-right')
        task_link = DIV(DIV(current_title_text), DIV(button_group), _id=current_title_id, _class='panel-heading clearfix')
        task_description_path = os.path.join(task.DataPath, 'description.md')
        # build panel body containing task description
        with open(task_description_path, 'r') as task_description:
            task_description = DIV(XML(markdown2.markdown(task_description.read())), _id=current_description_id, _class='panel-body')
        task_links_list.append(DIV(task_link, task_description, _class='panel panel-default'))
        # deactivate task descriptions by default and toggle them by clicking
        script_parts_list += '$("#{descID}").hide();'.format(descID=current_description_id)
        script_parts_list += '$("#{titleID}").click(function(){{ $("#{descID}").slideToggle(); }});'.format(titleID=current_title_id, descID=current_description_id)
    task_table = DIV(task_links_list, _id='task_table')
    script = SCRIPT("""
                function onclickTask(id) {{
                    alert(id);
                    //$("#upload_Task").empty();
                    //ajax('', ['Teacher'], ':eval');
                }};
                {moreScript}
                """.format(moreScript=script_parts_list))
    return dict(task_table=task_table, script=script)



def count_entries(task_id):
    entries = db(db.Entries.Task == task_id).count()
    return entries


def count_executed_builds(task_id):
    builds = db(db.Builds.Task == task_id).count()
    return builds


def count_successful_builds(task_id):
    builds = db(db.Builds.Task == task_id).select(db.Builds.Report, distinct=True)
    count_successful = 0
    for build in builds:
        build_successful = True
        if build['Report']:
            report = json.loads(build['Report'])
            if 'cunit' in report and 'tests' in report['cunit']:
                for suite in report['cunit']['tests']:
                    suite = report['cunit']['tests'][suite]
                    for test in suite:
                        if not suite[test]:
                            build_successful = False
            else:
                build_successful = False
        if build_successful:
            count_successful += 1
    return count_successful


def validate_task_id(task_id):
    """
    Validates a given task number. The given id can be directly taken from the
    arguments of the request (e.g. request.args[0]). This function checks
    whether the task id is really a integer and if it is inside the database.
    Furthermore it checks if the current user is authorized to handle this task.

    In case of errors, the response is an 404 error with a error message.

    :param task_id: task id to be validated
    :returns: task from database as Row object
    """
    # check if argument is valid integer number
    try:
        task_as_int = int(request.args[0])
    except ValueError:
        raise HTTP(404, T('Invalid argument given.'))
    # validate task number against database
    task_from_db = db(db.Tasks.id == task_as_int).select().first()
    if not task_from_db:
        raise HTTP(404, T('Invalid task id given.'))
    # TODO Check authorization of user for this task.
    return task_from_db


@auth.requires_login()
def download_project():
    if request.args:
        task_from_db = validate_task_id(request.args[0])
        data_path = task_from_db['DataPath']
        # TODO Refactor the project creation to separate module.
        t = libConCoCt.Task(data_path)
        with open(os.path.join(data_path, 'config.json'), 'r') as config_file:
            task_config = json.load(config_file)
        solution_file = os.path.join(data_path, 'src', task_config['files_student'][0])
        s = libConCoCt.Solution(t, (solution_file, ))
        p = t.get_main_project(s)
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        zip_file_name = '{}_{}.zip'.format(task_from_db['Name'], current_date)
        project_zip_file = p.create_cb_project(file_name=os.path.join(request.folder, 'private', zip_file_name))
        return response.stream(project_zip_file, chunk_size=2**14, attachment=True, filename=zip_file_name)
    else:
        raise HTTP(404, T('No task number given.'))


@auth.requires_membership('teacher')
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
        if os.path.exists(new_task_directory_path):
            # when task is already on the server, do not unzip again
            # TODO: Handle replacing of a task with a newer version with the same name.
            return ('', '')
        os.mkdir(new_task_directory_path)
        task_archive.extract(task_name + '/description.md', path=tasks_store_path)
        task_archive.extract(task_name + '/config.json', path=tasks_store_path)
        for filename in task_archive.namelist():
            #source_store_path = os.path.join(tasks_store_path, 'src')
            if filename.startswith(task_name + '/src/'):
                task_archive.extract(filename, path=tasks_store_path)
        # create directory to store submissions
        os.mkdir(os.path.join(new_task_directory_path, 'submissions'))
    return task_name, new_task_directory_path
