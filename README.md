# Better Window names for tmux

TODO: complete
Plugin that let you have a browser session that is attached to the tmux sessions.

TODO: complete
![Tmux Browser Demo GIF](screenshots/demo.gif)

## Dependencies
TODO: complete

* Python3.X
* libtmux

## Usage

TODO: complete

## Installation

### Installation with [Tmux Plugin Manager](https://github.com/tmux-plugins/tpm) (recommended)

Add plugin to the list of TPM plugins:

```tmux.conf
set -g @plugin 'ofirgall/tmux-window-name'
```

Press prefix + I to install it.

### Manual Installation

Clone the repo:

```bash
$ git clone https://github.com/ofirgall/tmux-window-name.git ~/clone/path
```

Add this line to your .tmux.conf:

```tmux.conf
run-shell ~/clone/path/tmux-window-name.tmux
```

Reload TMUX environment with:

```bash
$ tmux source-file ~/.tmux.conf
```

## Configuration Options

TODO: complete
### `@new_browser_window`

The command to run a new window.
E.g: `firefox --new-window url`

```tmux.conf
set -g @new_browser_window 'firefox --new-window'
```

---

## License

[MIT](LICENSE)
