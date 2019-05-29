

mcka-apros   [![codecov](https://codecov.io/gh/mckinseyacademy/mcka_apros/branch/development/graph/badge.svg?token=bN22sHuE49)](https://codecov.io/gh/mckinseyacademy/mcka_apros)
==========

Mckinsey Academy custom front end application

### Notes:

* Best to install requirements
`$ pip install -r requirements.txt`

    _(if you experience an error when installing mySql package on Mavericks try this command instead
`$ CFLAGS=-Wunused-command-line-argument-hard-error-in-future pip install -r requirements.txt`
    )_

* CSS and JS are compiled automatically upon save (for dev) when you run
`$ ./manage.py rundev`

* Detailed setup notes can be found [there][setup-notes]

* Notes for upgrading to Django 1.8 can be found [there][upgrade-notes]

* Notes for configuring Group Work v2 can be found [there][group-work-config]

* Instruction for working with Waffle flags and a list of waffle flags can be
found [here](docs/Waffle_Setup.md)

[setup-notes]: /docs/SetupNotes.md
[upgrade-notes]: /docs/UpgradeNotes.md
[group-work-config]: /docs/GroupWorkConfiguration.md

#### Templates
We are using standard Django templates, but we are preprocessing them with haml preprocessor (installed via pip)
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

#### Font Specification
  McKinsey font defintions all specify size, normal|semibold|bold, line-spacing - just like photoshop does
  To facilitate the CSS for these situations use the mixin "font-spec"
`@include font-spec(size, weight, line-spacing)`

    size defaults to 10
    weight defaults to normal (yet supports semibold as a specifier)
    line-spacing defaults to same as size

#### Override settings
Override settings in a local_settings.py file

#### Migrations
Some of the django apps herein are using Django's built-in support for schema migrations to assist with data model changes.

__Creating an Initial Migration__
To have your django app included in the migration run the following command

    ./manage.py makemigrations <name_of_app>

This will create and initial migration file that creates the database table and enables the app for future migration support

__Incorporating changes into a New Migration__
To take the current state and create a migration with the differences run the following command:

    ./manage.py makemigrations <name_of_app>

This will create a subsequent migration file that will apply the differences to the database model

__Marking a Migration as applied__
To fix up migration records so that the newly added migration record does not clash with a previously created database object (e.g. The table was already created using `./manage.py syncdb` but the app is now desired to use migrations) use the following command:

    ./manage.py migrate --fake-initial <name_of_app>

#### Deletion Admins
Given the dangerous nature of data deletion, especially when deleting a company
or performing a bulk deletion, we can set up extra emails to be notified when
those are executed.

Extra emails to be notified of deletions can be added by using a management command:

    ./manage.py deletion_admin add admin_1@test.com admin_2@test.com admin_3@test.com

These can be later removed by using:

    ./manage.py deletion_admin remove admin_2@test.com admin_3@test.com

Whenever a bulk or company deletion notification is sent to the admin that
started the process, it will be also sent to the existing deletion admins.
