mcka-apros
==========

Mckinsey Academy custom front end instance

Notes:

* Best to install requirements
`$ pip install -r requirements.txt`

    _(if you experience an error when installing mySql package on Mavericks try this command instead
`$ CFLAGS=-Wunused-command-line-argument-hard-error-in-future pip install -r requirements.txt`
    )_

* CSS and JS are compiled automatically upon save (for dev) when you run
`$ ./manage.py rundev`

* We are using standard Django templates, but we are preprocessing them with haml preprocessor (installed via pip)
haml is a lovely markup, quick reference:

  * to execute python code within template prefix with a - sign
    e.g.
`- x = "I love haml"`
    will add a variable named x set to the value of "I love haml"

  * to render the result of python code into the document use an = sign
    e.g.
`= x`
    will print the contents of the variable named x to the template

  * Follow the syntax %type.classname.anotherclassname#id for html elements
    e.g.
`%span.signature.here#sign-here`
    will create a span element with class="signature here" and id="sign-here"

  * Default element type is div - you don't even need to specify
    e.g.
`.button-area`
    will create a div with class="button-area"

  * Nest with indentation
    e.g.
`.square-box
  %span The important thing is that you
  %span.important love life`
    will generate HTML like:

`<div class="square-box">
  <span>The important thing is that you</span>
  <span class="important">love life</span>
</div>`

  * Font Specification
  McKinsey font defintions all specify size, normal|semibold|bold, line-spacing - just like photoshop does
  To facilitate the CSS for these situations use the mixin "font-spec"
`@include font-spec(size, weight, line-spacing)`

    size defaults to 10
    weight defaults to normal (yet supports semibold as a specifier)
    line-spacing defaults to same as size

* Override settings
    Override settings in local_settings.py file

