# Setting up McKinsey Academy (Apros) with a local LMS Installation

This document aims to guide a new developer to set up an Apros installation. While this guide is primarily aimed 
toward developers, the instructions within could be modified to create a deployment instance.

The steps we'll follow are as follows:

1. Setup the Solutions Devstack
2. Setup the Apros Environment
3. Set up the reverse Proxy server
4. Start the LMS and forum services
5. Start Apros

This document will make the assumptions that:

* You will be using the domain name `lms.mcka.local` for your LMS instance on port 8000 (the devstack default).
* You will be using the domain name `cms.mcka.local` for your CMS instance on port 8001 (the devstack default).
* You will be using the domain name `apros.mcka.local` for your Apros instance.
* You wish to use a basic development server for this environment on port 3000.
* You will be using a Vagrant VM-based devstack.

This document referes to `lms.env.json`, `lms.auth.json`, `cms.env.json` and `cms.auth.json` files. THey are located in
`edxapp` user home directory (one level above `edx-platform`  directory), which is normally located at `/edx/app/edxapp`.

## Step 1 - Set up the Solutions Devstack

While it is possible to create a development environment on your machine, it is highly recommended to use a vagrant 
instance. The instructions for the rest of this document assume you will do so.

Follow the directions on the [Solutions wiki][solutions-wiki] to set up an *edx-solutions* devstack.

[solutions-wiki]: http://github.com/edx-solutions/edx-platform/wiki/Setting-up-the-solutions-devstack

### Set up the Host System to Recognize the Hostnames

* Add the following line to your host system's `/etc/hosts`. This will allow your host machine to know where the domain names 
should point to. It will also work for the guest instance, since the guest instance trusts the host's name lookups.
        
        192.168.33.10   apros.mcka.local lms.mcka.local cms.mcka.local
        
### Clone the Apros repository

Make sure you clone it **in the same directory as the Vagrantfile**. Run:

    git clone git@github.com:mckinseyacademy/mcka_apros.git

or

    git clone https://github.com/mckinseyacademy/mcka_apros.git

**Note:** The mcka_apros directory may already exist, and should be empty before you run this command. That is normal.

### Modify the VagrantFile (Usually not necessary)

If you are using the recommended Vagrantfile (from the Solutions devstack instructions), it will already be setup to work with Apros, so you can skip this section. Specifically, it should share the "mcka_apros" folder into the VM at `/edx/app/apros/mcka_apros`:

    ```ruby
    MOUNT_DIRS = {
        ...
        :apros => {:repo => "mcka_apros", :local => "/edx/app/apros/mcka_apros", :owner => "apros"},
        ...
    }
    ```
    
    and it should have an "apros" provisioner defined:

    ```ruby
    config.vm.provision "apros", type: "shell", path: "<path_to_mcka_apros_directory>/docs/provision_script.sh"
    ```
    )

If you had to modify the Vagrantfile, reload your vagrant config with `vagrant reload`.

### Provision Apros

Run the apros provision script on your host with `vagrant provision --provision-with apros`

The script will do the following:

* Setup required system packages
* Install Nginx and configure "apros" site
* Create databases required for Apros
* Create `apros` user
* Create virtualenv and setup python requirements
* Install ruby 1.9.3, create ruby env
* Update `apros` ~/.bashrc to automatically activate apros virtualenv and rubyenv and jump to mcka_apros folder

If something goes wrong instructions to install everything manually are available at [Appendix E][appendix-e].

[appendix-e]: #appendix-e-manual-apros-environment-provisioning

### Override Specific Settings

The McKinsey Academy application hosts it's `settings.py` file within the mcka_apros app folder (this is a subfolder 
within the same-named `mcka_apros` repository root folder). Alongside this file, create a new file 
named `local_settings.py`.

#### Configure the name to use for the LMS instance, like this:

Put the following into `mcka_apros/mcka_apros/local_settings.py`

    API_SERVER_ADDRESS = 'http://lms.mcka.local'
    LMS_BASE_DOMAIN='mcka.local'
    LMS_SUB_DOMAIN='apros'
    EDX_API_KEY = 'edx_api_key'
    SESSION_COOKIE_SECURE = False
    ALLOWED_HOSTS = ['apros.mcka.local']

Details: 
* `API_SERVER_ADDRESS` is the base URI for accessing the LMS via the Apros server application
* `LMS_BASE_DOMAIN` This is the base domain users will fetch LMS assets from.
* `LMS_SUB_DOMAIN` is the subdomain for the LMS system that users will fetch assets from-- note that it's the same as apros because we use NginX's reverse proxying to do a bit of magic later in the configuration.
* `EDX_API_KEY` is the api key used for accessing the LMS API.
* `SESSION_COOKIE_SECURE` to `False` allows cookies to work with HTTP setup.

##### Configure the `EDX_API_KEY` in `lms.auth.json`

Edit `/edx/app/edxapp/lms.auth.json` and change 

    "EDX_API_KEY": "PUT_YOUR_API_KEY_HERE",

to

    "EDX_API_KEY": "edx_api_key",

Explanation: `EDX_API_KEY` in `lms.auth.json` and `local_settings.py` must match for apros to be able to communicate with the LMS API.
 
## Start the LMS and forum services

These services need to be running for Apros to work. Start them and leave them
running before moving on to the next step.

### To start the LMS:

As the `vagrant` user:

    sudo su edxapp                   # switch to the edxapp user (this will also cd to /edx/app/edxapp/edx-platform)

    # Optional: Run the migrations. This is usually not necessary since the Solutions Devstack
    # Setup Guide already told you to run these migrations.
    ./manage.py lms migrate --settings=devstack
    ./manage.py cms migrate --settings=devstack

    # Start the LMS
    # Omit --fast if you have updated edx-platform since the last time you ran it without --fast, to rebuild static assets
    paver devstack lms --fast

