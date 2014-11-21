# Setting up McKinsey Academy (Apros) with a local LMS Installation

This document aims to guide a new developer to set up an Apros installation. While this guide is primarily aimed 
toward developers, the instructions within could be modified to create a deployment instance.

The steps we'll follow are as follows:

1. Setup the edX Environment
2. Setup the Apros Environment
3. Modify the LMS installation to use the features we want so it can communicate with Apros
4. Set up the reverse Proxy server
5. Start Apros

This document will make the assumptions that:

* You will be using the domain name `lms.mcka.local` for your LMS instance on port 8000 (the devstack default).
* You will be using the domain name `cms.mcka.local` for your CMS instance on port 8001 (the devstack default).
* You will be using the domain name `mcka.local` for your Apros instance.
* You wish to use a SQLite database and basic development server for this environment on port 3000.
* You will be using a Vagrant VM-based devstack.

## Step 1 - Setup edX devstack Environment

While it is possible to create a development environment on your machine, it is highly recommended to use a vagrant 
instance. The instructions for the rest of this document assume you will do so.

Follow the directions on the [Solutions wiki][solutions-wiki] to set up an *edx-solutions* devstack.

[solutions-wiki]: http://github.com/edx-solutions/edx-platform/wiki/Setting-up-the-solutions-devstack

### Set up the Host System to Recognize the Hostnames

* Add the following lines to host system `/etc/hosts`. This will allow your host machine to know where the domain names 
should point to. It will also work for the guest instance, since the guest instance trusts the host's name lookups.
        
        127.0.0.1   mcka.local
        127.0.0.1   lms.mcka.local
        127.0.0.1   cms.mcka.local

### Create a user to run Apros under

Just as `edxapp` is used to run the LMS and CMS, you will want a separate user with its own Python Virtual Environment
and Ruby Version Manager to run Apros under.

Log into the vagrant instance with `vagrant ssh`. From the vagrant user's prompt, run:

    # Needed for RVM.
    sudo apt-get install -y gawk libreadline6-dev libyaml-dev sqlite3 autoconf libgdbm-dev \
        libncurses5-dev automake libtool libffi-dev libsqlite3-dev bison
        
If this is your first time creating this VM (that is, you haven't already modified your vagrant file as specified 
in the next section), do the following:

    sudo useradd apros --home /edx/app/apros --gid www-data --create-home --shell /bin/bash 

Otherwise, do this:

    sudo useradd apros --home /edx/app/apros --gid www-data --shell /bin/bash
    sudo cp -r /etc/skel/. /edx/app/apros/
    sudo chown apros:www-data /edx/app/apros

