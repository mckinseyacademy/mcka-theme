sudo sh -c 'apt-get update -qq ; true'   # suppressing errors due to expired keys
sudo apt-get install -y gawk libreadline6-dev libyaml-dev sqlite3 autoconf libgdbm-dev libncurses5-dev automake \
        libtool libffi-dev libsqlite3-dev bison libgmp-dev libgmp-dev libmysqlclient-dev


exists=$(grep -c "^apros:" /etc/passwd)
if [ $exists -eq 0 ];
then
  sudo useradd apros --home /edx/app/apros --gid www-data --shell /bin/bash
  sudo cp -r /etc/skel/. /edx/app/apros/
  sudo chown apros:www-data /edx/app/apros
else
  sudo useradd apros --home /edx/app/apros --gid www-data --create-home --shell /bin/bash
fi


id -u apros &>/dev/null || sudo useradd apros --home /edx/app/apros --gid www-data --create-home --shell /bin/bash

sudo chown -R apros:www-data /edx/app/apros

sudo -Hu apros bash << VENV_SCRIPT
  cd ~
  mkdir venvs
  rm -rf venvs/mcka_apros
  virtualenv -p python3 venvs/mcka_apros

  sed -i -e '4icd ~/mcka_apros\' ~/.bashrc
  echo "source ~/venvs/mcka_apros/bin/activate  # Use the Apros Python environment." >> ~/.bashrc
VENV_SCRIPT

sudo -Hu apros bash << REQUIREMENST_SCRIPT
  cd ~/mcka_apros
  source ~/venvs/mcka_apros/bin/activate  # Use the Apros Python environment.
  pip install -U pip
  pip install -r requirements.txt
REQUIREMENST_SCRIPT