### To start the forum:

As the `vagrant` user:

    sudo su forum                          # switch to the forum user (this will also cd to /edx/app/forum/cs_comments_service)
    bundle install                         # install ruby dependencies
    ruby app.rb -p 18080                   # start the forum

## Step 5 - Start Apros

#### Set up the database and seed data

To begin setting up Apros, **make sure that the LMS and forum/comment service are running**. Then, as the `vagrant` user:

    sudo su apros
    ./manage.py migrate
    ./manage.py load_seed_data

This will build the Apros database and load seed data into the LMS database, including [preconfigured users][load-seed-data].
When it finishes, run:

    ./manage.py rundev 3000

Wait for the above to finish pre-processing, then Ctrl+C out of it.
It will bring bundles of assets up to date, which will then need to be further collected.
It is finished processing when it says 'Watching 10 bundles for changes...'
Finally, collect all the static assets.

    ./manage.py collectstatic --noinput

At this point, everything should be in place, and you should be able to start Apros from the `apros` user's command line with:

    ./manage.py rundev 3000
    
**Make sure the LMS and the Forum/Comment services are running whenever you run Apros** as Apros relies on remote API calls to these.

[load-seed-data]: https://github.com/mckinseyacademy/mcka_apros/blob/master/main/management/commands/load_seed_data.py#L36-L55

## After you're done

You should now be able to access apros at http://apros.mcka.local/ .

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

[initial-configuration]: ../apros_initial_configuration.md

## Appendix A: Troubleshooting

### Logins don't work

Try the following:

    * Make sure both LMS and Apros are running
    * Clear all cookies.
    * Restart LMS and Apros
    
Sessions are a bit persnickety in Apros due to the fact that they must be aligned between both the LMS and Apros.

### Apros not working on a Linux host

In case you have issues with the Apros website on Linux and LMS and the forum are working, chances are that the port forwarding isn't working properly. To fix that try adding the [Mac rules in Vagrant](https://www.danpurdy.co.uk/web-development/osx-yosemite-port-forwarding-for-vagrant/) with adding the [iptables rules for Linux](http://serverfault.com/questions/112795/how-can-i-run-a-server-on-linux-on-port-80-as-a-normal-user). Note that the added iptables rules are deleted upon reboot, if you are on Debian you can use [this](http://unix.stackexchange.com/questions/52376/why-do-iptables-rules-disappear-when-restarting-my-debian-system) to make the rules permanent.

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

Setting this up requires creating a new NginX configuration. For easier switching between configurations, consider [NginX Ensite][nginx_ensite]. To get yourself up and running with pipeline:

* (First time only) Create another nginx config `mcka_apros_production_pipelined` using [example production-like 
  config with pipelines][example-pipelined-apros-config]. This config is essentially equal to [the normal 
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
[nginx_ensite]: https://github.com/perusio/nginx_ensite
[example-nginx-config]: mcka_apros_production
[example-pipelined-apros-config]: mcka_apros_production_pipelined
[example-pipelined-static-config]: lms_pipeline_assets


## Appendix D: Setting up an XBlock development workflow

XBlocks are usually developed using the workbench, and then finally tested on the platform. Accordingly, a good workflow for developing them is to run the workbench on the host machine, and allow access to the code via the Vagrant box. To set up this workflow, you should enter the vagrant directory for your solutions devstack, where the folders edx-platform, cs_comments_service and mcka_apros reside, and create a new directory with named `xblocks` alongside these.

Next, edit your Vagrantfile. Add the following entry to the `MOUNT_DIRS` hash:

```ruby
MOUNT_DIRS = {
    ...
    :xblocks => {:repo => "xblocks", :local => "/edx/app/edxapp/xblocks", :owner => "edxapp"},
    ...
}
```

You will then be able to access this directory as the edxapp user from `~/xblocks` within the VM, and install them from there while editing them from whatever virtualenvs you like on the host.

## Appendix E: Manual Apros environment provisioning

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

    source ~/venvs/mcka_apros/bin/activate  # Use the Apros Python environment.
    source ~/.rvm/scripts/rvm # Load RVM into a shell session *as a function*


...at the top, before anything else. After the line `[ -z "$PS1" ] && return` add:

    cd ~/mcka_apros

Finally, exit this user's shell. We'll be loading back into it later.

Do not worry that the directory `mcka_apros` does not exist. It will be created in the next section.

### Setup Apros Environment

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

### Creating default databases

To create the default databases, run:

    mysqladmin -u root create mcka_apros
    mysqladmin -u root create edx


### Set up the reverse proxy server

As the `vagrant` user, run:

    sudo apt-get -y install nginx

Create a file at `/etc/nginx/sites-available/mcka_apros` with [these contents][example-nginx-config]. 
**Note these rules aren't *precisely* like production.** 
If you need to precompile assets for pipelining, see [Appendix C][appendix-c].

[example-nginx-config]: mcka_apros_production

Enable this new virtual host with:

    sudo ln -s /etc/nginx/sites-{available,enabled}/mcka_apros
    sudo service nginx restart
    

[example-config]: mcka_apros
[appendix-c]: #appendix-c-complete-production-routing

## Appendix F: Celery Configuration
We are using celery for background tasks processing it requires RabbitMQ as broker. To configure celery on dev environment set `BROKER_URL` in your `local_settings.py` with specified username, password and host and then start celery worker using command:

    ./manage.py celery worker --loglevel=info

if want to avoid setting up RabbitMQ and running celery workers, you can directly execute the tasks when you queue them by adding following line in your `local_settings.py` file

    CELERY_ALWAYS_EAGER = True

