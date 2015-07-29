# -*- coding: utf-8 -*-

import os
import shutil
from gluon.tools import prettydate
# TODO Fix import problematic because base dir of web2py is different from
#      working directory of Celery worker!
import celery_tasks


@auth.requires_login()
def list():
    """
    Allows to upload, view and edit entries for given task.

    /entry/list -> list all entries for current user or all entries for given task???
    /entry/upload/[task id] -> upload a single! source code file (solution.c) as entry for a given task
                               forwarding to /entry/build/[task id] to wait for background process to run entry
    /entry/add/[task id] -> add a new entry from scratch (solution.c from task directory) and open code editor
                            by clicking 'build' button', building of entry and highlighting of errors in source
                            Results of tests will be shown in editor or separate DIV???
    /entry/build/[task id]/[entry id] -> build entry and wait, show build information when build is ready
                                         if entry id is empty, newest entry of current user for given task is build!!!
    /entry/build_status/[build id] -> returns build information (status, report) as JSON data
                                      error when no build id is given
    /entry/view/[task id] -> view result of compilation and run of entry
                             button to forward to code editor opened with current entry for given task
    """
    tasks_in_entries = db(db.Entries.Submitter == auth.user_id).select(orderby=db.Entries.Task, groupby=db.Entries.Task)
    task_div_list = []
    js_toggle_panels = ''
    for task in tasks_in_entries:
        # get current task from database based on id from Entries table
        current_task = db(db.Tasks.id == task.Task).select().first()
        # get all entries for current task sorted by submission time
        entries = db((db.Entries.Submitter == auth.user_id) & (db.Entries.Task == current_task.id)).select(orderby=~db.Entries.SubmissionTime)
        entry_rows = []
        entry_rows.append(TR(TD('Entry'), TD('Uploaded'), TD('Edit'), TD('Build'), _class='table_header'))
        for entry in entries:
            # build table row of current entry for current task
            entry_text = 'Entry no. {}'.format(entry.id)
            edit_entry_link = A('Edit entry', _href=URL(c='default', f='codeeditor', args=(entry.Task, entry.id)))
            build_entry_link = A('Build entry', _href=URL(f='build', args=(entry.Task, entry.id)))
            entry_rows.append(TR(TD(entry_text), TD(prettydate(entry.SubmissionTime,T)), TD(edit_entry_link),
                                 TD(build_entry_link), _id='entry_data-{}'.format(entry.id)))
        # build panel and its header
        task_panel_heading_id = 'task_heading-{}'.format(current_task.id)
        task_panel_body_id = 'task_body-{}'.format(current_task.id)
        entry_table = TABLE(*entry_rows, _class='table table-hover')
        current_task_table = DIV(entry_table, _class='panel-body', _id=task_panel_body_id)
        new_task_panel_header = H3('Task number {task_id}: {task_name}'.format(task_id=current_task.id, task_name=current_task.Name),
                                   _class='panel-title')
        current_task_header = DIV(new_task_panel_header, _class='panel-heading', _id=task_panel_heading_id)
        task_div_list.append(DIV(current_task_header, current_task_table, _class='panel panel-default'))
        # create JavaScript to toggle panels by clicking on their header
        js_toggle_panels += '$("#{contentID}").hide();'.format(contentID=task_panel_body_id)
        js_toggle_panels += '$("#{titleID}").click(function(){{ $("#{contentID}").slideToggle(); }});'.format(titleID=task_panel_heading_id, contentID=task_panel_body_id)
    complete_entry_list = DIV(task_div_list)
    js_toggle_panels = SCRIPT(js_toggle_panels)
    return locals()


@auth.requires_login()
def upload():
    if request.args:
        form = SQLFORM(db.Entries)
        # validate and process the form
        if form.process().accepted:
            response.flash = T('Entry submitted!')
    return locals()


@auth.requires_login()
def add():
    """
    Displays a form to upload a new entry for a given task.

    Exactly one argument is needed as task id. If no arguments are given this
    function returns a 404 error.

    TODO: Implement custom store and retrieve functions instead of copying the file.
    (See: http://stackoverflow.com/questions/8008213/web2py-upload-with-original-filename)
    """
    if request.args:
        # check if argument is valid task number
        try:
            task_to_upload_entry_to = int(request.args[0])
        except ValueError:
            raise HTTP(404, T('Invalid task number given.'))
        row = db(db.Tasks.id == task_to_upload_entry_to)
        if not row:
            raise HTTP(404, T('No task number given.'))
        # build upload form
        fields = (db.Entries.SubmittedFile, )
        query = (db.Entries.id > 0)
        form = SQLFORM(db.Entries)
        # validate and process the form
        if form.process().accepted:
            response.flash = T('Entry successfully uploaded!')
            # copy uploaded file to solutions directory to be build later
            solutions_path = os.path.join(request.folder, 'private', 'solutions',
                                          str(task_to_upload_entry_to), str(auth.user_id))
            if not os.path.exists(solutions_path):
                os.makedirs(solutions_path)
            # get number of already uploaded entries to name file of new submission
            number_of_already_made_entries = db((db.Entries.Submitter == auth.user_id) &
                                                (db.Entries.Task == task_to_upload_entry_to)).count()
            new_solution_file = os.path.join(solutions_path, 'solution.{}.c'.format(number_of_already_made_entries + 1))
            uploaded_file_on_disk = os.path.join(request.folder, 'uploads', form.vars.SubmittedFile)
            shutil.copyfile(uploaded_file_on_disk, new_solution_file)
            # update database entry
            new_entry = db(db.Entries.id == form.vars.id).select().first()
            new_entry.update_record(IPAddress=request.client)
            new_entry.update_record(Task=task_to_upload_entry_to)
            new_entry.update_record(OnDiskPath=new_solution_file)
            new_entry.update_record(Submitter=auth.user_id)
            # redirect to build page
            redirect(URL(f='build',args=(task_to_upload_entry_to, form.vars.id)))
        return locals()
    else:
        raise HTTP(404, T('No task number given.'))


