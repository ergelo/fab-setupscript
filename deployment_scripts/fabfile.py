from fabric.api import *
from fabric.contrib.console import confirm

import getpass

################
#    config    #
################

env.hosts = ['']
project_directory = ''
username = ''
password = '' #optional

################
#    scripts   #
################

#push development from local, pull it and restart apache remotely
def deploy():
    if confirm('did you commit the stuff you\'re deploying?'):
        user()
        push()
        pull()
        apache()

#pushes branch to github and merges with development
def close_branch(branch):
    if confirm('Merging "%s" in "development", deleting and pushing (did you commit)?' % branch):
        user()
        local('git push origin %s' % branch)
        local('git checkout development')
        local('git merge --no-ff %s' % branch)
        local('git branch -d %s' % branch)
        push()

#creates a new branch off "development"
def new_branch(branch):
    user()
    local('git checkout -b %s development' % branch)
    local('git push origin %s' % branch)

#nukes the db, creates a new one and runs syncdb, optionally south migrate as well
def reset_db(dbname, south=False):
    if confirm('You are deleting the database without backing up, sure you want to proceed?'):
        user()
        nuke_db(dbname)
        with cd('/home/web/%s/' % project_directory):
            run('django-admin.py syncdb')
            if south:
                run ('django-admin.py migrate')

################
#    helpers   #
################

#logs in user
def user():
    env.user = username
    env.password = password if password else getpass.getpass()

#restart apache
def apache():
    user()
    sudo("/etc/init.d/apache2 restart")

#restart nginx
def nginx():
    user()
    sudo("/etc/init.d/nginx restart")

#pull new development code
def pull():
    user()
    with cd('/home/web/%s/' % project_directory):
        run('git checkout development')
        run('git pull origin development')

#push development from local to github
def push():
    local('git push origin development')

#delete the db and create a new one with the same name
def nuke_db(dbname):
    user()
    run("dropdb %s" % dbname)
    run("createdb -O %s %s" % (username, dbname))
