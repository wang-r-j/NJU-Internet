#!/usr/bin/env python3

import requests
import getpass
import json
import time
import os
import sys
import signal
import argparse
from typing import Optional


class NJUInternet:
    LOGIN_URL = 'https://p.nju.edu.cn/api/portal/v1/login'
    LOGOUT_URL = 'https://p.nju.edu.cn/api/portal/v1/logout'

    def __init__(self, username: Optional[str] = None, stdin=False, logpath: Optional[str] = None):
        self.username = username
        self.password = None
        self.stdin = stdin
        self.noprint = False
        self.logpath = logpath

    def readpw(self):
        if self.username is None:
            print('NJUID: ', end='', file=sys.stderr, flush=True)
            self.username = input()
        if self.password is None:
            if self.stdin:
                if sys.stdin.isatty():
                    print('warning: Password will be echoed. Please remove the "-i" option.', file=sys.stderr)
                self.password = input()
            else:
                self.password = getpass.getpass(prompt='Password: ')

    def printerr(self, *args):
        if not self.noprint:
            print(*args, file=sys.stderr)
        elif self.logpath is not None:
            with open(self.logpath, 'a') as f:
                print(*args, file=f)

    def login(self):
        self.readpw()
        post_json = {
            'domain': 'default',
            'username': self.username,
            'password': self.password,
        }
        try:
            r = requests.post(NJUInternet.LOGIN_URL, json=post_json)
        except Exception as e:
            self.printerr(e)
            self.printerr('Failed to login')
            return False
        if r.status_code == 200 and json.loads(r.text)['reply_code'] == 0:
            self.printerr('Login successfully')
            return True
        else:
            self.printerr('Respose code:', r.status_code)
            self.printerr('Respose data:', r.text)
            self.printerr('Failed to login')
            return False

    def logout(self):
        post_json = {'domain': 'default'}
        try:
            r = requests.post(NJUInternet.LOGOUT_URL, json=post_json)
        except Exception as e:
            self.printerr(e)
            self.printerr('Failed to logout')
            return False
        if r.status_code == 200 and json.loads(r.text)['reply_code'] == 0:
            self.printerr('Logout successfully')
            return True
        else:
            self.printerr('Respose code:', r.status_code)
            self.printerr('Respose data:', r.text)
            self.printerr('Failed to logout')
            return False

    def keep(self, tstp=False, duration=-1., retry_interval=1., check_interval=6.):
        time_end = time.time() + duration * 3600
        while True:
            time_sleep = (check_interval if self.login() else retry_interval) * 3600
            if tstp:
                os.kill(os.getpid(), signal.SIGTSTP)
                tstp = False
                self.noprint = True
            if duration >= 0 and time.time() + time_sleep >= time_end:
                if time_end > time.time():
                    time.sleep(time_end - time.time())
                return self.logout()
            time.sleep(time_sleep)


def main():
    parser = argparse.ArgumentParser(
        prog=sys.argv[0],
        description='Login, keep login or logout from Internet in NJU.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.epilog = (
            'examples:\n'
            '  {prog} login\n'
            '  {prog} logout\n'
            '  {prog} keep --tstp; bg; disown\n'
    ).format(prog=parser.prog)
    parser.add_argument('cmd', default='login', nargs='?', choices=['login', 'logout', 'keep'], help='the action you want to perform')
    parser.add_argument('-u', '--id', '--njuid', '--username', default=None, type=str, help='NJUID', metavar='NJUID', dest='username')
    parser.add_argument('-i', '--stdin', action='store_true', help='read password from stdin instead of tty (for script usage only)')
    parser.add_argument('--tstp', action='store_true', help='send SIGTSTP to itself after the first login (used with bg to run in the background)')
    parser.add_argument('--logpath', default=None, type=str, help='the log file to be written after resuming from SIGTSTP')
    parser.add_argument('--duration', default=-1., type=float, help='the number of hours to stay logged in')
    parser.add_argument('--retry-interval', default=1., type=float, help='the number of hours between retries')
    parser.add_argument('--check-interval', default=6., type=float, help='the number of hours between login status checks')
    parser.add_argument('-v', '--version', action='version', version='version 0.1.0\nby Ren-Jian Wang')
    args = parser.parse_args()
    client = NJUInternet(args.username, args.stdin, args.logpath)
    if args.cmd == 'login':
        ret = client.login()
    elif args.cmd == 'logout':
        ret = client.logout()
    elif args.cmd == 'keep':
        ret = client.keep(args.tstp, args.duration, args.retry_interval, args.check_interval)
    else:
        raise NotImplementedError
    if not ret:
        sys.exit(3)


if __name__ == '__main__':
    main()
