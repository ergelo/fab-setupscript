This is the generalised version of the script I use to quickly setup and deploy
my django projects to Amazon AWS. It currently supports an 'all in one' test
machine, but I have a version that makes a distinction between db and dev
machines. The setup is loosely based on Jacobian's [Django Deployment
Workshop](https://github.com/jacobian/django-deployment-workshop) and includes:

* Postgresql database server
* Nginx as a front and media server
* Apache to serve the django site

It is based on Debian 6.0, and is tested on the following amazon AMIs:

* debian-6.0-squeeze-base-i386-20110417 (ami-6bb5821f)

It is obviously a work in progress, here is the TODO list:

* comment code, especially settings file
* further customise config file templates
* db machines
* multi-machine setups

Also includes a fabfile for deployment tools. This is geared towards some
common routines in our workflow, such as resetting the db,
opening/closing feature branches, deploying to server and backing up to
github.
****

**Instructions**

_Server Setup Script_
Fill in your settings, then execute `fab main` and it will do its magic. More
to come.

_Deployment Tools_
Fill in the settings at the top of the fabfile, run commands.
