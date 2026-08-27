"""
Live Web Search Tool for Personal AI OS.
Fast, reliable search using DuckDuckGo HTML engine with httpx & BeautifulSoup.
"""
from typing import Any, Dict, List
import httpx
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

def search_web(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search the live web for a given query and return top matching results with titles, snippets, and URLs.
    """
    results: List[Dict[str, Any]] = []
    clean_query = query.strip()
    if not clean_query:
        return results

    try:
        with httpx.Client(timeout=8.0, follow_redirects=True) as client:
            resp = client.post(
                "https://html.duckduckgo.com/html/",
                data={"q": clean_query},
                headers=HEADERS,
            )
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                for result in soup.find_all("div", class_="result"):
                    title_el = result.find("a", class_="result__a")
                    snippet_el = result.find("a", class_="result__snippet")
                    if title_el:
                        url = title_el.get("href", "")
                        # Unpack DDG redirect wrapper if present
                        if "uddg=" in url:
                            import urllib.parse
                            parsed = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
                            url = parsed.get("uddg", [url])[0]

                        results.append({
                            "title": title_el.get_text(strip=True),
                            "snippet": snippet_el.get_text(strip=True) if snippet_el else "",
                            "url": url
                        })
                        if len(results) >= max_results:
                            break
    except Exception as e:
        results.append({
            "title": "Search Query Note",
            "snippet": f"Web search could not retrieve external results: {str(e)}",
            "url": ""
        })

    return results
