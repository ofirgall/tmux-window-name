#!/usr/bin/env python3

# I hate this but i don't want to make it a pip package, its a script.
import sys
import pytest
from typing import List, Optional, Tuple
from dataclasses import dataclass

sys.path.append('scripts/')

from path_utils import get_exclusive_paths, Pane


pytestmark = pytest.mark.parametrize("ignore_program_diffs", [True, False])

@dataclass
class FakePane:
    pane_current_path: str | None


def _fake_pane(path: str, program: Optional[str]):
    return Pane(FakePane(path), program)


def _check(expected: List[Tuple[str, Optional[str], str]], ignore_program_diffs: bool):
    """check expected displayed paths

    Args:
        expected (List[Tuple[str, Optional[str], str]]): list of (full_path, program, expected_display)
        ignore_program_diffs (bool): ignore_program_diffs flag value to pass along to get_exclusive_paths
    E.g:
        _check([
            ('a/dir', 'p1', 'dir'), # Program p1 in a/dir will display dir (will be formated to p1:dir)
            ('b/dir', None, 'b/dir'), # Shell in b/dir will display b/dir
            ('c/dir', None', 'c/dir'), # Shell in c/dir will display c/dir
        ], False)
    """
    panes = [_fake_pane(full, program) for full, program, _ in expected]
    exclusive_panes = get_exclusive_paths(panes, ignore_program_diffs)
    for (full, _, expected_display), (_, display) in zip(expected, exclusive_panes):
        assert str(display) == expected_display


def test_not_intersect(ignore_program_diffs: bool):
    _check(
        [
            ('a/a_dir', None, 'a_dir'),
            ('b/b_dir', None, 'b_dir'),
        ],
        ignore_program_diffs
    )

    _check(
        [
            ('a', None, 'a'),
            ('b', None, 'b'),
        ],
        ignore_program_diffs
    )

    _check(
        [
            ('a', None, 'a'),
            ('b', None, 'b'),
            ('c', None, 'c'),
        ],
        ignore_program_diffs
    )


def test_basic_intersect(ignore_program_diffs: bool):
    _check(
        [
            ('a/dir', None, 'a/dir'),
            ('b/dir', None, 'b/dir'),
        ],
        ignore_program_diffs
    )


def test_not_same_length(ignore_program_diffs: bool):
    _check(
        [
            ('a/b/dir', None, 'a/b/dir'),
            ('b/dir', None, 'b/dir'),
        ],
        ignore_program_diffs
    )


def test_reacurring_dir(ignore_program_diffs: bool):
    _check(
        [
            ('a/dir', None, 'a/dir'),
            ('b/dir', None, 'b/dir'),
            ('c/dir', None, 'c/dir'),
        ],
        ignore_program_diffs
    )


def test_same_path_twice_dir(ignore_program_diffs: bool):
    _check(
        [
            ('a/dir', None, 'a/dir'),
            ('a/dir', None, 'a/dir'),
            ('b/dir', None, 'b/dir'),
        ],
        ignore_program_diffs
    )

    _check(
        [
            ('a/dir', None, 'a/dir'),
            ('b/dir', None, 'b/dir'),
            ('a/dir', None, 'a/dir'),
        ],
        ignore_program_diffs
    )

    _check(
        [
            ('a/dir', None, 'a/dir'),
            ('b/dir', None, 'b/dir'),
            ('b/dir', None, 'b/dir'),
            ('a/dir', None, 'a/dir'),
        ],
        ignore_program_diffs
    )

    _check(
        [
            ('a/dir', None, 'a/dir'),
            ('b/dir', None, 'b/dir'),
            ('a/dir', None, 'a/dir'),
            ('b/dir', None, 'b/dir'),
        ],
        ignore_program_diffs
    )

    _check(
        [
            ('a/dir', None, 'a/dir'),
            ('b/dir', None, 'b/dir'),
            ('c/dir', None, 'c/dir'),
            ('a/dir', None, 'a/dir'),
            ('b/dir', None, 'b/dir'),
            ('c/dir', None, 'c/dir'),
        ],
        ignore_program_diffs
    )


def test_mixed_basic(ignore_program_diffs: bool):
    _check(
        [
            ('a/dir', None, 'a/dir'),
            ('b/dir', None, 'b/dir'),
            ('c/c_dir', None, 'c_dir'),
        ],
        ignore_program_diffs
    )

    _check(
        [
            ('a/b/c/d', None, 'a/b/c/d'),
            ('b/c/d', None, 'b/c/d'),
            ('dirrr', None, 'dirrr'),
        ],
        ignore_program_diffs
    )


def test_program_basic(ignore_program_diffs: bool):
    _check(
        [
            ('a/dir', 'p1', 'a/dir' if ignore_program_diffs else 'dir'),
            ('b/dir', None, 'b/dir' if ignore_program_diffs else 'dir'),
        ],
        ignore_program_diffs
    )

    _check(
        [
            ('a/dir', 'p1', 'a/dir' if ignore_program_diffs else 'dir'),
            ('b/dir', 'p2', 'b/dir' if ignore_program_diffs else 'dir'),
        ],
        ignore_program_diffs
    )

    _check(
        [
            ('a/dir', 'p1', 'a/dir'),
            ('b/dir', 'p1', 'b/dir'),
        ],
        ignore_program_diffs
    )

    _check(
        [
            ('a/dir', 'p1', 'a/dir' if ignore_program_diffs else 'dir'),
            ('b/dir', 'p2', 'b/dir' if ignore_program_diffs else 'dir'),
        ],
        ignore_program_diffs
    )


def test_program_mixed(ignore_program_diffs: bool):
    _check(
        [
            ('a/dir', 'p1', 'a/dir' if ignore_program_diffs else 'dir'),
            ('b/dir', None, 'b/dir' if ignore_program_diffs else 'dir'),
            ('c/dir', 'p2', 'c/dir' if ignore_program_diffs else 'dir'),
        ],
        ignore_program_diffs
    )

    _check(
        [
            ('a/dir', 'p1', 'a/dir' if ignore_program_diffs else 'dir'),
            ('b/dir', None, 'b/dir' if ignore_program_diffs else 'dir'),
            ('a/dir', 'p1', 'a/dir' if ignore_program_diffs else 'dir'),
            ('c/dir', 'p2', 'c/dir' if ignore_program_diffs else 'dir'),
        ],
        ignore_program_diffs
    )

    _check(
        [
            ('a/dir', 'p1', 'a/dir'),
            ('b/dir', 'p1', 'b/dir'),
            ('a/dir', 'p1', 'a/dir'),
            ('c/dir', 'p2', 'c/dir' if ignore_program_diffs else 'dir'),
        ],
        ignore_program_diffs
    )
