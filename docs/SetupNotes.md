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
* You will be using the domain name `apros.mcka.local` for your Apros instance.
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
        
        127.0.0.1   apros.mcka.local
        127.0.0.1   lms.mcka.local
        127.0.0.1   cms.mcka.local

### Create a user to run Apros under

Just as `edxapp` is used to run the LMS and CMS, you will want a separate user with its own Python Virtual Environment
and Ruby Version Manager to run Apros under.

Log into the vagrant instance with `vagrant ssh`. From the vagrant user's prompt, run:

    # Make sure our links to all downloads are up to date.
    sudo apt-get update
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
    gpg --keyserver hkp://keys.gnupg.net --recv-keys 409B6B1796C275462A1703113804BB82D39DC0E3
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
  not work quite correctly without being on Port 80 due to the way session IDs are handled between it and the LMS. NOTE: for
  Yosemite OSX users ipfw (which that link describes) is no longer available, please see this [link for
  Yosemite](http://www.abetobing.com/blog/port-forwarding-mac-os-yosemite-81.html)

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

_Sqlite is sometimes easier to operate with than mySql, but this is purely a choice for the developer. It may be wise to
stick with MySql if you want to remain as close to the production environment as desired._

**If you want to use MySQL, you will need to create a MySQL database with users and permissions according to the 
`settings.py` file, or ones of your own creation in `local_settings.py`.**

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

        "ADDL_INSTALLED_APPS": ["progress", "organizations"],
        
This will install the progress application.

You should find the **FEATURES** section already exists, and you will want to add a few items to it. 
_It appears that these are generally kept in alphabetical order, but for simplicity, you may wish to just add these 
items to the **beginning** of the array._

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
    
Create a file at `/etc/nginx/sites-available/mcka_apros` using [example development config][example-config]. **Note that this is a 
minimal working example that lacks some special rules set in production.** Some minor features not necessary for most of 
development may not work (e.g. serving discussion user profiles from Apros rather than LMS). For complete example 
replicating actual production rules see [Appendix C][appendix-c].

Enable this new virtual host with:

    sudo ln -s /etc/nginx/sites-{available,enabled}/mcka_apros
    sudo service nginx restart
    

[example-config]: mcka_apros
[appendix-c]: #appendix-c-complete-production-routing
    

## Step 5 - Start Apros

#### Set up the database and seed data

To begin setting up Apros, **launch the LMS and forum/comment service and leave them running**. Then, run the following commands as the `apros` user: 

    ./manage.py syncdb --migrate
    ./manage.py load_seed_data

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


## Appendix C: Complete production routing

In production environment both Apros and LMS are served from the same domain, and sophisticated nginx rule set is used
to separate them. As a result, all requests pass through the same nginx server, so further customization is possible.
Another advantage of such setup is that there are no CORS requests at all.
 
So, in order to serve both LMS and Apros on the same domain, one need the following:

* (First time only) Set up production nginx proxying. The cleaniest way to do that while still being able to revert to 
  simpler setup would be to create new nginx virtual server (e.g. `mcka_apros_production`) using [example 
  production-like config][example-nginx-config]. 
* Switch to `mcka_apros_production` config. [Nginx ensite][nginx_ensite] script comes in very handy for switching between
  nginx virtual server configurations. 
* Modify Apros settings file so that `LMS_SUB_DOMAIN+'.'+LMS_BASE_DOMAIN` would be equal to Apros domain name. Example
  nginx config assumes `apros.mcka.local`, so the values should be: `LMS_SUB_DOMAIN='apros'`, `LMS_BASE_DOMAIN='mcka.local'`
* Don't forget to restart Apros if it was already running.

One way to make sure everything works as expected is to check Ajax requests sent by discussion xblock. With development
settings it uses lms domain name explicitly (i.e. request goes to `lms.mcka.local/...`), while with production-like it goes 
to Apros domain first, than got processed by nginx rules (i.e. request goes to `apros.mcka.local/...`)

To revert to development configuration simply unod these steps, i.e. set `LMS_SUB_DOMAIN='lms'` and switch back to `mcka_apros`.

Please note that [example config][example-nginx-config] is built based on actual ansible scripts used to deploy
[apros][apros-ansible-config], minus `apros_app_server` upstream and related directives (they are replaced with 
hard-coded reference to `localhost:3000` where Apros should be served by default). 


Apros does not work correctly if accessed from a non-standard HTTP port, so all nginx setups mentioned serves it on port 
80. However, there's a problem that Apros runs in a devstack virtual box, so port 80 is not directly accessible from 
host system, and it cannot be mapped to host's port 80 via Vagrantfile as mapping to priviledged ports (<1024) is 
restricted to superusers only. There are two options to solve this issue:

1. Vagrant maps guest port 80 to host port 8080. So, in order to access Apros at default HTTP port you will need to set 
   up a port redirect rule on your host system to forward traffic from port 80 to 8080. If you are using Linux, an 
   iptables script to do so can be found [there][apros-iptables]. Note those iptables rules are are transient, so script
   needs to be executed on every host system reload.
2. Devstack box is configured with two network interfaces, one of which is "Host-only adapter". If you do not plan to
   access Apros from any machine except localhost, you could edit `/etc/hosts` (or its equivalent in your OS) to contain 
   the following rules, **instead** of rules set up earlier (actual IP might change later, check out 
   `config.vm.network :private_network, ip: "192.168.33.10".` directive.
   
   
       192.168.33.10   apros.mcka.local lms.mcka.local studio.mcka.local


[example-nginx-config]: mcka_apros_production
[apros-iptables]: iptables_config.sh
[nginx_ensite]: https://github.com/perusio/nginx_ensite
[apros-ansible-config]: https://github.com/open-craft/ansible-private/blob/master/roles/mckinsey_apros/templates/edx/app/nginx/sites-available/mcka_apros.j2


## Appendix D: Production-like assets management

Static assets (js, css, images, etc.) are served in quite different ways in development and production:

* Development serves assets from where they are, thus allowing for quicker modify-reload-check cycle.
* Production uses pipelines ([django-pipeline][dj-pipeline]) to concatenate js and css files into larger bundles
to improve page load time. To further reduce application server load, static files are served by nginx.

So, to achieve production-like assets management in development, the following steps need to be performed:

* (First time only) Create yet another nginx config `mcka_apros_production_pipelined` using [example production-like 
  config with pipelines][example-pipelined-apros-config]. This config is essentially equal to [example production-like 
  config][example-nginx-config], except `location @proxy_to_lms_nginx` points to virtual server set up in `lms_pipeline_assets`, 
  rather than to LMS application location, and `lms.mcka.local` section rewritten to properly serve pipelined static assets.
* Enable pipelines: pipelines are governed by `FEATURES['USE_DJANGO_PIPELINE']` and disabled in development environment
  by default. To set it to true edit `[cl]ms.env.json` so that `FEATURES` block has `'USE_DJANGO_PIPELINE': true`.
* Set `DEBUG` setting to `False` - there are some mechanisms in XBlock runtime system that rewrite urls starting with `/static/`
  to be served from course modulestore. There's a shortcut through that mechanism enabled by `DEBUG=True`,
  so URLs that exist in filesystem are served from filesystem and yield significantly different URLs. This setting need to 
  be set in `[cl]ms/envs/devstack.py`. **Please make sure you don't accidentally commit it.**.
* Setting `DEBUG` to `False` activates the edx api key mechanism; in case you haven't configured it yet you should not be 
  able to log in into Apros. To solve this issue edit `lms/envs/devstack.py` so that `EDX_API_KEY` values both in 
  `edx-platform/lms/envs/devstack.py` and `mcka_apros/mcka_apros/settings.py` match.
* As `edxapp` user run `paver update_assets --settings=devstack` - this will place compiled assets to where `lms_pipeline_assets`
  expects them to be. Note that `paver devstack lms` does not run `collectstatic` so it won't work here. 
* Switch to `mcka_apros_production_pipelined`. This replaces `mcka_apros_production`, so `mcka_apros` and `mcka_apros_production`
  must be disabled.
  
To make sure everything works as expected check what static assets are loaded. If you see something like 
`lms-style-app-extend1.[12 hex digits].css` pipelines are enabled properly.
  
To revert to production config with non-pipelined assets switch back to `mcka_apros_production` and undo all `[cl]ms/envs/devstack.py`
modifications. It's fine to leave `USE_DJANGO_PIPELINE` set to true in `[cl]ms.env.json` as static url rewrites shortcut
the actual rewriting if `DEBUG` is set to true.


[dj-pipeline]: http://django-pipeline.readthedocs.org/en/latest/
[example-nginx-config]: mcka_apros_production
[example-pipelined-apros-config]: mcka_apros_production_pipelined
[example-pipelined-static-config]: lms_pipeline_assets


