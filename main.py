import subprocess
import signal
import time
from datetime import datetime
from os.path import exists


class GracefulKiller:
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, *args):
        self.kill_now = True


class Command:
    def __init__(self):
        self.get_uptime = 'uptime -s'
        self.iptables_save = 'iptables-save > /nsm/iptableslist.txt'
        self.iptables_restore = 'iptables-restore < /nsm/iptableslist.txt'
        self.process = None

    def run(self, command):
        self.process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return self.process.communicate()

    def kill(self):
        self.process.kill()


def dt_2_ts(dt):
    dt = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
    ts = time.mktime(dt.timetuple())
    return ts


if __name__ == '__main__':
    cmd = Command()
    killer = GracefulKiller()
    restored = False
    while not killer.kill_now:
        if not restored:
            now = dt_2_ts(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            uptime = dt_2_ts(cmd.run(cmd.get_uptime)[0].decode('utf-8').strip())
            # If uptime is less than 3 minutes, restore iptables
            if exists('/nsm/iptableslist.txt') and now - uptime < 180:
                cmd.run(cmd.iptables_restore)
                restored = True
                print('[{now}] [INFO] Restored iptables'.format(now=datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        time.sleep(3)
