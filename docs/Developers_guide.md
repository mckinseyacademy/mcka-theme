# Apros Developer’s Guide
This is a general developer's guide for the Apros environment made to help developers. If you find something missing here 
and think of it as important, please open up a PR and add to the file. Thanks.



## Vagrant setup:

  If you are setting up Apros on a mac and have access to a peer's mac machine with the setup already installed in it, 
  Refer to the  **Share vagrant setup (Mac only)** section below. Otherwise, please continue.
  
- Setup Part I (LMS): https://github.com/edx-solutions/edx-platform/wiki/Setting-up-the-solutions-devstack
- Setup Part II (Apros): https://github.com/wajeeha-khalid/mcka_apros/blob/master/docs/SetupNotes.md
- Google Groups link: https://groups.google.com/forum/#!forum/openedx-ops

The following sub-section demonstrates solutions to commonly faced issues during the apros and lms setups mentioned above.
If you get 404 on the pages above, Please coordinate with the development team and make sure your github id has proper access rights.
### Issues


- #### "msg": "Failed to update apt cache."
  Solution:
  ```
  vagrant ssh
  sudo -i
  sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 69464050
  ```

- #### failed: E: dpkg was interrupted, you must manually run 'sudo dpkg --configure -a' to correct the problem
  Solution:
  ```
  export DEBIAN_FRONTEND=noninteractive
  export LANGUAGE=en_US.UTF-8
  export LANG=en_US.UTF-8
  export LC_ALL=en_US.UTF-8
  locale-gen en_US.UTF-8
  sudo dpkg-reconfigure locales
  ```

- #### locales is broken or not fully installed
  Solution:
  `sudo dpkg --configure -a`

- #### This is not a git repository (/ecommerce)
  Solution:
  ```
  cd ~/solutions/ecommerce/
  git remote add https://github.com/edx/ecommerce
  git pull
  cd ..
  vagrant provision
  ```

- #### In apros, while running ./manage.py collectstatic --noinput fails saying:
  IOError: [Errno 37] No locks available
  Solution:
  ```
  sudo systemctl enable rpc-statd  # Enable statd on boot
  sudo systemctl start rpc-statd  # Start statd for the current session
  ```

- #### Load seed data gives error in edx-platform.
  Solution:
  switch edx branch to development

- #### "Gemfile could not be found" or **Gemfile version conflict** occurs.
  Solution:
  Simply replace the "cs_comment_services" folder in devstack-solutions with someone’s who's forum is working fine.

- #### Xblocks are not loading at client.
  Solution:
  Make sure the following entries are in FEATURES inside the "lms.env.json" 
  vagrant ssh
  sudo su edxapp
  cd ..
  nano lms.env.json
  Then in FEATURES,
  "ENABLE_XBLOCK_VIEW_ENDPOINT": true,
  "ENABLE_NOTIFICATIONS": true

- #### While running vagrant up, **NFS fails**.
  Solution:
  `sudo apt-get install nfs-common nfs-kernel-server`

### Share vagrant setup (Mac only)
1.  Install virtual box and vagrant on the remote machine
2.  Get box from any mac by running this command
`vagrant package --base [machine name as it shows in virtual box] --output /Users/myuser/Documents/Workspace/my.box
3. Copy devstask folder and this box on your machine
4. Remove vagrant file from devstack folder and save it somewhere else
5. Init vagrant with this command
vagrant init [machine name as it shows in virtual box] /Users/myuser/Documents/Workspace/my.box`
6. Run vagrant up
7. Above command will throw some errors but let it run
8. Replace vagrant file with saved(original) vagrant file
9. run vagrant halt and then vagrant up 
10. add this line at the end of your /etct/hosts
`192.168.33.10 apros.mcka.local lms.mcka.local cms.mcka.local saml.mcka.local`


## Vagrant: General
- Shutting down the host machine without running vagrant halt can cause **pymongo errors** when you run vagrant up next time. To resolve, type in the following on by one on as a vagrant user:
  ```
  sudo rm /edx/var/mongo/mongodb/mongod.lock
  sudo mongod -repair --config /etc/mongod.conf
  sudo chown -R mongodb:mongodb /edx/var/mongo/.
  sudo service mongod start
  ```
  If you face the error `sudo: /etc/init.d/mongod: command not found` try the following:
  `sudo rm /edx/var/mongo/mongodb/mongod.lock && sudo mongod -repair --config /etc/mongod.conf && sudo chown -R mongodb:mongodb /edx/var/mongo/. && sudo systemctl start mongod.service`


