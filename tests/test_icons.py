#!/usr/bin/env python3

import sys
from dataclasses import dataclass
from typing import Optional
from unittest.mock import Mock, patch, call

sys.path.append('scripts/')

from rename_session_windows import Options, get_program_icon, rename_window, PROGRAM_ICONS


@dataclass
class FakeServer:
    def __init__(self):
        self.cmd = Mock()
        self.cmd.return_value = self


def test_get_program_icon_built_in():
    """Test retrieving built-in program icons"""
    options = Options()
    assert get_program_icon('nvim', options) == PROGRAM_ICONS['nvim']  # vim icon
    assert get_program_icon('python', options) == PROGRAM_ICONS['python']  # python icon
    assert get_program_icon('nonexistent', options) == ''  # no icon


def test_get_program_icon_custom():
    """Test custom program icons override built-in ones"""
    options = Options(
        custom_icons={
            'custom_app': '󰀄',
            'nvim': '󰹻',  # override default vim icon
        }
    )
    assert get_program_icon('custom_app', options) == '󰀄'
    assert get_program_icon('nvim', options) == '󰹻'  # should use custom icon
    assert get_program_icon('python', options) == PROGRAM_ICONS['python']  # should use built-in icon


def test_get_program_icon_with_path():
    """Test that program icons work with full paths"""
    options = Options()
    assert get_program_icon('/usr/bin/python', options) == PROGRAM_ICONS['python']
    assert get_program_icon('/custom/path/nvim', options) == PROGRAM_ICONS['nvim']


def test_get_program_icon_with_args():
    """Test that program icons work with command arguments"""
    options = Options()
    assert get_program_icon('python script.py --arg', options) == PROGRAM_ICONS['python']
    assert get_program_icon('nvim file.txt', options) == PROGRAM_ICONS['nvim']


def test_rename_window_name_style():
    """Test window renaming with 'name' style (default)"""
    server = FakeServer()
    options = Options(icon_style='name')
    rename_window(server, '1', 'python', 20, options)
    expected_calls = [
        call('rename-window', '-t', '1', 'python'),
        call('set-option', '-wq', '-t', '1', 'automatic-rename-format', 'python'),
        call('set-option', '-wq', '-t', '1', 'automatic-rename', 'on'),
    ]
    assert server.cmd.call_args_list == expected_calls


def test_rename_window_icon_style():
    """Test window renaming with 'icon' style"""
    server = FakeServer()
    options = Options(icon_style='icon')
    rename_window(server, '1', 'python', 20, options)
    expected_calls = [
        call('rename-window', '-t', '1', PROGRAM_ICONS['python']),
        call('set-option', '-wq', '-t', '1', 'automatic-rename-format', PROGRAM_ICONS['python']),
        call('set-option', '-wq', '-t', '1', 'automatic-rename', 'on'),
    ]
    assert server.cmd.call_args_list == expected_calls


def test_rename_window_name_plus_icon_style():
    """Test window renaming with 'name+icon' style"""
    server = FakeServer()
    options = Options(icon_style='name+icon')
    rename_window(server, '1', 'python', 20, options)
    expected_calls = [
        call('rename-window', '-t', '1', f'{PROGRAM_ICONS["python"]} python'),
        call('set-option', '-wq', '-t', '1', 'automatic-rename-format', f'{PROGRAM_ICONS["python"]} python'),
        call('set-option', '-wq', '-t', '1', 'automatic-rename', 'on'),
    ]
    assert server.cmd.call_args_list == expected_calls


def test_rename_window_custom_icon():
    """Test window renaming with custom icon"""
    server = FakeServer()
    options = Options(icon_style='name+icon', custom_icons={'python': '🐍'})
    rename_window(server, '1', 'python', 20, options)
    expected_calls = [
        call('rename-window', '-t', '1', '🐍 python'),
        call('set-option', '-wq', '-t', '1', 'automatic-rename-format', '🐍 python'),
        call('set-option', '-wq', '-t', '1', 'automatic-rename', 'on'),
    ]
    assert server.cmd.call_args_list == expected_calls


def test_rename_window_max_length():
    """Test that window names respect max_name_len"""
    server = FakeServer()
    options = Options(icon_style='name+icon', max_name_len=10)
    rename_window(server, '1', 'python', 10, options)
    expected_calls = [
        call('rename-window', '-t', '1', f'{PROGRAM_ICONS["python"]} python'),
        call('set-option', '-wq', '-t', '1', 'automatic-rename-format', f'{PROGRAM_ICONS["python"]} python'),
        call('set-option', '-wq', '-t', '1', 'automatic-rename', 'on'),
    ]
    assert server.cmd.call_args_list == expected_calls


def test_get_program_icon_with_colon():
    """Test that program icons work with program names containing colons"""
    options = Options()
    assert get_program_icon('python:3.9', options) == PROGRAM_ICONS['python']
    assert get_program_icon('nvim:q', options) == PROGRAM_ICONS['nvim']


def test_custom_icons_json_parsing():
    """Test that custom icons can be parsed from JSON string"""
    server = FakeServer()
    server.cmd.return_value.stdout = ['{"python": "🐍", "custom": "📦"}']
    options = Options.from_options(server)
    assert get_program_icon('python', options) == '🐍'
    assert get_program_icon('custom', options) == '📦'


def test_invalid_custom_icons_json():
    """Test handling of invalid JSON for custom icons"""
    server = FakeServer()

    # Use simple approach that doesn't require complicated patching
    def custom_cmd(*args):
        result = Mock()
        option = args[2] if len(args) > 2 else ''

        if option.endswith('custom_icons'):
            result.stdout = ['{invalid json']  # Invalid JSON
        else:
            result.stdout = []  # Empty for all other options, will use defaults
        return result

    server.cmd.side_effect = custom_cmd

    # Create options with default values except for custom_icons
    options = Options.from_options(server)

    # Should fall back to default (empty dict)
    assert options.custom_icons == {}
