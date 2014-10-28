
# Prerequisites

Follow mcka_apros [setup notes][mcka-apros-setup], executing all Apros-related scripts inside virtual box. Setup assumes you checkout 
Apros repository on host machine and then share Apros root folder with devstack virtual box.

[mcka-apros-setup]: https://github.com/mckinseyacademy/mcka_apros/blob/master/SetupNotes.md

# Post SetupNotes configuration

* Add the following lines to host system /etc/hosts
        
        127.0.0.1 	mckinseyacademy.local.org
        127.0.0.1 	lms.local.org

* Modify devstack Vagrantfile to forward required ports by adding the following lines:
  
        config.vm.network :forwarded_port, guest: 3000, host: 3000
        config.vm.network :forwarded_port, guest: 8002, host: 8002

  You could use any ports > 1024, but make sure to use two distinct ports that are free on the host system and
  don't forget to modify all the listings in this file accordingly.

* Share Apros root folder with the VM by adding the following lines into Vargant file. There are lines similar to these already
  in the file, make sure you add them to proper place. There are `if ENV['VAGRANT_USE_VBOXFS'] == 'true'` block, first line should go to 
  `True` branch, second line to `False` branch

        config.vm.synced_folder "<path-to-mcka-root-folder-on-host-machine>", "/edx/mckinsey", create: true, owner: "edxapp", group: "www-data"

        config.vm.synced_folder "<path-to-mcka-root-folder-on-host-machine>", "/edx/mckinsey", create: true, nfs: true

* Reload vagrant config with `vagrant reload`, log in into vagrant box using `vagrant ssh`
* Modify nginx.conf so `server` tags added in [step 4][nginx-proxy] listen on port 8002. Reload nginx with `(sudo) nginx -s reload`
* Modify `lms.env.json` `CORS_ORIGIN_WHITELIST` to contain `mckinseyacademy.local.org:**8002**`
* Modify `mcka_apros/mcka_apros/local_settings.py` so all references to `local.org` contains port as well

        API_SERVER_ADDRESS = 'http://lms.local.org:8002'
        LMS_BASE_DOMAIN = 'local.org:8002'

  **Do not** add 8002 to `LMS_SUB_DOMAIN`

[nginx-proxy]: https://github.com/mckinseyacademy/mcka_apros/blob/master/SetupNotes.md#edit-nginxconf-to-proxy-calls-to-local-web-applications

# Running Apros

## Launching LMS

Log in into devstack vagrant box and issue the following commands

    sudo su edxapp
    paver devstack lms

Last operation launches django development server in console, so that particular tty session is busy.

## Launching Apros

Log in into devstack vagrant box and navigate to mcka_apros root folder (one containing `manage.py`).

### (First-time only) Loading seed data

If not haven't done this previously, issue the following commands to migrate db and load seed data containing preconfigured users

    ./manage.py syncdb --migrate
    ./manage.py load_seed_data

Note that loading data is done via API, so LMS should be up and running.

### Launching Apros server

    ./manage.py rundev 0.0.0.0:3000

This should launch django development server at 0.0.0.0:3000, which is forwarded to 127.0.0.1:3000 outside of vagrant box.
Again, this captures tty, so you'll be able to peek into logs and kill the server by Ctrl-C.

**Note:** by default rundev listens to 127.0.0.1:3000, which is not forwarded, so you won't be able to access Apros launched
with default settings.

### Accessing Apros

Always access Apros as `mckinseyacademy.local.org:8002` so nginx proxy are triggered and Apros -> LMS API calls contain correct origin.
Failing to do that will result in the following error when trying to view course materials:

    No 'Access-Control-Allow-Origin' header is present on the requested resource. Origin '<your origin here>' is therefore not allowed access.
