import subprocess
import signal
import sys
import time
from datetime import datetime
from os.path import exists


class GracefulKiller:
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self):
        self.kill_now = True


class Command:
    def __init__(self):
        self.get_uptime = 'uptime -s'
        self.iptables_restore = 'iptables-restore < /nsm/iptableslist.txt'
        self.docker_is_active = 'systemctl is-active docker'
        self.process = None

    def run(self, command):
        self.process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return self.process.communicate()

    def kill(self):
        self.process.kill()


if __name__ == '__main__':
    cmd = Command()
    killer = GracefulKiller()
    restored = False
    while not killer.kill_now:
        if not restored and cmd.run(cmd.docker_is_active)[0].decode('utf-8').strip() == 'active':
            if exists('/nsm/iptableslist.txt'):
                cmd.run(cmd.iptables_restore)
                restored = True
                print('[{now}] [INFO] Restored iptables'.format(now=datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                killer.exit_gracefully()
            else:
                print('[{now}] [ERROR] File not found: /nsm/iptableslist.txt'.format(now=datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            sys.stdout.flush()
        time.sleep(3)
