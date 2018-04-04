Waffle Setup 
============

To conditionally enable/disable features Apros includes uses ``django-waffle``. 
You can read about how Waffle's features and how it works in the official 
[Waffle docs](http://waffle.readthedocs.io/en/v0.14.0/).  

Gated Features on Apros
-----------------------

The following features are currently behind a Waffle Flags/Switch/Sample: 

### New Login Flow 

**Waffle Flag**: ``use_new_login_flow``

Currently a new login flow is being tested and can be configured using the
``use_new_login_flow`` flag. If this feature is enabled (some) users will see
the new login page with the new password and SSO-based login flow. You can run 
the following management command to create this flag and enable it for 50% of
all users: 

```bash
./manage.py waffle_flag use_new_login_flow --percent=50 --create
``` 
