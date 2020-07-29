import hashlib
import math
import os.path
import pathlib
import re
import sys

import timewreport.parser
import toml
import typing

import timew_sync.jira


def load_config():
    base_dir = pathlib.Path(
        os.environ.get("TIMEWARRIORDB", "~/.timewarrior")
    ).expanduser()
    with open(base_dir / "timew-sync.toml") as fob:
        return toml.load(fob)


def get_worklogs(
    data: timewreport.parser.TimeWarriorParser, pattern
) -> typing.Iterator[timew_sync.jira.Worklog]:
    def get_id(tags):
        for tag in tags:
            match = pattern.match(tag)
            if match:
                return match.group(1)

    def hash_interval(interval: timewreport.parser.TimeWarriorInterval) -> str:
        return hashlib.sha256(
            str(
                (
                    str(interval.get_date()),
                    str(interval.get_start()),
                    str(interval.get_end()),
                    sorted(interval.get_tags()),
                )
            ).encode("utf-8")
        ).hexdigest()

    for interval in data.get_intervals():
        bauhaus_id = get_id(interval.get_tags())
        if not interval.is_open() and bauhaus_id:
            yield timew_sync.jira.Worklog(
                ticket_id=bauhaus_id,
                comment=f"timew-sync: {hash_interval(interval)}",
                timeSpentSeconds=60
                * math.ceil(int(interval.get_duration().total_seconds()) / 60),
            )


def main(data):
    jira_config = load_config().get("Jira", {})
    pattern = re.compile(jira_config["pattern"])

    parsed = timewreport.parser.TimeWarriorParser(data)
    jira = timew_sync.jira.Jira(
        url=jira_config["url"],
        authentication=timew_sync.jira.Authentication(
            (jira_config["username"], jira_config["password"])
        ),
    )

    worklogs = get_worklogs(parsed, pattern)
    jira.sync_worklogs(worklogs)


if __name__ == "__main__":
    main(sys.stdin)
