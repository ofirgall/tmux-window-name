#!/usr/bin/env python3

import sys

sys.path.append('scripts/')

from rename_session_windows import apply_prefix, extract_prefix, should_enable_dynamic


def test_extract_prefix():
    assert extract_prefix("foo|bar") == "foo|"
    assert extract_prefix("a|b|c") == "a|"
    assert extract_prefix("|foo") == "|"
    assert extract_prefix("STATIC") == "STATIC"
    assert extract_prefix("") == ""


def test_apply_prefix():
    assert apply_prefix("work|", "vim") == "work|vim"
    assert apply_prefix("|", "foo") == "|foo"
    assert apply_prefix("STATIC", "vim") == "STATIC"
    assert apply_prefix("", "vim") == "vim"


def test_should_enable_dynamic():
    assert should_enable_dynamic("work|") == True
    assert should_enable_dynamic("") == True
    assert should_enable_dynamic("STATIC") == False
