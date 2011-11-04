from fabric.api import *
from fabric.contrib.console import confirm
import settings as s
import configs as cf


#########################
#                       #
#       routines        #
#                       #
#########################

def user_routine():
    """
    as root user, this routine creates the user, adds him to the sudoers file, 
    and creates the /home/web/ directory (where our app will live), assigning 
    it to the user
    """

    root()

    createuser()
    make_su(s.username)

    user()
    sudo("mkdir -p /home/web/")
    sudo("chown -R %s /home/web/" % s.username)




#########################
#                       #
#        helpers        #
#                       #
#########################

#functions to change between connection users
def root():
    "to log in as root"
    local('ssh-add ~/.ssh/%s.pem' % s.pemkey_name)
    env.user = 'root'
    env.keyfilename = '~/.ssh/%s.pem' % s.pemkey_name

def user():
    "to login as user"
    env.user = s.username
    env.password = s.password
    env.keyfilename = ''

#debian management
def createuser():
    "add user and set password"
    run('adduser --disabled-password --gecos "" %s' % s.username)
    run('echo "%s:%s" | chpasswd' % (s.username, s.password))

def make_su(username):
    "make user a su"
    install('sudo')
    run('echo "%s  ALL=(ALL) ALL" >> /etc/sudoers' % s.username)
    run('chmod 440 /etc/sudoers')

#package installing functions
def apt_install(package):
    sudo('apt-get --yes install %s' % package)

def pip_install(module):
    sudo("pip install %s" % module)

def github_egg_install(user, project):
    run('git clone https://github.com/%s/%s.git' % (user, project))
    with cd('%s/' % project):
        sudo('python setup.py install')
    sudo('rm -rf %s' % project)

#installation frameworks setup
def update_apt():
    "update apt sources"
    run('apt-get update')

def apt_setup():
    packages = ' '.join(s.dev_packages)
    apt_install(packages)

def pip_setup():
    sudo("easy_install pip")
    modules = ' '.join(s.dev_modules)
    pip_install(modules)

def github_egg_setup():
    for egg in s.dev_github_eggs:
        github_egg_install(egg[user], egg[project])

#networking
def setup_ssh():
    run('ssh-keygen -t dsa -N "" -f ~/.ssh/id_rsa')
    get('.ssh/id_rsa.pub', 'temp_rsa.pub')
    local('cat temp_rsa.pub')
    local('rm temp_rsa.pub')
    
    confirm('Copied key to GitHub?')

    run('git config --global user.name "%s"' % s.github_name)
    run('git config --global user.email "%s"' % s.github_email)

def compile_hosts():
    lines = []
    root()
    # for x in ['web', 'db']:
    #     for i, host in enumerate(env.roledefs[x]):
    #         with settings(host_string=host):
    internal = '.'.join(run('hostname').split('.')[0].split('-')[1:])
    external = '.'.join(env.host_string.split('.')[0].split('-')[1:])
    lines.append('%s %s_dev1_int' % (internal, prefix))
    lines.append('%s %s_dev1_ext' % (external, prefix))
    for l in lines:
        sudo('echo %s >> /etc/hosts' % l)

#webserver functions
def amazon_reload():
    "Reload Apache to pick up new code changes."
    user()
    sudo("invoke-rc.d apache2 reload")

def nginx_reload():
    "Reload nginx"
    user()
    sudo("invoke-rc.d nginx reload")

def nginx_test():
    local('echo "%s" > testnginx.conf' % cf.nginx)

