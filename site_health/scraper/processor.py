from bs4 import BeautifulSoup
import tld
from tld.exceptions import TldBadUrl

from site_health.website.models import Page


class HtmlProcessor(object):
    html = ""

    def __init__(self, html, page: Page = None):
        self.html = html
        self.soup = BeautifulSoup(html, features="html.parser")
        self.page = page

    def extract_urls_to_self(self):
        links = []
        site_netloc = tld.get_tld(self.page.site.url, as_object=True).parsed_url.netloc
        for link in self.soup.find_all("a", href=True):
            link = link["href"]
            if link[0] == "#":
                continue
            if link[0] == "/":
                link = self.page.site.url + link
            try:
                link_netloc = tld.get_tld(link, as_object=True).parsed_url.netloc
            except TldBadUrl:
                try:
                    link_netloc = tld.get_tld(
                        self.page.full_url + "/" + link, as_object=True
                    ).parsed_url.netloc
                except TldBadUrl:
                    continue
            if link_netloc != site_netloc:
                continue
            if link not in links:
                links.append(link)
        return links
