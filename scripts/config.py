import pexpect
import re
import sys
import time

from argh import arg, alias, ArghParser


def array_to_flex_ip(leader_ip, compute_nodes):
    # Note: Leader IP must be listed first when using flexible IP format
    if not isinstance(leader_ip, str):
        raise TypeError
    if isinstance(compute_nodes, list):
        return "%s;%s" % (leader_ip, ";".join(compute_nodes))
    elif isinstance(compute_nodes, str):
        return "%s;%s" % (leader_ip, compute_nodes)


def number_of_nodes(leader_count, compute_nodes):
    if not isinstance(leader_count, int):
        raise TypeError
    if isinstance(compute_nodes, list):
        return leader_count + len(compute_nodes)
    elif isinstance(compute_nodes, int):
        return leader_count + compute_nodes


def use_ip(string, ip):
    """Function to determine if a string includes a given IP"""
    if re.search(" %s " % ip, string):
        return "yes"
    else:
        return "no"


@alias('phase1')
@arg('--installer', type=str, default='/mnt/matrix/install_padb')
@arg('--leader-ip', type=str)
@arg('--compute-nodes', type=str, help='Comma seperated list of IPs')
@arg('--root-password', type=str)
@arg('--leader-count', type=int, default=1)
@arg('--standby-count', type=int, choices=[0,1], default=0)
def phase1_install(args):
    """Complete Phase 1 installation process of Actian Matrix leader node"""
    installer = getattr(args, 'installer')
    leader_ip = getattr(args, 'leader_ip')
    compute_nodes = getattr(args, 'compute_nodes').split(",")
    root_password = getattr(args, 'root_password')
    leader_count = getattr(args, 'leader_count')
    standby_count = getattr(args, 'standby_count')

    yes = "yes"  # In case installer is switched to use y/n
    no = "no"  # In case installer is switched to use y/n

    child = pexpect.spawn(installer)
    child.expect("Choose install task")
    child.sendline("1")

    child.expect("Type 'accept' if you accept the terms of the ParAccel EULA")
    child.sendline("accept")

    child.expect("Dedicated leader node")
    child.sendline(yes)

    child.expect("Total nodes in the cluster including leader and standby")
    child.sendline("%s" % number_of_nodes(leader_count, compute_nodes))

    i = child.expect(["Number of standby compute nodes",
                      "Use IP.* for PADB cluster"])
    if i == 0:
        child.sendline("%s" % standby_count)

        child.expect("Use IP.* for PADB cluster")
        child.sendline(use_ip(child.after, leader_ip))
    elif i == 1:
        child.sendline(use_ip(child.after, leader_ip))

    child.expect("Use IP.* for PADB cluster")
    child.sendline(use_ip(child.after, leader_ip))

    i = child.expect(["Use IP.* for PADB cluster",
                      "Are cluster node IPs sequential"])
    if i == 0:
        child.sendline(use_ip(child.after, leader_ip))

        child.expect("Are cluster node IPs sequential")
        child.sendline(no)
    elif i == 1:
        child.sendline(no)

    child.expect("Enter cluster flexible IP specification")
    child.sendline(array_to_flex_ip(leader_ip, compute_nodes))

    child.expect("Automate compute node install")
    child.sendline(yes)

    child.expect("Use existing paraccel user account")
    child.sendline(no)

    child.expect("Group name for installation")
    child.sendline("paraccel")

    # Number of user tables expected
    child.expect("Please select from the options above")
    child.sendline("2")

    # Work load type
    child.expect("Please select from the options above")
    child.sendline("1")

    child.expect("Do you wish to review your selections")
    child.sendline(no)

    child.expect("Enter the compute node root password")
    child.sendline(root_password)

    child.expect("Re-enter the compute node root password")
    child.sendline(root_password)

    child.expect("Run a set of non-destructive tests to verify cluster "
                 "readiness for PADB installation")
    child.sendline(no)

    child.expect("Start PADB installation")
    child.sendline(yes)

    child.expect("Reboot the leader node now", timeout=1200)
    child.sendline(no)

    child.close()


@alias('phase2')
@arg('--user', type=str, default='paraccel')
@arg('--password', type=str, help='Password for paraccel on compute nodes')
@arg('--setup', type=str,
     default='/home/paraccel/scripts/stage_two_install.py')
@arg('--start-delay', type=int, default=90)
def phase2_install(args):
    """ Second part of the Matrix install, run as the paraccel user. Make sure
    the setup script is patched prior to running phase 2 """
    user = getattr(args, 'user')
    password = getattr(args, 'password')
    start_delay = getattr(args, 'start_delay')
    setup = getattr(args, 'setup')

    time.sleep(start_delay)

    yes = "yes"  # In case installer is switched to use y/n
    no = "no"  # In case installer is switched to use y/n

    setup_command = "su -l %s -c '%s'" % (user, setup)
    child = pexpect.spawn(setup_command)
    child.expect("Press ENTER to begin")
    child.sendline('')

    child.expect("Is the above information correct")
    child.sendline(yes)

    i = child.expect(["Firewall options", "Press ENTER to continue"])
    if i == 0:
        child.sendline("1")

        child.expect("Press ENTER to continue")
        child.sendline('')
    elif i == 1:
        child.sendline('')

    child.expect("Is the above information correct")
    child.sendline(yes)

    child.expect("Do you want to configure PADB to send email alerts")
    child.sendline(no)

    child.expect("Enter new paraccel password for all nodes", timeout=1200)
    child.sendline(password)

    child.expect("Re-enter new paraccel password for all nodes")
    child.sendline(password)

    child.expect("Secure server by removing sudo access from the paraccel "
                 "account")
    child.sendline(yes)

    child.expect("Retain paraccel sudo access to renice")
    child.sendline(yes)

    child.expect("Press ENTER to continue:")
    child.sendline('')

    child.expect("Type the task number")
    child.sendline('7')

    child.close()


def main():
    """Shell entry point for execution"""
    try:
        argparser = ArghParser()
        argparser.add_commands([
            phase1_install,
            phase2_install,
        ])

        argparser.dispatch()
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
