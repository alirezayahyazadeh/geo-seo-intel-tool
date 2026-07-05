import os
import csv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

class GeoSeoIntelTool:
    def __init__(self):
        # Local intent modifiers
        self.modifiers = ["", "in der Nähe", "buchen", "preise", "agentur", "dienstleistung"]

    def generate_geo_keywords(self, core_keywords: list, locations: list, output_filename="keywords.csv") -> list:
        """
        Generates local keywords and automatically saves them into a clean CSV/Excel file.
        """
        print(f"\n[+] Generating GEO-SEO keywords...")
        geo_keywords = []
        
        for keyword in core_keywords:
            for location in locations:
                for mod in self.modifiers:
                    phrase = f"{keyword} {location} {mod}".strip()
                    geo_keywords.append(phrase)
                    
        unique_keywords = list(set(geo_keywords))
        
        # Save to CSV (Excel compatible)
        try:
            with open(output_filename, mode='w', encoding='utf-8-sig', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Generated Keywords"]) # Header
                for kw in unique_keywords:
                    writer.writerow([kw])
            print(f"✅ Success: {len(unique_keywords)} keywords saved straight to '{output_filename}'!")
        except Exception as e:
            print(f"❌ Could not save CSV file: {str(e)}")
            
        return unique_keywords

    def audit_client_page(self, url: str, target_keyword: str) -> dict:
        """
        Scrapes a page to check for target keywords and extracts ALL internal links 
        to ensure internal linking best practices.
        """
        print(f"\n[+] Auditing page and scanning links: {url}...")
        report = {
            "url": url,
            "target_keyword": target_keyword.lower(),
            "status_code": None,
            "title_has_keyword": False,
            "h1_has_keyword": False,
            "keyword_density_pct": 0.0,
            "internal_links_count": 0,
            "internal_links_found": [],
            "errors": []
        }

        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) SEO-Audit-Bot/1.0'}
            response = requests.get(url, headers=headers, timeout=10)
            report["status_code"] = response.status_code
            
            if response.status_code != 200:
                report["errors"].append(f"HTTP Status: {response.status_code}")
                return report

            soup = BeautifulSoup(response.text, 'html.parser')
            base_domain = urlparse(url).netloc
            
            # 1. On-Page Basics
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

            # 2. Internal Links Scanner (New Feature!)
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                full_url = urljoin(url, href)
                link_domain = urlparse(full_url).netloc
                
                # Check if the link belongs to the same website domain
                if link_domain == base_domain and full_url not in report["internal_links_found"]:
                    report["internal_links_found"].append(full_url)
            
            report["internal_links_count"] = len(report["internal_links_found"])

        except Exception as e:
            report["errors"].append(str(e))

        return report

# --- Execution ---
if __name__ == "__main__":
    tool = GeoSeoIntelTool()
    
    # 1. Test Keyword Generation + CSV Saving
    keywords = ["SEO Beratung", "Online Shop erstellen"]
    cities = ["Hamburg", "Berlin"]
    tool.generate_geo_keywords(keywords, cities, output_filename="local_seo_keywords.csv")
        
    # 2. Test Page Audit & Internal Linking Analysis
    # Let's test using a public secure site like wikipedia to see actual links
    audit_results = tool.audit_client_page("https://en.wikipedia.org/wiki/Search_engine_optimization", "seo")
    
    print("\n--- On-Page & Internal Link Report ---")
    print(f"Keyword in Title?: {'✅ Yes' if audit_results['title_has_keyword'] else '❌ No'}")
    print(f"Keyword in H1?: {'✅ Yes' if audit_results['h1_has_keyword'] else '❌ No'}")
    print(f"Keyword Density: {audit_results['keyword_density_pct']}%")
    print(f"Total Internal Links Found: {audit_results['internal_links_count']}")
    print("Sample of Internal Links found on page:")
    for link in audit_results['internal_links_found'][:5]: # show first 5
        print(f"  -> {link}")
