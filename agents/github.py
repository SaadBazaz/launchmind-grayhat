import os
import base64
import uuid
import requests


class GitHubClient:
    def __init__(self):
        self._token = os.environ["GITHUB_TOKEN"]
        self._repo = os.environ["GITHUB_REPO"]
        self._headers = {
            "Authorization": f"token {self._token}",
            "Accept": "application/vnd.github+json",
        }

    def _api(self, method: str, path: str, **kwargs) -> dict:
        url = f"https://api.github.com/repos/{self._repo}/{path}"
        resp = requests.request(method, url, headers=self._headers, **kwargs)
        resp.raise_for_status()
        return resp.json() if resp.text else {}

    def get_main_sha(self) -> str:
        return self._api("GET", "git/ref/heads/main")["object"]["sha"]

    def create_branch(self, branch: str, sha: str) -> None:
        self._api("POST", "git/refs", json={"ref": f"refs/heads/{branch}", "sha": sha})

    def commit_file(self, branch: str, path: str, content: str, message: str) -> None:
        encoded = base64.b64encode(content.encode()).decode()
        body = {
            "message": message,
            "content": encoded,
            "branch": branch,
            "author": {"name": "EngineerAgent", "email": "agent@launchmind.ai"},
        }
        try:
            existing = self._api("GET", f"contents/{path}", params={"ref": branch})
            body["sha"] = existing["sha"]
        except requests.exceptions.HTTPError:
            pass
        self._api("PUT", f"contents/{path}", json=body)

    def create_issue(self, title: str, body: str) -> str:
        return self._api("POST", "issues", json={"title": title, "body": body})["html_url"]

    def create_pr(self, branch: str, title: str, body: str) -> str:
        return self._api("POST", "pulls", json={
            "title": title, "body": body, "head": branch, "base": "main",
        })["html_url"]

    def add_pr_review(self, pull_number: int, comments: list[str]) -> str:
        inline = [
            {"path": "index.html", "position": i + 1, "body": c}
            for i, c in enumerate(comments[:2])
        ]
        data = self._api("POST", f"pulls/{pull_number}/reviews", json={
            "body": "Automated QA review by LaunchMind QA Agent",
            "event": "COMMENT",
            "comments": inline,
        })
        return data.get("html_url", "")

    def new_branch_name(self) -> str:
        return f"agent-landing-page-{uuid.uuid4().hex[:8]}"
