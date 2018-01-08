#!/usr/bin/python

"""
Mohammad Fatemipopur
m.fatemipour@gmail.com
watchall is a tool same is linux watch with scrolling capability.
"""

import curses

import sys
import tty
import time
import argparse
import subprocess
from threading import Thread
import difflib
import signal

try: # Python 2
    import Queue
except ImportError: # Python 3
    import queue as Queue


# https://stackoverflow.com/questions/510357/python-read-a-single-character-from-the-user

class _Getch(object):
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self, reset=False):
        return self.impl(reset)

class _GetchUnix(object):
    sane = None
    def __init__(self):
        import tty, sys

    def __call__(self, reset):
        import sys, tty, termios
        ch = None
        try:
            fd = sys.stdin.fileno()
            if not reset:
                self.sane = termios.tcgetattr(fd)
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
        finally:
            if not self.sane:
                try:
                    self.sane = termios.tcgetattr(fd)
                except:
                    return ch
            termios.tcsetattr(fd, termios.TCSADRAIN, self.sane)
        return ch

class _GetchWindows(object):
    def __init__(self):
        import msvcrt

    def __call__(self, reset):
        import msvcrt
        return msvcrt.getch()

getch = _Getch()

#https://stackoverflow.com/questions/774316/python-difflib-highlighting-differences-inline
def color_diff(seqm):
    # https://gist.github.com/chrisopedia/8754917
    fmt_color = "\033[{}m{}\033[0m".format
    GREEN, YELLO = 92,93
    for opcode, a0, a1, b0, b1 in seqm.get_opcodes():
        if opcode == 'equal':
            yield seqm.b[b0:b1]
        elif opcode == 'insert':
            yield fmt_color(GREEN, seqm.b[b0:b1])
        elif opcode == 'replace':
            yield fmt_color(YELLO, seqm.b[b0:b1])
        elif opcode == 'delete':
            continue

