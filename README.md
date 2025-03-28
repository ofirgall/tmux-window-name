# Better Window Names for tmux

A plugin to name your tmux windows smartly, like IDE's.

![Tmux Window Name Screenshot](screenshots/example.png)

## Index
* [Use case](#use-case)
* [Usage](#usage)
* [How it works](#how-it-works)
* [Installation](#installation)
* [Configuration Options](#configuration-options)

## Dependencies

* tmux (Tested on 3.0a)
* Python 3.6.8+ (Maybe can be lower, tested on 3.6.8)
* pip
* [libtmux](https://github.com/tmux-python/libtmux) >0.16

## Use case

If you are using tmux as your main multiplexer you probably found yourself with 5+ windows per session with indexed names but no information about whats going on in the windows.

You tried to configure `automatic-rename` and `automatic-rename-format` but you found yourself pretty limited.

This plugin comes to solve those issues to name your windows inspired by IDE tablines.\
It makes sure to show you the shortest path possible!

#### Examples
This session:
```
1. ~/workspace/my_project
2. ~/workspace/my_project/tests/
3. ~/workspace/my_other_project
4. ~/workspace/my_other_project/tests
```
Will display:
```
1. my_project
2. my_project/tests
3. my_other_project
4. my_other_project/tests
```

---

It knows which programs runs
```
1. ~/workspace/my_project (with nvim)
2. ~/workspace/my_project
3. ~/workspace/my_other_project (with git diff)
4. ~/workspace/my_other_project
```
Will display:
```
1. nvim:my_project
2. my_project
3. git diff:my_other_project
4. my_other_project
```

For more scenarios you check out the [tests](tests/test_exclusive_paths.py).

## Usage
[Install](#installation) the plugin and let it name your windows :)

_**Note**_: if you are using [tmux-resurrect](https://github.com/tmux-plugins/tmux-resurrect) `tmux-window-name` must be loaded before `tmux-resurrect`

You can `tmux rename-window` manually to set your own window names, to re-enable automatic renames set run `tmux rename-window ""`

Make sure your configuration/other plugins doesn't turn on `automatic-rename` and doesn't rename your windows.

### Automatic rename after launching neovim
By default `tmux-window-name` hooks `after-select-window` which trigged when switching windows.

You can add autocmd to rename after nvim launches and stops as so:
```lua
local uv = vim.uv

vim.api.nvim_create_autocmd({ 'VimEnter', 'VimLeave' }, {
	callback = function()
		if vim.env.TMUX_PLUGIN_MANAGER_PATH then
			uv.spawn(vim.env.TMUX_PLUGIN_MANAGER_PATH .. '/tmux-window-name/scripts/rename_session_windows.py', {})
		end
	end,
})
```

### Automatic rename after changing dir
By default `tmux-window-name` hooks `after-select-window` which trigged when switching windows, you can add hook in your `.shellrc` to execute `tmux-window-name`
##### .zshrc
```bash
tmux-window-name() {
	($TMUX_PLUGIN_MANAGER_PATH/tmux-window-name/scripts/rename_session_windows.py &)
}

add-zsh-hook chpwd tmux-window-name
```

#### Hooks Used
Make sure the hooks that used aren't overridden.
* @resurrect-hook-pre-restore-all
* @resurrect-hook-post-restore-all

---

## How it works
Each time you unfocus from a pane, the plugin looks for every active pane in your session windows.

_**Note**_: if you have a better hook in mind make sure to notify me!

1. If shell is running, it shows the current dir as short as possible, `long_dir/a` -> `a`, it avoids [intersections](#Intersections) too!
1. If "regular" program is running it shows the program with the args, `less ~/my_file` -> `less ~/my_file`.
1. If "special" program is running it shows the program with the dir attached, `git diff` (in `long_dir/a`) -> `git diff:a`, it avoids [intersections](#Intersections) too!

### Intersections

To make the shortest path as possible the plugin finds the shortest not common path if your windows.

--- 

## Installation

### Install libtmux (must)
_**Note**_: Make sure you are using the `user` python and not `sudo` python or `virutalenv` python!

```sh
python3 -m pip install --user libtmux
```

### Install dataclasses (for Python 3.6.X only)
```sh
python3 -m pip install dataclasses --user
```

### Installation with [Tmux Plugin Manager](https://github.com/tmux-plugins/tpm) (recommended)

Add plugin to the list of TPM plugins:

```tmux.conf
set -g @plugin 'ofirgall/tmux-window-name'
```

_**Note**_: set `tmux-window-name` before `tmux-resurrect` (if you are using `tmux-resurrect`)

```tmux.conf
set -g @plugin 'ofirgall/tmux-window-name'
set -g @plugin 'tmux-plugins/tmux-resurrect'
```

Press prefix + I to install it.

### Manual Installation

Clone the repo:

```bash
$ git clone https://github.com/ofirgall/tmux-window-name.git ~/clone/path
```

Add this line to your .tmux.conf:

```tmux.conf
run-shell ~/clone/path/tmux_window_name.tmux
```

Reload TMUX environment with:

```bash
$ tmux source-file ~/.tmux.conf
```

## Configuration Options
_**Note**_: All options are evaluated with [eval](https://docs.python.org/3/library/functions.html#eval) be careful!

### `@tmux_window_name_shells`

Shell programs, will show dir instead of the program

```tmux.conf
set -g @tmux_window_name_shells "['bash', 'fish', 'sh', 'zsh']"
```

### `@tmux_window_name_dir_programs`

Programs that will show the dir name too.

E.g: `git diff` running in `long_dir/my_repo` will show `git diff:my_repo`

```tmux.conf
set -g @tmux_window_dir_programs "['nvim', 'vim', 'vi', 'git']"
```

### `@tmux_window_name_ignored_programs`

Programs that will be skipped/ignored when looking for active program.

```tmux.conf
set -g @tmux_window_name_ignored_programs "['sqlite3']" # Default is []
```

### `@tmux_window_name_max_name_len`

Maximum name length of a window

```tmux.conf
set -g @tmux_window_name_max_name_len "20"
```

### `@tmux_window_name_use_tilde`

Replace `$HOME` with `~` in window names

```tmux.conf
set -g @tmux_window_name_use_tilde "False"
```

### `@tmux_window_name_show_program_args`

Show arguments that the program has been ran with.

```tmux.conf
set -g @tmux_window_name_show_program_args "True"
```

### `@tmux_window_name_substitute_sets`

Replace program command lines with [re.sub](https://docs.python.org/3/library/re.html#re.sub). \
The options expect list of tuples with 2 elements, `pattern` and `repl`. \
E.g: The example below will replace `/usr/bin/python3 /usr/bin/ipython3` with `ipython3`, and the same for ipython2

Note: use `~/.tmux/plugins/tmux-window-name/scripts/rename_session_windows.py --print_programs` to see the full program command line and the results of the substitute.

```tmux.conf
set -g @tmux_window_name_substitute_sets "[('.+ipython2', 'ipython2'), ('.+ipython3', 'ipython3')]"

# Same example but with regex groups
set -g @tmux_window_name_substitute_sets "[('.+ipython([32])', 'ipython\g<1>')]"

# Default Value:
set -g @tmux_window_name_substitute_sets "[('.+ipython([32])', 'ipython\g<1>'), ('^(/usr)?/bin/(.+)', '\g<2>'), ('(bash) (.+)/(.+[ $])(.+)', '\g<3>\g<4>'), ('.+poetry shell', 'poetry')]"
	# 0: from example
	# 1: removing `/usr/bin` and `/bin` prefixes of files
	# 2: removing `bash /long/path/for/bashscript`
	# 3: changing "poetry shell" to "poetry"
```

### `@tmux_window_name_dir_substitute_sets`

Replace dir lines with [re.sub](https://docs.python.org/3/library/re.html#re.sub). \
The options expect list of tuples with 2 elements, `pattern` and `repl` as above. 
E.g: The example below will replace `tmux-resurrect` with `resurrect`

```tmux.conf
set -g @tmux_window_name_dir_substitute_sets "[('tmux-(.+)', '\\g<1>')]"

# Default Value:
set -g @tmux_window_name_dir_substitute_sets "[]"
```

### `@tmux_window_name_icon_style`

Configure how icons are displayed in window names. \
Available styles:
- `name`: Show only program name (default)
- `icon`: Show only icon
- `name_and_icon`: Show both icon and program name

```tmux.conf
# Show only icons
set -g @tmux_window_name_icon_style "'icon'"

# Show icons with program names
set -g @tmux_window_name_icon_style "'name_and_icon'"

# Default Value:
set -g @tmux_window_name_icon_style "'name'"
```

### `@tmux_window_name_custom_icons`

Customize icons for specific programs. \
The value should be a dictionary mapping program names to their icons.

```tmux.conf
# Custom icons example
set -g @tmux_window_name_custom_icons '{"python": "🐍", "custom_app": "📦"}'

# Default Value:
set -g @tmux_window_name_custom_icons '{}'
```

_**Note**_: Icons can be any Unicode characters, including emoji or Nerd Font icons. \
If using Nerd Font icons, make sure your terminal supports them.

---

## Debug Configuration Options

### `@tmux_window_name_log_level`

Set log level of the script. \
Logs output go to `/tmp/tmux-window-name.log`

```tmux.conf
# Enable debug logs
set -g @tmux_window_name_log_level "'DEBUG'"

# Default Value:
set -g @tmux_window_name_log_level "'WARNING'"
```

---

# Development
Run `ruff format` before applying PR

# Testing
Run `pytest` at the root dir

---

## License

[MIT](LICENSE)
