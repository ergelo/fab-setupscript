import settings as s

from fab_helpers import *

env.hosts = s.hosts

def main():
    """
    checks the settings and calls the appropriate setup functions
    """

    if s.single_machine_setup:
        dev_setup()
    else:
        db_setup()
        dev_setup()

#################################
#                               #
#       setup functions         #
#                               #
#################################

def dev_setup():
    "setup dev server machine"
    
    root()
    
    update_apt()
    user_routine()

    user()

    apt_setup()
    pip_setup()

    setup_ssh()
    compile_hosts()

    github_egg_setup()

    webserver_setup_routine()

    if s.single_machine_setup:
        db_setup_routine()

    django_site_setup_routine()
