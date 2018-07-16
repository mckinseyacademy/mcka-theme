#!/bin/bash

# This file is for devstack and developers only for running traslation commands.
# Usage:
# 1: chmod +x filename.sh
# 2: ./translations.sh
cd ..
for lang in locale/*
do
	bn=$(basename $lang)
	if [ $bn != 'config.yaml' ]
	then
		echo "translating locale $bn"
		django-admin makemessages -l $bn --extension=html,haml,py
	 	django-admin makemessages --locale=$bn --domain=djangojs --ignore=gen/* --ignore=static_cache/* --ignore=vendor/*
		python manage.py compilemessages -l $bn
	fi
done
