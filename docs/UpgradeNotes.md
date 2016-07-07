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

* Execute following sql queries on mcka_apros database:
```
$ mysql -u username -p password
$ use mcka_apros;
RENAME TABLE admin_accesskey TO admin_apros_accesskey;
RENAME TABLE admin_batchoperationerrors TO admin_apros_batchoperationerrors;
RENAME TABLE admin_batchoperationstatus TO admin_apros_batchoperationstatus;
RENAME TABLE admin_brandingsettings TO admin_apros_brandingsettings;
RENAME TABLE admin_clientcustomization TO admin_apros_clientcustomization;
RENAME TABLE admin_clientnavlinks TO admin_apros_clientnavlinks;
RENAME TABLE admin_companycontact TO admin_apros_companycontact;
RENAME TABLE admin_companyinvoicingdetails TO admin_apros_companyinvoicingdetails;
RENAME TABLE admin_dashboardadminquickfilter TO admin_apros_dashboardadminquickfilter;
RENAME TABLE admin_emailtemplate TO admin_apros_emailtemplate;
RENAME TABLE admin_learnerdashboard TO admin_apros_learnerdashboard;
RENAME TABLE admin_learnerdashboarddiscovery TO admin_apros_learnerdashboarddiscovery;
RENAME TABLE admin_learnerdashboardtile TO admin_apros_learnerdashboardtile;
RENAME TABLE admin_tilebookmark TO admin_apros_tilebookmark;
RENAME TABLE admin_userregistrationbatch TO admin_apros_userregistrationbatch;
RENAME TABLE admin_userregistrationerror TO admin_apros_userregistrationerror;
```

* Mark existing migrations as applied
```
$ ./manage.py migrate --fake-initial
```

* Migrate the apps 
```
$ ./manage.py migrate
```
