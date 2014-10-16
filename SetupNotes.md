# Setting up McKinsey Academy (Apros) with local LMS

As the edX API starts to mature it becomes more desirable to develop the Apros product while hooked up to a real edX LMS system.

This document explains how to achieve this in a development environment. For instructions on setting Apros inside edx-platform devstack virtual box see [Installing Apros inside devstack virtual box][devstack-apros-setup]. 

The steps we'll follow are as follows:

1. Setup edX Environment
- Setup Apros Environment
- Prepare the McKinsey Academy project to talk to specific version of LMS
- Prepare LMS to respond to API / XBlock requests from Apros
- Configure your system to use a common domain between Apros and LMS

Throughout, this document refers to the names `lms.mcka.local` and `mcka.local`. It should be noted that these are simply names that we'll use when adding the systems to the same domain. You can use whatever names you like, but the important thing is that they have a common domain, to allow easy access to the LMS session cookie within Apros which enables data transfer through the XBlock.

[devstack-apros-setup]: devstack_apros_setup.md

## Step 1 - Setup edX devstack Environment

By far the simplest way to set up the edX system is to install the devstack environment which includes a virtualbox environment that runs a separate machine to host the edX platform and conveniently shares folders so that the edX-platform code resides on the host machine.

Follow the instructions at https://github.com/edx/configuration/wiki/edX-Developer-Stack

The devstack environment maps some local ports so that LMS and CMS (Studio) serve content on the host machines ports 8000 and 8001 respectively.

Please note that edx/edx-platform devstack does not support LMS API, so edx-solutions/edx-platform should be used instead.

### Setting up solutions devstack

Start with a shiny new upstream devstack. Then checkout solutions in your edx-platform repo.

Next, clear and rebuilt the Python dependencies

As vagrant user:
```
sudo virtualenv --clear /edx/app/edxapp/venvs/edxapp
sudo chown edxapp:edxapp -R /edx/app/edxapp/venvs/edxapp
sudo su edxapp  #make sure prompt reads ~/edx-platform
pip install -r requirements/edx/paver.txt
pip install python-memcached==1.48  # Until edx-solutions/edx-platform#152 is closed
paver install_prereqs
pip install -r requirements/edx/custom.txt
```
Finally give the same treatment to the db. The correct way to do this would involve 

    echo "DROP DATABASE edxapp;" | mysql -uedxapp001 -ppassword edxapp` `echo "CREATE DATABASE edxapp;" | mysql -uedxapp001 -ppassword` 
    
but then paver seems unable to rebuild on MySQL. The reason behind this is the fact that `django-openid-auth` uses 
`models.TextField(max_length=2047)` as a foreign key field and MySQL seems don't like it as

> Index prefixes on foreign key columns are not supported. One consequence of this is that BLOB and TEXT columns cannot 
be included in a foreign key because indexes on those columns must always include a prefix length.

To solve that, modify /edx/app/edxapp/venvs/edxapp/lib/python2.7/site-packages/django_openid_auth/models.py, so that 
`UserOpenID.claimed_id` becomes `CharField`:

    class UserOpenID(models.Model):
        user = models.ForeignKey(User)
        claimed_id = models.CharField(max_length=2047, unique=True)
        display_id = models.TextField(max_length=2047)
        
There's a little problem here: *it still wouldn't work*. Broken snippet is given here to draw your attention to the fact 
that steps to fix it could potentially lead to incorrect behavior of openid authentication. Django does not support 
`unique=True` on `CharFields` longer than 255 characters, so there are two options:

* Set `unique=False` losing identity integrity and potentially allowing multiple users have same claimed_id
* Set `max_length=255` losing precision and potentially truncating longer claimed_id

Yet another alternative would be to switch to SQLite `nano ~/lms.auth.json`:

```
    "DATABASES": {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": "edxapp.db"
        },
    }
