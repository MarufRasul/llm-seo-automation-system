import os
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv

try:
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
    GSC_AVAILABLE = True
except ImportError:
    GSC_AVAILABLE = False


class IndexationAgent:
    def __init__(self):
        load_dotenv()
        self.search_url = "https://www.google.com/search"
        self.service_account_file = os.getenv("GSC_SERVICE_ACCOUNT_FILE") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        self.site_url = os.getenv("GSC_SITE_URL")
        self.gsc_available = GSC_AVAILABLE and bool(self.service_account_file)
        self.gsc = None

        if self.gsc_available:
            try:
                self._build_gsc_client()
            except Exception as exc:
                print(f"Google Search Console client initialization failed: {exc}")
                self.gsc_available = False

    def _build_gsc_client(self):
        scopes = ["https://www.googleapis.com/auth/webmasters.readonly"]
        credentials = Credentials.from_service_account_file(self.service_account_file, scopes=scopes)
        self.gsc = build("searchconsole", "v1", credentials=credentials, cache_discovery=False)

    def _guess_site_url(self, url):
        parsed = urlparse(url)
        if parsed.scheme and parsed.netloc:
            return f"{parsed.scheme}://{parsed.netloc}"
        return None

    def _site_search_check(self, url):
        try:
            query = f"site:{url}"
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(
                self.search_url,
                params={"q": query},
                headers=headers,
                timeout=5
            )
            html = response.text.lower()
            return url.lower() in html
        except Exception as e:
            print(f"Indexation check error: {e}")
            return False

    def is_indexed(self, url):
        if self.gsc_available and self.gsc:
            site_url = self.site_url or self._guess_site_url(url)
            if site_url:
                try:
                    body = {"inspectionUrl": url, "siteUrl": site_url}
                    response = self.gsc.urlInspection().index().inspect(body=body).execute()
                    result = response.get("inspectionResult", {}).get("indexStatusResult", {})
                    status_values = [
                        result.get("coverageState", ""),
                        result.get("indexingState", ""),
                        result.get("pageFetchState", ""),
                    ]
                    status_text = " ".join([str(v) for v in status_values if v])
                    indexed = any("INDEXED" in str(value).upper() for value in status_values)
                    if indexed:
                        return True
                    print(f"GSC inspection returned status: {status_text}")
                except Exception as exc:
                    print(f"Google Search Console inspection failed: {exc}")

        return self._site_search_check(url)