# https://github.com/mfs-git/watchall/blob/master/watchall
class Watchall(object):

    def __init__(self, args):
        # Handle keyboard interrupt
        signal.signal(signal.SIGINT, self.stop)
        # Prepare internal state
        self.differences = args.differences
        self.interval = args.interval
        self.header = args.header
        self.cmd = args.command
        # Check for input
        self.key_q = Queue.Queue()
        key_thread = Thread(**{
            'target': self.run_scroll,
        })
        key_thread.daemon = True
        key_thread.start()
        # Check for output
        self.cmd_q = Queue.Queue()
        cmd_thread = Thread(**{
            'target': self.run_cmd,
        })
        cmd_thread.daemon = True
        cmd_thread.start()

    def stop(self, *_):
        getch(True)   
        self.key_q.put(None)
        sys.stdout.write('\r\n')

    def run_scroll(self):
        ESC = chr(27)
        while True:
            for key in iter(getch, ESC):
                if key == 'q':
                    self.key_q.put(None)
            key_1 = getch()
            # ANSI escape codes
            if '[' != key_1:
                continue
            key_2 = getch()
            # Arrow keys
            delta = {
                'A': -1,
                'B': +1,
            }.get(key_2, 0)
            # Scroll the screen
            if delta:
                self.key_q.put(delta)

    def get_scroll(self, _t=0):
        debounce = 0
        while True:
            try:
                delta = self.key_q.get(timeout=_t)
                if delta is None:
                    return None
                debounce += delta
            except Queue.Empty:
                return debounce
    
    def get_output(self, _t=0):
        try:
            return self.cmd_q.get(timeout=_t)
        except Queue.Empty:
            return None

    def crop_view(self, _view, _delta):
        empty = abs(_delta)*['']
        # Crop current for comparison
        if _delta > 0:
            return empty + _view[_delta:]
        if _delta < 0:
            return _view[:_delta] + empty
        return _view

    def run_update(self):
        cur_view = []
        is_scroll = True
        header = self.header
        color = self.differences
        timeout = min(0.01, self.interval)
        height = self.get_term_y()
        y_stop = height
        y_start = 0
        delta = 0
        msg = ''
        # Get first command result
        cur_lines = None
        while cur_lines is None:
            cur_lines = self.get_output(timeout)
        # Continue to update command
        while True:
            # Check new command output
            new_lines = self.get_output()
            if new_lines is not None:
                cur_lines = new_lines
            y_max = len(cur_lines)
            pre_view = self.crop_view(cur_view, delta)
            cur_view = cur_lines[y_start:y_stop]
            # Only update if the view changed
            if is_scroll or pre_view != cur_view:
                msg = self.get_msg(y_start, y_max, header)
                self.show_text(pre_view, cur_view, height, msg, color)
            pre_time = time.time()
            end_time = time.time() + self.interval
            # Wait until key or interval
            for cur_time in iter(time.time, 0):
                # Resume if process interrupted
                if cur_time - pre_time > 2*timeout:
                    self.show_text([], cur_view, height, msg, True)
                pre_time = cur_time
                # Resume if past interval
                if cur_time > end_time:
                    break
                # Wait for keyboard events
                delta = self.get_scroll(timeout)
                if delta is None:
                    return
                if delta is not 0:
                    break
            # Recalculate start, stop, and height
            y_range = (0, y_start + delta, y_max)
            height = self.get_term_y()
            new_start = sorted(y_range)[1]
            new_stop = new_start + height
            # Is new if view changed
            if (new_start, new_stop) == (y_start, y_stop):
                is_scroll = False
                delta = 0
                continue
            y_start = new_start
            y_stop = new_stop
            is_scroll = True

    def execute_cmd(self):
        process_keys = {
            'stdout': subprocess.PIPE,
            'stderr': subprocess.STDOUT,
            'universal_newlines': True,
        }
        try:
            process = subprocess.Popen(self.cmd, **process_keys)
        except:
            self.stop()
            raise

        output, stderr = process.communicate()
        retcode = process.poll()
        if retcode:
            msg = 'ERR {}:\n {}'.format(retcode, stderr)
            return msg.splitlines()

        return output.splitlines()

    def run_cmd(self):
        while True:
            if not self.cmd_q.empty():
                continue
            self.cmd_q.put(self.execute_cmd())

    def get_term_y(self):
        # We could try this for cross-platform support:
        # https://gist.github.com/jtriley/1108174
        w = curses.initscr()
        y, x = w.getmaxyx()
        curses.endwin()
        return y

    def get_msg(self, y_start, y_max, header=True):
        if not header:
            return []
        cmd_state = self.interval, ' '.join(self.cmd)
        status_msg = "Every {2}s: {3}, first line: {0}/{1}"
        return [status_msg.format(y_start, y_max, *cmd_state)]

    def get_text(self, view, height, msg_len=0):
        # Add empty lines
        n_empty = height - len(view)
        if n_empty > 0:
            view += ['']*n_empty
 
        return '\r\n'.join(view[:-msg_len])

    def show_text(self, pre_view, cur_view, height=0, msg='', color=False):
        # Write status
        if len(msg):
            msg_text = '\r\n'.join(['']+msg+[''])
            sys.stdout.write(msg_text)

        # Color changes
        pre_text = self.get_text(pre_view, height, len(msg))
        cur_text = self.get_text(cur_view, height, len(msg))
        text = cur_text
        if color:
            diff = difflib.SequenceMatcher(None, pre_text, cur_text)
            text = ''.join(color_diff(diff))

        sys.stdout.write(text)
        sys.stdout.flush()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-n', '--interval', **{
        'help': 'seconds to wait between updates',
        'type': float,
        'default': 2.0,
    })
    parser.add_argument('-d', '--differences', **{
        'help': 'highlight changes between updates',
        'action': 'store_true',
    })
    parser.add_argument('-t', '--no-title', **{
        'help': 'turns off showing the header',
        'action': 'store_false',
        'dest': 'header',
    })
    parser.add_argument('command', **{
        'nargs': argparse.REMAINDER,
        'help': 'command',
    })

    # ------ Global variables -------
    args = parser.parse_args()

    w = Watchall(args)
    w.run_update()
    w.stop()
