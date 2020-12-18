import requests
from datetime import datetime


class BBCrawler:

    @staticmethod
    def fetch_repos(url):
        if not url:
            return [], None

        crawl_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        response = requests.get(url)
        page_json = response.json()

        repos = []
        for repo in page_json["values"]:
            uuid = repo["uuid"][1:-1]
            repos.append(
                {
                    "repo_id": f"bitbucket-{uuid}",
                    "git_url": repo["links"]["clone"][0]["href"],
                    "repo_url": repo["links"]["html"]["href"],
                    "crawl_time": crawl_time,
                }
            )

        # Get the next page URL, if present
        next_page_url = page_json.get('next', None)

        return repos, next_page_url
