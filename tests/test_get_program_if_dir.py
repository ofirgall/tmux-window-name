#!/usr/bin/env python3

import sys

sys.path.append('scripts/')

from rename_session_windows import get_program_if_dir


def test_exact_match():
    assert get_program_if_dir('nvim', ['nvim', 'vim']) == 'nvim'


def test_exact_match_with_args():
    assert get_program_if_dir('git diff', ['git', 'nvim']) == 'git diff'


def test_no_match():
    assert get_program_if_dir('htop', ['nvim', 'git']) is None


def test_no_match_empty_dir_programs():
    assert get_program_if_dir('nvim', []) is None


def test_interpreter_launched_exact_arg():
    assert get_program_if_dir('/usr/bin/node /usr/bin/lazygit', ['lazygit']) == 'lazygit'


def test_interpreter_launched_path_arg():
    assert get_program_if_dir('/home/user/.asdf/shims/node /home/user/.bun/bin/some-cli', ['some-cli']) == 'some-cli'


def test_interpreter_launched_no_match():
    assert get_program_if_dir('/usr/bin/node /usr/bin/something', ['lazygit']) is None
