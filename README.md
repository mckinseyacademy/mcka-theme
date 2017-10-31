Open edX Theme for McKinsey Academy
===================================

This theme contains (S)CSS overrides used to make XBlocks match the
desired appearance within Apros and/or the various native mobile apps.

Mobile apps use the LMS webviews directly, so the only way to style
XBlocks in the mobile apps is to put style overrides into this theme
(i.e. they can't be put into Apros).

Configuration
-------------

**On devstack**:

First, clone this repo to the `themes` directory on your devstack.

Then, in `lms.env.json` and `cms.env.json`:

1. Set `"ENABLE_COMPREHENSIVE_THEMING": true,`
1. Set `"COMPREHENSIVE_THEME_DIRS": ["/edx/app/edxapp/themes"],`
1. Set `"DEFAULT_SITE_THEME": "mcka-theme",`

**Via Ansible**:

Set these ansible variables:

```
EDXAPP_ENABLE_COMPREHENSIVE_THEMING: true
EDXAPP_COMPREHENSIVE_THEME_DIRS:
  - '/edx/app/edxapp/themes'
EDXAPP_DEFAULT_SITE_THEME: 'mcka-theme'
edxapp_theme_name: 'mcka-theme'
edxapp_theme_source_repo: 'https://github.com/mckinseyacademy/mcka-theme.git'
edxapp_theme_version: 'mcka-theme'
```

TBD: Deploy key or make the repo public
