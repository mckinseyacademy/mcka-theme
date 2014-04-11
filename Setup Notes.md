# Setting up McKinsey Academy (Apros) with local LMS

As the edX API starts to mature it becomes more desirable to develop the Apros product while hooked up to a real edX LMS system.

This document explains how to achieve this in a development environment. The steps we'll follow are as follows:

1. Setup edX Environment
- Prepare the McKinsey Academy project to talk to specific version of LMS
- Prepare LMS to respond to API / XBlock requests from Apros
- Configure your system to use a common domain between Apros and LMS

_Throughout, this document refers to the names `lms.local.org` and `mckinseyacademy.local.org`. It should be noted that these are simply names that we'll use when adding the systems to the same domain. You can use whatever names you like, but the important thing is that they have a common domain, to allow easy access to the LMS session cookie within Apros which enables data transfer through the XBlock._

## Step 1 - Setup edX devstack Environment

By far the simplest way to set up the edX system is to install the devstack environment which includes a virtualbox environment that runs a separate machine to host the edX platform and conveniently shares folders so that the edX-platform code resides on the host machine.

Follow the instructions at https://github.com/edx/configuration/wiki/edX-Developer-Stack

The devstack environment maps some local ports so that LMS and CMS (Studio) serve content on the host machines ports 8000 and 8001 respectively.

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





## Step 2 - Prepare Apros to talk to specific instance of LMS

### Setup McKinsey Academy project on your machine

    git clone git@github.com:mckinseyacademy/mcka_apros.git
or

    git clone https://github.com/mckinseyacademy/mcka_apros.git

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
    LMS_BASE_DOMAIN = 'local.org'
    LMS_SUB_DOMAIN = 'lms'

`API_SERVER_ADDRESS` could be the dns name that we'll setup later (e.g. http://lms.local.org)
`LMS_BASE_DOMAIN` will be a common domain for both the LMS system and Apros system.
`LMS_SUB_DOMAIN` is the subdomain for the LMS system

#### (Optional for development) Configure the API_KEY
The value of `EDX_API_KEY` will need to match the API_KEY as configured within the LMS system; as long as they both match they can talk to each other - unless you are running LMS in __development__ mode (in which most development is performed)

    EDX_API_KEY = 'test_api_key'

**Now your Apros system is ready to talk to an LMS system**

#### Run Apros on port 3000

The edX virtual environment has LMS running on port 8000. You will wish to run Apros on a different port than LMS. _This document assumes that this port is 3000, but you can choose any free port you like_

Start up Apros in development mode, which automatically updates assets from the source code therein. This is done with the following command:
    
    ./manage.py rundev 3000





## Step 3 - Prepare LMS to accept communication from Apros

### Override specific settings in lms.env.json

This file can only be found in the devstack environment
    
- Log in as edxapp user `vagrant ssh -c "sudo su edxapp"`
- `cd ~`
- Edit the file `lms.env.json` in your favourite command-line editor

#### Add an array of servers for which the LMS will support CORS requests:
    "CORS_ORIGIN_WHITELIST": [
        "mckinseyacademy.local.org"
    ],

_This should include the fully qualified domain name for the Apros system that we'll set up_

#### Enable API and CORS Headers
You should find the FEATURES section already existing. _It appears that these are generally kept in alphabetical order._

    "FEATURES": {
        "API": true,
        ...
        "ENABLE_CORS_HEADERS": true, 
        ...
    }, 

#### (Optional for development) Configure the API_KEY
This will need to match the API_KEY that the client is using.

    "EDX_API_KEY": {"test_api_key"}

**Now your
 LMS system is ready to receive communication from Apros**




## Step 4 - Configure your machine to use a common domain for Apros and LMS

So, the systems are now setup to talk to each other using the names `lms.local.org` and `mckinseyacademy.local.org`. Now, we need to ensure that the systems will respond to those names with the correct data. There are a numer of ways of doing this, but a good way is using nginx.

### Map names in local hosts file

To allow your machine to address those names locally add the following entries to your hosts file:

    # LMS and API client names
    127.0.0.1       lms.local.org
    127.0.0.1       mckinseyacademy.local.org


### Install nginx

* On Mac - `brew install nginx`
* On Windows - Follow the instuctions at http://nginx.org/en/docs/windows.html
* On Linux - `sudo yum install nginx` or `sudo apt-get install nginx` depending upon your system (refer to http://nginx.org/en/linux_packages.html for more details)

It is worth a quick look at the nginx beginners' guide - http://nginx.org/en/docs/beginners_guide.html

### Edit nginx.conf to proxy calls to local web applications

nginx uses information in the `nginx.conf` file to configure its operation _(by default on Mac it appears to be installed in /usr/local/etc/nginx)_

Change `nginx.conf` to proxy calls to `lms.local.org` and `mckinseyacademy.local.org` as follows:

    # 1 - McKinsey Academy server
    server {
        listen 80;
        server_name  mckinseyacademy.local.org;
        location / {
            # proxy to django listening on 127.0.0.1:3000
            proxy_pass http://localhost:3000/;
        }
        # proxy calls to c4x to lms asset host
        location /c4x/ {
            proxy_pass http://localhost:8000/c4x/;
        }
    }
    #
    # 2 - LMS Server
    server {
        listen 80;
        server_name  lms.local.org;
        location / {
            # proxy to django listening on 127.0.0.1:8000
            proxy_pass http://localhost:8000/;
        }
    }


### Startup nginx

Simply execute the command `(sudo) nginx`.

If you edit the nginx.conf file at any time, you will need to reload nginx with the following command:

    (sudo) nginx -s reload

**With Python environments one may become used to changes taking effect without a restart - changes to nginx.conf will not take effect unless the reload command is executed**

To stop nginx use the command:

    (sudo) nginx -s quit