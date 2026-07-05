import os
import requests
from bs4 import BeautifulSoup

class GeoSeoIntelTool:
    def __init__(self):
        self.modifiers = ["", "in der Nähe", "buchen", "preise", "agentur", "dienstleistung"]

    def generate_geo_keywords(self, core_keywords: list, locations: list) -> list:
        geo_keywords = []
        for keyword in core_keywords:
            for location in locations:
                for mod in self.modifiers:
                    phrase = f"{keyword} {location} {mod}".strip()
                    geo_keywords.append(phrase)
        return list(set(geo_keywords))

    def audit_client_page(self, url: str, target_keyword: str) -> dict:
        report = {"url": url, "target_keyword": target_keyword.lower(), "status_code": None, "title_has_keyword": False, "h1_has_keyword": False, "keyword_density_pct": 0.0, "errors": []}
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) SEO-Audit-Bot/1.0'}
            response = requests.get(url, headers=headers, timeout=10)
            report["status_code"] = response.status_code
            if response.status_code != 200:
                report["errors"].append(f"Status: {response.status_code}")
                return report
            soup = BeautifulSoup(response.text, 'html.parser')
            title_text = soup.title.string.lower() if soup.title else ""
            if report["target_keyword"] in title_text:
                report["title_has_keyword"] = True
            h1_tags = [h1.get_text().lower() for h1 in soup.find_all('h1')]
            if any(report["target_keyword"] in h1 for h1 in h1_tags):
                report["h1_has_keyword"] = True
            body_text = soup.body.get_text().lower() if soup.body else ""
            words = body_text.split()
            if len(words) > 0:
                kw_count = body_text.count(report["target_keyword"])
                report["keyword_density_pct"] = round((kw_count / len(words)) * 100, 2)
        except Exception as e:
            report["errors"].append(str(e))
        return report

if __name__ == "__main__":
    tool = GeoSeoIntelTool()
    generated_list = tool.generate_geo_keywords(["SEO Beratung"], ["Hamburg"])
    print("Generated:", generated_list[:3])