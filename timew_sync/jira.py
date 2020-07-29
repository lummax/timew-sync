import argparse
import dataclasses
import getpass
import os.path
import typing

import requests

Authentication = typing.NewType("Authentication", typing.Tuple[str, str])


@dataclasses.dataclass(eq=True, frozen=True)
class Worklog:
    ticket_id: str
    comment: typing.Optional[str]
    timeSpentSeconds: int

    @classmethod
    def from_json(cls, ticket_id: str, data):
        return cls(
            ticket_id=ticket_id,
            comment=data.get("comment") or None,
            timeSpentSeconds=int(data.get("timeSpentSeconds", 0)),
        )

    def to_json(self):
        data = {"timeSpentSeconds": self.timeSpentSeconds}
        if self.comment is not None:
            data["comment"] = self.comment
        return data


class Jira:
    url: str
    session: requests.Session

    def __init__(self, url: str, authentication: Authentication):
        self.url = os.path.join(url, "rest/api/2/")
        self.session = requests.Session()
        self.session.auth = authentication

    def get(self, endpoint: str, **kwargs):
        return self.session.get(os.path.join(self.url, endpoint), **kwargs)

    def post(self, endpoint: str, **kwargs):
        return self.session.post(os.path.join(self.url, endpoint), **kwargs)

    def worklog(self, ticket_id: str) -> typing.Iterator[Worklog]:
        response = self.get(f"issue/{ticket_id}/worklog")
        response.raise_for_status()
        for wl in response.json().get("worklogs"):
            yield Worklog.from_json(ticket_id, wl)

    def add_worklog(self, entry: Worklog):
        resp = self.post(f"issue/{entry.ticket_id}/worklog", json=entry.to_json())
        resp.raise_for_status()

    def sync_worklogs(self, entries: typing.Iterable[Worklog]):
        new_entries = set(entries)
        existing = {wl for new in new_entries for wl in self.worklog(new.ticket_id)}
        for to_add in new_entries - existing:
            print("Adding", to_add)
            self.add_worklog(to_add)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("ticket_id", metavar="ticket-id")
    parser.add_argument("--user", default=getpass.getuser())
    parser.add_argument("--password")
    args = parser.parse_args()
    if args.password is None:
        args.password = getpass.getpass("JIRA password:")
    return args


def main():
    args = parse_args()
    jira = Jira(url=args.url, authentication=Authentication((args.user, args.password)))
    for entry in jira.worklog(ticket_id=args.ticket_id):
        print(entry)


if __name__ == "__main__":
    main()
