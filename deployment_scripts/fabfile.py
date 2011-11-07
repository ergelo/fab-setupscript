from fabric.api import *
from fabric.contrib.console import confirm

import getpass

################
#    config    #
################

env.hosts = ['']
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
    if confirm('Merging "%s" in "development", deleting and pushing?'):
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
    with cd('home/web/%s/' % project_directory):
        run('git checkout development')
        run('git pull origin development')

#push development from local to github
def push():
    local('git push origin development')

#pushes branch to github and merges with development
def close_branch(branch):
    if confirm('Merging "%s" in "development", deleting and pushing?'):
        local('git push origin %s' % branch)
        local('git checkout development')
        local('git merge --no-ff %s' % branch)
        local('git branch -d %s' % branch)
        push()

#creates a new branch off "development"
def new_branch(branch):
    local('git checkout -b %s development' % branch)
    local('git push origin %s' % branch)
