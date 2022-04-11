#!/usr/bin/env python3

import subprocess
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Mapping, Optional, Tuple
from argparse import ArgumentParser

import libtmux

from path_utils import get_exclusive_paths, Pane

OPTIONS_PREFIX = '@tmux_window_name_'

HOME_DIR = os.path.expanduser('~')

def get_option(server: libtmux.Server, option: str, default: Any) -> Any:
    out = server.cmd('show-option', '-gv', f'{OPTIONS_PREFIX}{option}').stdout
    if len(out) == 0:
        return default

    return eval(out[0])

@dataclass
class Options:
    shells: List[str] = field(default_factory=lambda: ['zsh', 'bash', 'sh'])
    dir_programs: List[str] = field(default_factory=lambda: ['nvim', 'vim', 'vi', 'git'])
    max_name_len: int = 20
    use_tilde: bool = False
    substitute_sets: List[Tuple] = field(default_factory=lambda: [('.+ipython([32])', r'ipython\g<1>')])

    @staticmethod
    def from_options(server: libtmux.Server):
        fields = Options.__dataclass_fields__

        def default_field_value(f: field):
            if callable(f.default_factory):
                return f.default_factory()
            return f.default

        fields_values = {field.name: get_option(server, field.name, default_field_value(field)) for field in fields.values()}

        return Options(**fields_values)

def parse_shell_command(shell_cmd: List[bytes]) -> Optional[str]:
    # Only shell
    if len(shell_cmd) == 1:
        return None

    shell_cmd_str = [x.decode() for x in shell_cmd]
    # Get base filename
    shell_cmd_str[1] = Path(shell_cmd_str[1]).name
    return ' '.join(shell_cmd_str[1:])

def get_current_program(running_programs: List[bytes], pid: int, shells: List[str]) -> Optional[str]:
    for program in running_programs:
        program = program.split()

        # if pid matches parse program
        if int(program[0]) == pid:
            program = program[1:]
            # Ignore shells
            if program[0].decode() in shells:
                return parse_shell_command(program)

            return b' '.join(program).decode()

    return None


def get_program_if_dir(program_line: str, dir_programs: List[str]) -> Optional[str]:
    program = program_line.split()

    for p in dir_programs:
        if p in program[0]:
            program[0] = p
            return ' '.join(program)

    return None

def get_session_active_panes(session: libtmux.Session) -> List[Mapping[str, Any]]:
    all_panes = session.server._list_panes()
    session_windows = session._list_windows()
    session_windows_ids = [window['window_id'] for window in session_windows]

    return [p for p in all_panes if p['pane_active'] == '1' and p['window_id'] in session_windows_ids]

def rename_window(server: libtmux.Server, window_id: str, window_name: str, max_name_len: int, use_tilde: bool):
    if use_tilde:
        window_name = window_name.replace(HOME_DIR, '~')
    server.cmd('rename-window', '-t', window_id, window_name[:max_name_len])

def get_panes_programs(session: libtmux.Session, options: Options):
    session_active_panes = get_session_active_panes(session)
    running_programs = subprocess.check_output(['ps', '-a', '-oppid,command']).splitlines()[1:]

    return [Pane(p, get_current_program(running_programs, int(p['pane_pid']), options.shells)) for p in session_active_panes]

def rename_windows(server: libtmux.Server):
    current_session = get_current_session(server)
    options = Options.from_options(server)

    panes_programs = get_panes_programs(current_session, options)
    panes_with_programs = [p for p in panes_programs if p.program is not None]
    panes_with_dir = [p for p in panes_programs if p.program is None]

    for pane in panes_with_programs:
        program_name = get_program_if_dir(pane.program, options.dir_programs)
        if program_name is not None:
            pane.program = program_name
            panes_with_dir.append(pane)
            continue

        pane.program = substitute_program_name(pane.program, options.substitute_sets)
        rename_window(server, pane.info['window_id'], pane.program, options.max_name_len, options.use_tilde)

    exclusive_paths = get_exclusive_paths(panes_with_dir)

    for p, display_path in exclusive_paths:
        if p.program is not None:
            p.program = substitute_program_name(p.program, options.substitute_sets)
            display_path = f'{p.program}:{display_path}'

        rename_window(server, p.info['window_id'], str(display_path), options.max_name_len, options.use_tilde)

def get_current_session(server: libtmux.Server) -> libtmux.Session:
    session_id = server.cmd('display-message', '-p', '#{session_id}').stdout[0]
    return libtmux.Session(server, session_id=session_id)

def substitute_program_name(program_line: str, substitute_sets: List[Tuple]) -> str:
    for pattern, replacement in substitute_sets:
        program_line = re.sub(pattern, replacement, program_line)

    return program_line

def print_programs(server: libtmux.Server):
    current_session = get_current_session(server)
    options = Options.from_options(server)

    panes_programs = get_panes_programs(current_session, options)

    for pane in panes_programs:
        if pane.program:
            print(f'{pane.program} -> {substitute_program_name(pane.program, options.substitute_sets)}')

def main():
    server = libtmux.Server()

    parser = ArgumentParser('Renames tmux session windows')
    parser.add_argument('--print_programs', action='store_true', help='Prints full name of the programs in the session')

    args = parser.parse_args()
    if args.print_programs:
        print_programs(server)
    else:
        rename_windows(server)

if __name__ == '__main__':
    main()
