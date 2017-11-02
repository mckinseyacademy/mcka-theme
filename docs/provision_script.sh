sudo sh -c 'apt-get update -qq ; true'   # suppressing errors due to expired keys
sudo apt-get install -y gawk libreadline6-dev libyaml-dev sqlite3 autoconf libgdbm-dev libncurses5-dev automake libtool libffi-dev libsqlite3-dev bison libgmp-dev libgmp-dev

sudo apt-get -y install nginx
sudo cp /edx/app/apros/mcka_apros/docs/mcka_apros_production /etc/nginx/sites-available/mcka_apros
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


sudo -Hu apros bash << REQUIREMENST_SCRIPT
  cd ~/mcka_apros
  source ~/venvs/mcka_apros/bin/activate  # Use the Apros Python environment.
  pip install -U pip
  pip install -r requirements.txt
REQUIREMENST_SCRIPT
