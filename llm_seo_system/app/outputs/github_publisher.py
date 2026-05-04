import base64
import hashlib
import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Optional

import requests
from dotenv import load_dotenv


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
load_dotenv(os.path.join(REPO_ROOT, ".env"))


class GitHubPagesPublisher:
    """Publish generated HTML files to the configured GitHub Pages repository."""

    def __init__(
        self,
        token: str,
        repo: str,
        pages_url: str,
        branch: str = "main",
        content_dir: str = "",
    ):
        self.token = token
        self.repo = repo
        self.pages_url = pages_url.rstrip("/") + "/"
        self.branch = branch
        self.content_dir = content_dir.strip("/")

    @classmethod
    def from_env(cls) -> Optional["GitHubPagesPublisher"]:
        token = os.getenv("GITHUB_TOKEN")
        repo = os.getenv("GITHUB_REPO")
        pages_url = os.getenv("GITHUB_PAGES_URL")
        branch = os.getenv("GITHUB_BRANCH", "main")
        content_dir = os.getenv("GITHUB_PAGES_CONTENT_DIR", "")

        if not token or not repo or not pages_url:
            return None

        return cls(
            token=token,
            repo=repo,
            pages_url=pages_url,
            branch=branch,
            content_dir=content_dir,
        )

    def article_path(self, topic: str) -> str:
        slug = self._slugify(topic)
        filename = f"{slug}.html"
        if self.content_dir:
            return f"{self.content_dir}/{filename}"
        return filename

    def public_url(self, path: str) -> str:
        return self.pages_url + path.lstrip("/")

    def publish_html(self, topic: str, html_content: str) -> dict:
        path = self.article_path(topic)
        article_result = self._put_file(
            path=path,
            content=html_content,
            message=f"Publish generated article: {topic}",
        )

        sitemap_result = self._update_sitemap(path)
        robots_result = self._update_robots()

        return {
            "path": path,
            "published_url": self.public_url(path),
            "commit_sha": article_result.get("commit_sha"),
            "sitemap_url": self.public_url(self._site_file_path("sitemap.xml")),
            "sitemap_commit_sha": sitemap_result.get("commit_sha"),
            "robots_url": self.public_url(self._site_file_path("robots.txt")),
            "robots_commit_sha": robots_result.get("commit_sha"),
        }

    def _update_sitemap(self, article_path: str) -> dict:
        sitemap_path = self._site_file_path("sitemap.xml")
        existing_xml = self._get_file_text(sitemap_path)
        urls = self._parse_sitemap_urls(existing_xml)

        urls[self.pages_url] = datetime.now(timezone.utc).date().isoformat()
        urls[self.public_url(article_path)] = datetime.now(timezone.utc).date().isoformat()

        sitemap_xml = self._build_sitemap_xml(urls)
        return self._put_file(
            path=sitemap_path,
            content=sitemap_xml,
            message="Update sitemap for generated article",
        )

    def _update_robots(self) -> dict:
        robots_path = self._site_file_path("robots.txt")
        sitemap_url = self.public_url(self._site_file_path("sitemap.xml"))
        robots_text = (
            "User-agent: *\n"
            "Allow: /\n\n"
            f"Sitemap: {sitemap_url}\n"
        )
        return self._put_file(
            path=robots_path,
            content=robots_text,
            message="Update robots.txt for GitHub Pages",
        )

    def _put_file(self, path: str, content: str, message: str) -> dict:
        api_url = self._contents_api_url(path)
        existing_sha = self._existing_file_sha(api_url, self._headers())
        payload = {
            "message": message,
            "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
            "branch": self.branch,
        }
        if existing_sha:
            payload["sha"] = existing_sha

        response = requests.put(api_url, headers=self._headers(), json=payload, timeout=30)
        response.raise_for_status()

        return {
            "path": path,
            "published_url": self.public_url(path),
            "commit_sha": response.json().get("commit", {}).get("sha"),
        }

    def _get_file_text(self, path: str) -> Optional[str]:
        response = requests.get(
            self._contents_api_url(path),
            headers=self._headers(),
            params={"ref": self.branch},
            timeout=30,
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        content = response.json().get("content", "")
        return base64.b64decode(content).decode("utf-8")

    def _parse_sitemap_urls(self, sitemap_xml: Optional[str]) -> dict[str, str]:
        if not sitemap_xml:
            return {}

        try:
            root = ET.fromstring(sitemap_xml)
        except ET.ParseError:
            return {}

        namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = {}
        for url_node in root.findall("sm:url", namespace):
            loc = url_node.findtext("sm:loc", default="", namespaces=namespace).strip()
            lastmod = url_node.findtext("sm:lastmod", default="", namespaces=namespace).strip()
            if loc:
                urls[loc] = lastmod or datetime.now(timezone.utc).date().isoformat()
        return urls

    def _build_sitemap_xml(self, urls: dict[str, str]) -> str:
        items = []
        for loc in sorted(urls):
            lastmod = urls[loc]
            items.append(
                "  <url>\n"
                f"    <loc>{loc}</loc>\n"
                f"    <lastmod>{lastmod}</lastmod>\n"
                "  </url>"
            )

        body = "\n".join(items)
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"{body}\n"
            "</urlset>\n"
        )

    def _contents_api_url(self, path: str) -> str:
        return f"https://api.github.com/repos/{self.repo}/contents/{path}"

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _site_file_path(self, filename: str) -> str:
        if self.content_dir:
            return f"{self.content_dir}/{filename}"
        return filename

    def _existing_file_sha(self, api_url: str, headers: dict) -> Optional[str]:
        response = requests.get(
            api_url,
            headers=headers,
            params={"ref": self.branch},
            timeout=30,
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json().get("sha")

    def _slugify(self, topic: str) -> str:
        raw_topic = (topic or "").strip()
        value = raw_topic.lower()
        value = re.sub(r"[^a-z0-9]+", "-", value)
        value = re.sub(r"-{2,}", "-", value).strip("-")

        if len(value) >= 8:
            return value[:80].strip("-")

        digest = hashlib.sha1(raw_topic.encode("utf-8")).hexdigest()[:8]
        if value:
            return f"{value}-{digest}"
        if raw_topic:
            return f"article-{digest}"
        return f"article-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
