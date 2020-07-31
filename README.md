# timew-sync

Sync your time tracked with [`timew`](https://timewarrior.net/) to a JIRA
instance. This works by inspecting the tags of your `timew` intervals to
extract possible JIRA-IDs from it.

## Installation

```
git close https://github.com/lummax/timew-sync.git
cd timew-sync/
pip install --user .
ln -s ~/.local/bin/timew-sync ~/.timewarrior/extensions/sync.py
```

## Configuration

To make this work, please create a `~/.timewarrior/timew-sync.toml`:

```
[Jira]
url = "XXX"
username = "XXX"
password = "XXX"
pattern = "(\\w+-\\d+)"
```

The `pattern` is a Python regex that is matched against every tag of the
`timew` intervals. It must contain at least one group.

When experiencing `toml.decoder.TomlDecodeError: Reserved escape sequence used` make sure to escape backslashes.

## Using

Run `timew sync :day` to sync your intervals to JIRA.
