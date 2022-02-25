#!/usr/bin/env python3

import subprocess
from typing import Any, List, Mapping, Optional, Tuple

import libtmux

from path_utils import get_exclusive_paths, Pane

# TODO: option?
PROGRAMS_WITH_DIR = ['nvim', 'vim', 'vi', 'git']
SHELLS = ['zsh', 'bash', 'sh']
MAX_WINDOW_NAME_LEN = 20

def get_current_program(pid: int) -> Optional[str]:
    try:
        program = subprocess.check_output(['ps', '-f', '--no-headers', '--ppid', str(pid)])
    except subprocess.CalledProcessError:
        return None

    program = program.split()[7:]

    # Ignore shells
    if program[0].decode() in SHELLS:
        return None

    return b' '.join(program).decode()

def get_program_if_dir(program_line: str) -> Optional[str]:
    program = program_line.split()

    for p in PROGRAMS_WITH_DIR:
        if p in program[0]:
            program[0] = p
            return ' '.join(program)

    return None

def get_session_active_panes(session: libtmux.Session) -> List[Mapping[str, Any]]:
    all_panes = session.server._list_panes()
    session_windows = session._list_windows()
    session_windows_ids = [window['window_id'] for window in session_windows]

    return [p for p in all_panes if p['pane_active'] == '1' and p['window_id'] in session_windows_ids]

def rename_window(server: libtmux.Server, window_id: str, window_name: str):
    server.cmd('rename-window', '-t', window_id, window_name[:MAX_WINDOW_NAME_LEN])

def rename_windows(server: libtmux.Server):
    current_session = get_current_session(server)
    session_active_panes = get_session_active_panes(current_session)

    panes_programs = [Pane(p, get_current_program(p['pane_pid'])) for p in session_active_panes]
    panes_with_programs = [p for p in panes_programs if p.program is not None]
    panes_with_dir = [p for p in panes_programs if p.program is None]

    for pane in panes_with_programs:
        program_name = get_program_if_dir(pane.program)
        if program_name is not None:
            pane.program = program_name
            panes_with_dir.append(pane)
            continue

        rename_window(server, pane.info['window_id'], pane.program)

    exclusive_paths = get_exclusive_paths(panes_with_dir)

    for p, display_path in exclusive_paths:
        if p.program is not None:
            # TODO: format from option?
            display_path = f'{p.program}:{display_path}'
        rename_window(server, p.info['window_id'], str(display_path))

def get_current_session(server: libtmux.Server) -> libtmux.Session:
    session_id = server.cmd('display-message', '-p', '#{session_id}').stdout[0]
    return libtmux.Session(server, session_id=session_id)

def main():
    server = libtmux.Server()
    rename_windows(server)

if __name__ == '__main__':
    main()