@auth.requires_login()
def build():
    """
    Returns results of build and test execution as JSON or HTML.
    """
    if request.args:
        if len(request.args) != 2:
            raise HTTP(404, T('Invalid number of arguments.'))
        # TODO Validate arguments against database.
        task_to_be_build = request.args[0]
        entry_to_be_build = request.args[1]
        entries_solution_file = db(db.Entries.id == entry_to_be_build).select().first()['OnDiskPath']
        tasks_store_path = db(db.Tasks.id == task_to_be_build).select().first()['DataPath']
        # start building entry for task
        building = celery_tasks.build_and_check_task_with_solution.delay(tasks_store_path, entries_solution_file)
        # store build job in database including Celery UUID
        build_id = db.Builds.insert(Task=task_to_be_build, Entry=entry_to_be_build,
                                    CeleryUUID=building.id, Finished=False)
        # setup components to display status and results of build
        status_box = DIV(_id='build_status')
        result_box = DIV(_id='build_results')
        script = SCRIPT("""
                        var intervalID = setInterval(function(){{ reload() }}, 250);

                        function reload()
                        {{
                            $.get("{reload_url}", function(data) {{
                                $("#build_status").text(data.status);
                                $("#build_results").text(data.test_results);
                                if (data.test_results != ""){{
                                    // clear timer and show button when result is in
                                    $("#forward_button").show();
                                    clearInterval(intervalID);
                                }};
                            }});
                        }};

                        $("#forward_button").hide();
                        """.format(reload_url=URL(r=request, c='entry', f='build_status.json', args=(build_id,))))
        forward_button = A(T('Results'), _href=URL(c='default', f='codeeditor', args=(task_to_be_build, entry_to_be_build)),
                           _class='btn btn-primary', _id='forward_button')
        return locals()
    else:
        raise HTTP(404, T('No task number given.'))


@auth.requires_login()
def build_status():
    """
    Returns information about an ongoing or finished build. The information
    contains a build status and an error report.

    Furthermore this function checks whether the build with the given id is
    finished. In that case it stores the test results inside the database and
    marks the build as complete.

    When this function is called to explicitly return data in JSON format
    (/ConCoct/entry/build_status.json) it is used for displaying that build
    information on the build page (/ConCoct/entry/build).

    If simply a dictionary is returned, web2py will use the associated view to
    display the data when not asked for JSON data. Local variables can be
    explicitly rendered into JSON with: return response.json(custdata)
    """
    if request.args:
        requested_build_id = request.args[0]
        try:
            build_id = db(db.Builds.id == requested_build_id).select().first()['CeleryUUID']
        except TypeError:
            raise HTTP(404, T('Invalid build number given.'))
        result = celery_tasks.build_and_check_task_with_solution.AsyncResult(build_id)
        status = T('Build status: {status}').format(status=result.status)
        test_results = ''
        if result.ready():
            try:
                test_results = result.get()
                # store results in database if build has not already been finished
                chosen_build = db(db.Builds.id == requested_build_id).select().first()
                already_finished = chosen_build['Finished']
                if not already_finished:
                    chosen_build.update_record(Finished=True)
                    chosen_build.update_record(Report=test_results)
                    #db.commit()
            except AttributeError:
                test_results = ''
        return dict(status=status, test_results=test_results)
    else:
        raise HTTP(404, T('No build number given.'))


@auth.requires_login()
def view():
    if request.args:
        #fields = (db.task.Name, db.task.DueDate, db.task.Token)
        query = ((db.Entries.Submitter == auth.user))
        #headers = {'task.Name':   T('Name'),
        #           'task.DueDate': T('DueDate'),
        #           'task.Token': T('Token')}
        #default_sort_order=[db.task.DueDate]
        #links = [dict(header=T('View uploads'), body=lambda row: A(T('View uploaded files'), _href=URL('manage', 'collect', args=[row.id], user_signature=True)))]
        grid = SQLFORM.grid(query=query, orderby=default_sort_order, create=True,
                            links=links, deletable=True, editable=True, csv=False, maxtextlength=64, paginate=25,
                            onvalidation=validate_task_data) #if auth.user else login
    else:
        raise HTTP(404, T('No task number given.'))