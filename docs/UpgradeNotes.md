Upgrading from Django 1.6 to Django 1.8
==========

This document aims to guide a developer to upgrade an Apros installation to Django 1.8.13.

### Notes:

* SSH to your VM and activate apros user:
  ```
  $ vagrant ssh
  $ sudo su apros
  ```
  
* Install the requirements (you should be in /edx/app/apros/mcka_apros folder):
```
$ pip install -r requirements.txt
```

* Execute following management command:
```
$ ./manage.py rename_admin_apros_tables {db_alias}
```
Check your mcka_apros database db_alias in settings.py under DATABASES


* Mark existing migrations as applied
```
$ ./manage.py migrate --fake-initial
```

* Migrate the apps 
```
$ ./manage.py migrate
```
