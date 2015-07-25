# -*- coding: utf-8 -*-

import os
from zipfile import ZipFile
from gluon.contrib.markdown import markdown2


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
        submit_entry_button = A(T('Submit entry'), _href=URL(c='entry',f='add', args=(task_to_be_shown)), _class='btn btn-primary', _id='submit_entry_button')
        return dict(description=description, back_button=back_button,
                    submit_entry_button=submit_entry_button,
                    task_name=row.select().first()['Name'])
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
        current_title_text = H3('Task: {}'.format(task.Name), _class='panel-title pull-left')
        view_current_task_button = A(T('View task'), _href=URL(c='task', f='view', args=(task.id,)),
                                     _class='btn btn-primary', _id='view_button-{}'.format(task.id))
        button_group = DIV(view_current_task_button, _class='btn-group pull-right')
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
