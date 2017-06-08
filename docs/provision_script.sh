sudo sh -c 'apt-get update -qq ; true'   # suppressing errors due to expired keys
sudo apt-get install -y gawk libreadline6-dev libyaml-dev sqlite3 autoconf libgdbm-dev libncurses5-dev automake libtool libffi-dev libsqlite3-dev bison libgmp-dev libgmp-dev

sudo apt-get -y install nginx
sudo cp /edx/app/apros/mcka_apros/docs/mcka_apros /etc/nginx/sites-available/mcka_apros
sudo ln -s /etc/nginx/sites-{available,enabled}/mcka_apros
sudo service nginx restart

mysqladmin -u root create mcka_apros
mysqladmin -u root create edx

if [ -d "/edx/app/apros" ];
then
  sudo useradd apros --home /edx/app/apros --gid www-data --shell /bin/bash
  sudo cp -r /etc/skel/. /edx/app/apros/
  sudo chown apros:www-data /edx/app/apros
else
  sudo useradd apros --home /edx/app/apros --gid www-data --create-home --shell /bin/bash
fi


id -u apros &>/dev/null || sudo useradd apros --home /edx/app/apros --gid www-data --create-home --shell /bin/bash
sudo chown -R apros:apros /edx/app/apros

sudo -Hu apros bash << RVM_SCRIPT
  cd ~
  mkdir venvs
  virtualenv venvs/mcka_apros
  # Standard warnings about curling to bash apply.
  gpg --keyserver hkp://keys.gnupg.net --recv-keys 409B6B1796C275462A1703113804BB82D39DC0E3
  bash <(curl -sSL https://get.rvm.io) stable
  # This will automatically be sourced on the next login.
  source /edx/app/apros/.rvm/scripts/rvm
  # If this fails for some reason, it should give you a list of things to install with apt.
  rvm install ruby-1.9.3 --autolibs=read-fail
  rvm use 1.9.3 --default

  sed -i -e '4icd ~/mcka_apros\' ~/.bashrc
  echo "
source ~/venvs/mcka_apros/bin/activate  # Use the Apros Python environment.
source ~/.rvm/scripts/rvm # Load RVM into a shell session *as a function*
  " >> ~/.bashrc
RVM_SCRIPT

sudo -Hu apros bash << REQUIREMENST_SCRIPT
  cd ~/mcka_apros
  source ~/venvs/mcka_apros/bin/activate  # Use the Apros Python environment.
  source ~/.rvm/scripts/rvm # Load RVM into a shell session *as a function*
  pip install -U pip
  pip install -r requirements.txt
  gem install sass --version 3.3.14
REQUIREMENST_SCRIPT
