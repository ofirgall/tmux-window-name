#!/usr/bin/env python3

import subprocess
from typing import Any, List, Mapping, NamedTuple, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass

import libtmux

@dataclass
class DisplayedPath:
    extra: Any
    full: Path
    display: Path

@dataclass
class Pane:
    info: Mapping[str, Any]
    program: Optional[str]

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

def is_program_with_dir(program_line: str) -> Tuple[bool, str]:
    program = program_line.split()

    for p in PROGRAMS_WITH_DIR:
        if p in program[0]:
            program[0] = p
            return True, ' '.join(program)

    return False, ''

def get_session_active_panes(session: libtmux.Session) -> List[Mapping[str, Any]]:
    all_panes = session.server._list_panes()
    session_windows = session._list_windows()
    session_windows_ids = [window['window_id'] for window in session_windows]

    return [p for p in all_panes if p['pane_active'] == '1' and p['window_id'] in session_windows_ids]

def rename_window(server: libtmux.Server, window_id: str, window_name: str):
    server.cmd('rename-window', '-t', window_id, window_name[:MAX_WINDOW_NAME_LEN])

def get_uncommon_path(a: Path, b: Path) -> Tuple[Path, Path]:
    for x in range(-1, -max(len(a.parts), len(b.parts)) - 1, -1):
        try:
            if a.parts[x] != b.parts[x]:
                break
        except IndexError:
            break

    return Path(*a.parts[x:]), Path(*b.parts[x:])

def get_exclusive_paths(panes: List[Pane]) -> List[Tuple[Pane, Path]]:
    # Start all displays as the last dir (.name)
    exc_paths = [DisplayedPath(pane, Path(pane.info['pane_current_path']), Path(Path(pane.info['pane_current_path']).name)) for pane in panes]

    # TODO: issue:
    # a/b - a/b
    # a/b - b (need to bo a/b too)
    # c/b - c/b
    for x in range(len(exc_paths)):
        for y in range(len(exc_paths)):
            if x == y:
                continue
            # If same display find new display
            if exc_paths[x].display == exc_paths[y].display and \
                    panes[x].program == panes[y].program and \
                    exc_paths[x].full != exc_paths[y].full:
                exc_paths[x].display, exc_paths[y].display = get_uncommon_path(exc_paths[x].full, exc_paths[y].full)

    return [(p.extra, p.display) for p in exc_paths]

def rename_windows(server: libtmux.Server):
    current_session = get_current_session(server)
    session_active_panes = get_session_active_panes(current_session)

    panes_programs = [Pane(p, get_current_program(p['pane_pid'])) for p in session_active_panes]
    panes_with_programs = [p for p in panes_programs if p.program is not None]
    panes_with_dir = [p for p in panes_programs if p.program is None]

    for pane in panes_with_programs:
        is_with_dir, program_name = is_program_with_dir(pane.program)
        if is_with_dir:
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