Next, run:

    sudo su - apros # The prompt should now say you're logged in as apros@
    mkdir venvs
    virtualenv venvs/mcka_apros
    # Standard warnings about curling to bash apply.
    bash <(curl -sSL https://get.rvm.io) stable
    # This will automatically be sourced on the next login.
    source /edx/app/apros/.rvm/scripts/rvm
    # If this fails for some reason, it should give you a list of 
    # things to install with apt.
    rvm install ruby-1.9.3 --autolibs=read-fail
    rvm use 1.9.3 --default
    

Edit the user's .bashrc file in your favorite editor. Add the lines:

    cd ~/mcka_apros
    source ~/venvs/mcka_apros/bin/activate  # Use the Apros Python environment.
    source ~/.rvm/scripts/rvm # Load RVM into a shell session *as a function*


...at the top, before anything else. Finally, exit this user's shell. We'll be loading back into it later.

Do not worry that the directory `mcka_apros` does not exist. It will be created in the next section.

### Modify the VagrantFile
* Modify the devstack Vagrantfile to forward required port by adding the following lines:
  
        config.vm.network :forwarded_port, guest: 80, host: 8080

  You will want to *forward port 80 on your host machine to port 8080, because of the privileged port restrictions*.
  The method for this differs from OS to OS, but some guides are available 
  [here for mac](http://www.dmuth.org/node/1404/web-development-port-80-and-443-vagrant) and 
  [here for linux](http://serverfault.com/questions/112795/how-can-i-run-a-server-on-linux-on-port-80-as-a-normal-user).
  The guide for mac has some extra tips you may be able to backport to your Linux installation. Several Apros features do
  not work quite correctly without being on Port 80 due to the way session IDs are handled between it and the LMS.

* Clone the Apros repository **in your vagrant staging folder**, like so:

 
    git clone git@github.com:mckinseyacademy/mcka_apros.git

 or
 
    git clone https://github.com/mckinseyacademy/mcka_apros.git
 
 Make note of the path to the repository, as you will use it in the next step.

* Share Apros root folder with the VM by adding the following lines into Vargant file. There are lines similar to these already
  in the file, make sure you add them to proper place. There are `if ENV['VAGRANT_USE_VBOXFS'] == 'true'` block, first line should go to 
  `True` branch, second line to `False` branch

        config.vm.synced_folder "<path-to-mcka-root-folder-on-host-machine>", "/edx/app/apros/mcka_apros",
            create: true, owner: "apros", group: "www-data"

        config.vm.synced_folder "<path-to-mcka-root-folder-on-host-machine>", "/edx/app/apros/mcka_apros",
            create: true, nfs: true

* Reload vagrant config with `vagrant reload`, log in into vagrant box using `vagrant ssh`. If the vagrant instance was
 not running, use `vagrant up` instead of `vagrant reload`.

## Step 2 - Setup Apros Environment

After following the previous instructions, you should be able to jump right into the codebase at any time by running:

    vagrant ssh
    sudo su apros
    
We'll do Apros's configuration as this user.

### Install Python requirements
Apros's requirements are handled in a requirements.txt file. To install the requirements, run:
 
    pip install -r requirements.txt


### Install Other requirements
We require SASS to be used to build assets

    gem install sass --version 3.3.14

Notes:
* Sass 3.4+ is not compatible - see https://github.com/zurb/foundation-rails/pull/96


### Override Specific Settings

The McKinsey Academy application hosts it's `settings.py` file within the mcka_apros app folder (this is a subfolder 
within the same-named `mcka_apros` repository root folder). Alongside this file, create a new file 
named `local_settings.py`.

#### Set up the database

**If you'd like to use Sqlite instead of MySQL, add the following lines**:

    import os
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

_Sqlite is sometimes easier to operate with than mySql, but this is purely a choice for the developer. It may be wise to stick with MySql if you want to remain as close to the production environment as desired._

**If you want to use MySQL, you will need to create a MySQL database with users and permissions according to the `settings.py` file, or ones of your own creation in `local_settings.py`.**

#### Configure the name to use for the LMS instance, like this:

    API_SERVER_ADDRESS = 'http://lms.mcka.local'
    LMS_BASE_DOMAIN = 'mcka.local'
    LMS_SUB_DOMAIN = 'lms'

`API_SERVER_ADDRESS` is the base URI for accessing the LMS via the Apros server application
`LMS_BASE_DOMAIN` This is the base domain name of the LMS system, with its port.
`LMS_SUB_DOMAIN` is the subdomain for the LMS system


## Step 3 - Prepare the LMS for Apros

The LMS will need a few additional settings to work with Apros.

### Override specific settings in lms.env.json

This file can only be found in the devstack environment

- Log in as edxapp user `vagrant ssh -c "sudo su edxapp"`
- `cd ~`
- Edit the file `lms.env.json` in your favourite command-line editor

At the top of the dictionary, add this line:

        "ADDL_INSTALLED_APPS": ["progress"],
        
This will install the progress application.

You should find the **FEATURES** section already exists, and you will want to add a few items to it. _It appears that these are generally kept in alphabetical order, but for simplicity, you may wish to just add these items to the **beginning** of the array._

        "API": true,
        "MARK_PROGRESS_ON_GRADING_EVENT": true,
        "SIGNAL_ON_SCORE_CHANGED": true,
        "STUDENT_GRADEBOOK": true,
        "STUDENT_PROGRESS": true,
        "ORGANIZATIONS_APP": true,
        "PROJECTS_APP": true,
        
Finally, run:

    paver update_db --settings=devstack

This will install the tables for the `progress` application.


### Step 4 - Set up the reverse proxy server

For security purposes, browsers have very rigid rules on how they'll handle sharing of content between domains and ports. 
In order to make sure that Apros is able to load remote resources from the LMS (such as assets and the content of XBlocks),
you will need to set up a reverse proxy server.

As the `vagrant` user, run:

    sudo apt-get -y install nginx
    
Create a file at `/etc/nginx/sites-available/mcka_apros`
    
...and paste in these contents:

    server {
        listen 80;
        
        server_name mcka.local;
        
        location / {
            proxy_pass http://localhost:3000;
            proxy_set_header Host $host;
        }
    }

    server {
        listen 80;

        server_name lms.mcka.local;

        location / {
            proxy_pass http://localhost:8000;
            proxy_set_header Host $host;
            add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
            add_header "Access-Control-Allow-Credentials" "true";
            add_header "Access-Control-Allow-Origin" "http://mcka.local";
            add_header "Access-Control-Allow-Headers" "X-CSRFToken,X-Requested-With,Keep-Alive,User-Agent,If-Modified-Since,Cache-Control,Content-Type,DNT,X-Mx-ReqToken";
            if ($request_method = 'OPTIONS') {
                return 204;
            }
        }
    }

Enable this new virtual host with:

    sudo ln -s /etc/nginx/sites-{available,enabled}/mcka_apros
    sudo service nginx restart
    

## Step 5 - Start Apros

#### Set up the database and seed data

To begin setting up Apros, **launch the LMS and forum/comment service and leave them running**. Then, run the following commands as the `apros` user: 

    manage.py syncdb --migrate
    manage.py load_seed_data

This will build the Apros database and load seed data into the LMS database, including [preconfigured users][load-seed-data].

[load-seed-data]: https://github.com/mckinseyacademy/mcka_apros/blob/master/main/management/commands/load_seed_data.py#L36-L55

At this point, everything should be in place, and you should be able to start Apros from the `apros` user's command line with:

    ./manage.py rundev 3000
    
**Make sure the LMS and the Forum/Comment services are running whenever you run Apros** as Apros relies on remote API calls to these.

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

## Appendix A: Troubleshooting

### Logins don't work

Try the following:

    * Make sure both LMS and Apros are running
    * Clear all cookies.
    * Restart LMS and Apros
    
Sessions are a bit persnickety in Apros due to the fact that they must be aligned between both the LMS and Apros.

## Appendix B: 'Real-Word' Deployments

Deployments of Apros that are publicly accessible should differ in several respects. Chiefly:

1. The database used should be MySQL instead of SQLite.
2. A proper WSGI application server should serve Apros and the LMS, such as Gunicorn or uwsgi. See the edx-platform 
   documentation for information of deploying edx-platform for production.
3. You will need to generate and set API keys for use between the server and Apros, and turn off the DEBUG flag.


## Appendix C: Production-like assets management

Static assets (js, css, images, etc.) are served in quite different ways in development and production:

* Development serves assets from where they are, thus allowing for quicker modify-reload-check cycle.
* Production uses pipelines ([django-pipeline][dj-pipeline]) to concatenate js and css files into larger bundles
to improve page load time. To further reduce application server load, static files are served by nginx.

So, to achieve prodution-like assets management in development, the following steps need to be performed:

* Enable pipelines: pipelines are governed by two settings: `PIPELINES` and `FEATURES['USE_DJANGO_PIPELINE']`.
  Both need to be set to true. While it's possible to set `FEATURES['USE_DJANGO_PIPELINE']` via `[cl]ms.env.json`,
  `PIPELINES` can only be set in configuration file (e.g. `[cl]ms/envs/devstack.py`). **Please make sure you don't
  accidentally commit it.**
* Set up nginx proxying. The cleaniest way would be to copy `/etc/nginx/sites-available/mcka_apros` (e.g. `mcka_apros_prod`) 
  and modify it's contents, than toggle between `mcka_apros` and `mcka_apros_prod`. [Nginx ensite][nginx_ensite] script 
  comes in very handy for toggling them.

`mcka_apros_prod` should contain the following rules added to corresponding `location` sections.

For `server_name mcka.local` location:

    location ~ /static/(?P<file>.*) {
        root /edx/app/apros/mcka_apros;      # this should point to apros root folder, containing manage.py
        try_files /static_cache/$file /static/$file @proxy_to_lms_nginx;
    }
    
    location @proxy_to_lms_nginx {
        proxy_set_header X-Forwarded-Proto $http_x_forwarded_proto;
        proxy_set_header X-Forwarded-Port $http_x_forwarded_port;
        proxy_set_header X-Forwarded-For $http_x_forwarded_for;
        proxy_set_header Host $host;

        proxy_redirect off;
        proxy_pass http://localhost:8000;    # this should be address of lms, as seen from inside the virtual box
    }

For `server_name lms.mcka.local` location:

    location ~ ^/static/(?P<file>.*) {
        root /edx/var/edxapp/;               # this should point to where lms collectstatic puts static files
        try_files /staticfiles/$file /course_static/$file =404;

        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS';
        add_header "Access-Control-Allow-Credentials" "true";
        add_header "Access-Control-Allow-Origin" "http://mcka.local";
        add_header "Access-Control-Allow-Headers" "X-CSRFToken,X-Requested-With,Keep-Alive,User-Agent,If-Modified-Since,Cache-Control,Content-Type,DNT,X-Mx-ReqToken";

        # return a 403 for static files that shouldn't be
        # in the staticfiles directory
        location ~ ^/static/(?:.*)(?:\.xml|\.json|README.TXT) {
            add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS';
            add_header "Access-Control-Allow-Credentials" "true";
            add_header "Access-Control-Allow-Origin" "http://mcka.local";
            add_header "Access-Control-Allow-Headers" "X-CSRFToken,X-Requested-With,Keep-Alive,User-Agent,If-Modified-Since,Cache-Control,Content-Type,DNT,X-Mx-ReqToken";
            return 403;
        }

        # http://www.red-team-design.com/firefox-doesnt-allow-cross-domain-fonts-by-default
        location ~ "/static/(?P<collected>.*\.[0-9a-f]{12}\.(eot|otf|ttf|woff))" {
            expires max;
            add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS';
            add_header "Access-Control-Allow-Credentials" "true";
            add_header "Access-Control-Allow-Origin" "http://mcka.local";
            add_header "Access-Control-Allow-Headers" "X-CSRFToken,X-Requested-With,Keep-Alive,User-Agent,If-Modified-Since,Cache-Control,Content-Type,DNT,X-Mx-ReqToken";
            try_files /staticfiles/$collected /course_static/$collected =404;
        }

        # Set django-pipelined files to maximum cache time
        location ~ "/static/(?P<collected>.*\.[0-9a-f]{12}\..*)" {
            expires max;
            add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS';
            add_header "Access-Control-Allow-Credentials" "true";
            add_header "Access-Control-Allow-Origin" "http://mcka.local";
            add_header "Access-Control-Allow-Headers" "X-CSRFToken,X-Requested-With,Keep-Alive,User-Agent,If-Modified-Since,Cache-Control,Content-Type,DNT,X-Mx-ReqToken";

            # Without this try_files, files that have been run through
            # django-pipeline return 404s
            try_files /staticfiles/$collected /course_static/$collected =404;
        }

        # Expire other static files immediately (there should be very few / none of these)
        expires epoch;
    }

Cors headers `add_header` blocks are identical and must be duplicated in all nested locations, as it appears that `add_header` directives are not inherited. 

[dj-pipeline]: http://django-pipeline.readthedocs.org/en/latest/
[nginx_ensite]: https://github.com/perusio/nginx_ensite
