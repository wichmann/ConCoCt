# -*- coding: utf-8 -*-

import os

### required - do no delete
def user(): return dict(form=auth())
def download(): return response.download(request,db)
def call(): return service()
### end requires


def index():
    return dict()


def codeeditor():
    """Shows a editor to change uploaded code files.

    Parameters are
    """
    # get file content if an argument is given
    if request.args:
        code_file_name = request.args[0]
        code_file_path = os.path.join(request.folder, 'private', code_file_name)
        with open(code_file_path, 'r') as code_file:
            code = code_file.read()
    else:
        code = 'int main(){}'
    # prepare java script code for displaying the editor
    # using Ace editor (http://ace.c9.io/)
    editor_code = """
                  // setup Ace editor
                  var editor = ace.edit("editor");
                  editor.setTheme("ace/theme/monokai");
                  editor.getSession().setMode("ace/mode/c_cpp");
                  var Range = ace.require('ace/range').Range;
                  editor.getSession().addMarker(new Range(10, 0, 13, 30), "warning", "text");
                  // 'line' instead of 'text' highlights the whole line
                  editor.session.setOption("useWorker", false)
                  editor.getSession().setAnnotations([{
                    row: 1,
                    column: 10,
                    text: "Strange error",
                    type: "warning" // also error and information
                  }]);
                  // call function on click on submit button
                  $("#submit_button").bind('click', function () { alert('File saved!'); });
                  """
    editor = DIV(code, _id='editor')
    js1 = SCRIPT(_src=URL('static', 'js/src-noconflict/ace.js'), _type='text/javascript', _charset='utf-8')
    js2 = SCRIPT(editor_code, _type='text/javascript')
    submit_button = INPUT(_type='button', _value='Save changes...', _id='submit_button')
    # instead of the js above also possible: _onclick="ajax('ajaxwiki_onclick',['text'],'html')"
    return locals()


def view_result():
    import os
    # TODO Check if syntac highlighting should be done on server side or on the client
    # See: http://alexgorbatchev.com/SyntaxHighlighter/
    from pygments import highlight
    from pygments.lexers import PythonLexer
    from pygments.formatters import HtmlFormatter

    # get source and highlight it
    source_file = os.path.join(request.folder, 'private', 'main.c')
    # create highlighted source and wrap it into XML object to prevent
    # characters like < or > to be escaped into HTML entities
    code = XML(highlight(open(source_file, 'rb').read(), PythonLexer(),
                         HtmlFormatter(linenos='inline', lineanchors='lineanchor', linespans='line')))

    # highlight all errors in source and show mouse over info box
    errors = ( (2, 'Can not import file.'), (17, 'Function main not ok.'), (22, 'Do not know any more errors.') )
    commands = ''
    styles = ''
    # TODO: Write my own HTML formatter for pygments to include error and warning classes into HTML
    for error in errors:
        commands += "$('span#line-{lineno}').attr('title','{message}');".format(lineno=error[0], message=error[1])
        styles += '#line-{lineno} {{ background-color: yellow }}'.format(lineno=error[0])
    javascript = SCRIPT(commands, _type='text/javascript')
    error_styles = STYLE(XML(styles))

    return dict(code=code, javascript=javascript, error_styles=error_styles)


def error():
    return dict()