- Set staff to super user from within the database:
  ```
  vagrant ssh
  sudo su edxapp
  mysql -u root -p
  mysql> show databases;
  use edxapp
  mysql> show tables;
  select * from auth_user;
  mysql> update auth_user set is_superuser=1 where username='staff';
  mysql> exit 
  ```

- Exposing local sever through public IP to other machines
  Author: Zaman Afzal
  - Set ALLOW_HOSTS in settings to *.
  - SSH in your virtual machine and go to `cd /etc/nginx/sites-available/mcka_apros`
  - Copy the whole second dict of server and paste it again at the end.
  - Change the listen to 9999;
  - Change the server_name to YOUR_IP
  - Save this file.
  - Open your vagrant file and add the following line
    `config.vm.network :forwarded_port, guest: 9999, host: 9999 # Public Apros
    after 
    `config.vm.network :forwarded_port, guest: 80, host: 8080 # Apros`
  - Save the file
  - `vagrant reload`
  - If you strat getting 278 on login then remove following from the local settings.
    ```
    LMS_SESSION_COOKIE_DOMAIN = '.mcka.local'
    SESSION_COOKIE_DOMAIN = '.mcka.local'
    ```


## Xblocks:

- Installing Xblocks for the first time
  Make a new folder ‘xblocks’ in devstack-solutions/edx-platform
  Follow the installation instructions in https://github.com/edx/xblock-sdk inside this folder.


- Replace installed xblock with local in edx-platform for debugging (Poll xblock in this example):
  ```
  vagrant ssh
  sudo su edxapp
  pip freeze | grep poll
  pip uninstall xblock_poll
  pip install -e ~/xblocks/xblock-poll/
  ```
  
## SSH Access:
  ### Setup:
  After coordinating with the development team and making sure your github id has access to qa/stage, put the following in `~/.ssh/config on your host. Just replace `GITHUB_ID` with your github ID.

  ```
  Host qa-mckinsey-*
  proxycommand ssh -W %h:%p GITHUB_ID@qa-bastion.mckinsey.edx.org 2> /dev/null
  user GITHUB_ID

  Host qa-mckinsey-integration-2
  HostName 10.254.1.87
  User GITHUB_ID
  StrictHostKeyChecking no

  Host qa-mckinsey-qa
  HostName 10.254.1.106
  User GITHUB_ID
  StrictHostKeyChecking no

  Host stage-mckinsey
  HostName 10.1.10.192
  User GITHUB_ID
  StrictHostKeyChecking no

  Host qa-bastion.mckinsey.edx.org
  user GITHUB_ID
  DynamicForward 8091
  ```

  ### Access:
  For QA, type in your terminal: 
  `ssh qa-mckinsey-qa`

  For Stage we can only access DB through the following two steps:
  `ssh GITHUBUSERNAME@stage-bastion.mckinsey.edx.org`
  then
  `/edx/bin/edxapp-rds.sh`
  
## Supervisor
  ### Supervisor Commands:
  Following are the Supervisor commands that can be entered after ssh’ing into qa.
  - Supervisor status
    `/edx/bin/supervisorctl status`
  - Restart server
    `/edx/bin/supervisorctl restart mcka_apros`
  - LMS Sample Management Command Run
    `sudo -u edxapp /edx/bin/python.edxapp manage.py lms --settings=aws compute_social_engagement_score`
  - Sample lms pip command
    `sudo -u edxapp /edx/bin/pip.edxapp freeze`
  - Sample apros pip command
    `sudo -u edxapp /edx/bin/pip.mcka_apros freeze`

  ### Supervisor logs:
  Supervisor logs can be found in edx/var/log/supervisor. To view a log file enter the following command:
  ```tail -n 200 [FILE_NAME]```

  Where 200 is the most recent number of lines to be shown from the file.
