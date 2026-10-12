import sys
from unittest.mock import Mock

sys.path.append('scripts/')

import rename_session_windows


def test_disabled_window_recovers_when_automatic_rename_is_on(monkeypatch):
    server = Mock()
    set_window_option = Mock()

    monkeypatch.setattr(rename_session_windows, 'get_window_option', lambda *args: 0)
    monkeypatch.setattr(rename_session_windows, 'get_window_tmux_option', lambda *args: 'on')
    monkeypatch.setattr(rename_session_windows, 'set_window_tmux_option', set_window_option)

    assert rename_session_windows.is_window_rename_enabled(server, '@2') is True
    set_window_option.assert_called_once_with(server, '@2', '@tmux_window_name_enabled', '1')


def test_disabled_window_stays_disabled_when_automatic_rename_is_off(monkeypatch):
    server = Mock()
    set_window_option = Mock()

    monkeypatch.setattr(rename_session_windows, 'get_window_option', lambda *args: 0)
    monkeypatch.setattr(rename_session_windows, 'get_window_tmux_option', lambda *args: 'off')
    monkeypatch.setattr(rename_session_windows, 'set_window_tmux_option', set_window_option)

    assert rename_session_windows.is_window_rename_enabled(server, '@2') is False
    set_window_option.assert_not_called()


def test_rename_hook_only_disables_nonempty_manual_names():
    server = Mock()

    rename_session_windows.enable_user_rename_hook(server)

    hook_command = server.cmd.call_args.args[-1]
    assert '[ #{n:window_name} -gt 0 ] && [ #{automatic-rename} -eq 0 ]' in hook_command