```

After following any of these three paths, do `paver update_db --settings=devstack` to rebuild the database. 

Apros comes with a set of seed data, including preconfigured users. Unfortunately, it can't be loaded at this step, as 
it requires more configuration, so this is explained later in this document (see *Build Apros database and load seed data*)

You might also want to assign staff rights to at least one user, to do this (assuming that your user in named `staff`):

```
./manage.py dbshell <<< 'update auth_user set is_superuser=1, is_staff=1 where username="staff";'
```

### Run LMS

To run LMS, use the following command:

    paver devstack lms

This will compile any assets that are out of date and then run the django server. If you are confident there are no assets to compile (e.g. different runs with no source updates) one can start up the server more quickly using the command:

    paver devstack --fast lms

### (Optional) Run CMS (Studio)

Similarly, Studio is configured to startup with the command:

    paver devstack studio

or:

    paver devstack --fast studio



## Step 2 - Setup Apros Environment

### Setup McKinsey Academy project on your machine

    git clone git@github.com:mckinseyacademy/mcka_apros.git
or

    git clone https://github.com/mckinseyacademy/mcka_apros.git

### Install Python requirements
Requirements are configured using the command `$ pip install -r requirements.txt`

_(if you experience an error when installing mySql package on Mavericks try this command instead
`$ CFLAGS=-Wunused-command-line-argument-hard-error-in-future pip install -r requirements.txt`
    )_

### Install Other requirements
We require SASS to be used to build assets

    gem install sass --version 3.3.14

Notes:
* Sass 3.4+ is not compatible - see https://github.com/zurb/foundation-rails/pull/96
* _If `gem` is not installed, e.g. on a vanilla Windows machine, one may need to install ruby and gem framework to get started - this is left as an excercise to the reader_



## Step 3 - Prepare Apros to talk to specific instance of LMS

### Override specific settings in `local_settings.py` file

The McKinsey Academy application hosts it's `settings.py` file within the mcka_apros app folder. Alongside this file, create a new file named `local_settings.py`.

#### If you'd like to use Sqlite instead of mySQL, add the following lines:

    import os
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

_Sqlite is sometimes easier to operate with than mySql, but this is purely a choice for the developer. It may be wise to stick with mySql if you want to remain as close to the production environment as desired._

#### Configure the name to use for the LMS instance, like this:

    API_SERVER_ADDRESS = 'http://localhost:8000'
    LMS_BASE_DOMAIN = 'mcka.local'
    LMS_SUB_DOMAIN = 'lms'

`API_SERVER_ADDRESS` could be the dns name that we'll setup later (e.g. http://lms.mcka.local)
`LMS_BASE_DOMAIN` will be a common domain for both the LMS system and Apros system.
`LMS_SUB_DOMAIN` is the subdomain for the LMS system

#### (Optional for development) Configure the API_KEY
The value of `EDX_API_KEY` will need to match the API_KEY as configured within the LMS system; as long as they both match they can talk to each other - unless you are running LMS in __development__ mode (in which most development is performed)

    EDX_API_KEY = 'test_api_key'

**Now your Apros system is ready to talk to an LMS system**

#### Set up the database and seed data

These commands should be run before starting Apros for the first time:

    manage.py syncdb --migrate
    manage.py load_seed_data

This would build Apros database and load seed data into LMS database, including [preconfigured users][load-seed-data].

[load-seed-data]: https://github.com/mckinseyacademy/mcka_apros/blob/master/main/management/commands/load_seed_data.py#L36-L55

#### Run Apros (on port 3000)

The edX virtual environment has LMS running on port 8000. You will wish to run Apros on a different port than LMS. _This document assumes that this port is 3000, but you can choose any free port you like_

Start up Apros in development mode, which automatically updates assets from the source code therein. This is done with the following command (note that the default port is 3000 so it can be left off unless you want to override):

    ./manage.py rundev 3000





## Step 4 - Prepare LMS to accept communication from Apros

### Override specific settings in lms.env.json

This file can only be found in the devstack environment

- Log in as edxapp user `vagrant ssh -c "sudo su edxapp"`
- `cd ~`
- Edit the file `lms.env.json` in your favourite command-line editor

#### Add an array of servers for which the LMS will support CORS requests:
    "CORS_ORIGIN_WHITELIST": [
        "mcka.local"
    ],

_This should include the fully qualified domain name for the Apros system that we'll set up_

#### Enable API, CORS and PROGRESS Headers
You should find the FEATURES section already existing. _It appears that these are generally kept in alphabetical order._

    "FEATURES": {
        "API": true,
        ...
        "ENABLE_CORS_HEADERS": true,
        ...
        "MARK_PROGRESS_ON_GRADING_EVENT": true,
        ...
        "SIGNAL_ON_SCORE_CHANGED": true,
        ...
        "STUDENT_GRADEBOOK": true,
        ...
        "STUDENT_PROGRESS": true,
        ...
    },

#### (Optional for development) Configure the API_KEY
This will need to match the API_KEY that the client is using.

    "EDX_API_KEY": "test_api_key"

#### (If you are setting EDX_API_KEY) Configure the API_KEY in lms.auth.json
EDX_API_KEY also needs to be set in lms.auth.json - we are not sure why this is

    "EDX_API_KEY": "test_api_key"

**Now your LMS system is ready to receive communication from Apros**




## Step 5 - Configure your machine to use a common domain for Apros and LMS

So, the systems are now setup to talk to each other using the names `lms.mcka.local` and `mcka.local`. Now, we need to ensure that the systems will respond to those names with the correct data. There are a numer of ways of doing this, but an easy way is the included basic reverse proxy server.

### Map names in local hosts file

To allow your machine to address those names locally add the following entries to your hosts file:

    # LMS and API client names
    127.0.0.1       mcka.local
    127.0.0.1       cms.mcka.local
    127.0.0.1       studio.mcka.local

Ensure that the settings in`local_settings.py` match the entries in your hosts file.

### Set up the reverse proxy server

This proxy setup is required for xblocks authoring to work properly, since the lms and cms must be able to share cookies.

The proxy server requires twisted, so first run `pip install twisted`

Now you can start the proxy with this command:

    python -m util.devproxy

Once it's running, you can browse to http://mcka.local:8888 to see Apros.

If you want to run the proxy on port 80, add `DEV_PROXY_PORT = 80` to your `local_settings.py`, and start the proxy with `sudo python -m util.devproxy`

## After you're done

See [Initial configuration][initial-configuration] for details on configuring Apros programs, clients and students.

You may wish to enable to local mock server if you so desire. To do this, add the following to your local_settings.py file:

    RUN_LOCAL_MOCK_API = True

    API_MOCK_SERVER_ADDRESS = 'http://localhost:3000/mockapi'
    API_SERVER_ADDRESS = API_MOCK_SERVER_ADDRESS

    LOCAL_MOCK_API_FILES = [
        os.path.join(BASE_DIR, 'apiary.apib'),
        os.path.join(BASE_DIR, 'mock_supplementals.apib'),
    ]

`RUN_LOCAL_MOCK_API` indicates that the local system wants to accept mock requests
`API_MOCK_SERVER_ADDRESS` sets the mock address to use
`API_SERVER_ADDRESS` is the core server, this sets it to be the local mock server

The LOCAL_MOCK_API_FILES can be amended with additional files from which to take mock server content
apiary.apib - contains a copy of the API Blueprint from apiary
mock_supplementals.apib - currently contains specific responses for demo course in edX LMS as setup within devstack

[initial-configuration]: apros_initial_configuration.md
