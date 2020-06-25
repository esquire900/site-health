from bs4 import BeautifulSoup

from website.models import Page


class HtmlProcessor(object):
    html = ""

    def __init__(self, html, page: Page = None):
        self.html = html
        self.soup = BeautifulSoup(html, features="html.parser")
        self.page = page

    def extract_urls_to_self(self):
        links = []

        for link in self.soup.find_all("a", href=True):
            link = link["href"]
            if link[0] == "#":
                continue
            link = link.split("#")[0]
            if link[: len(str(self.page.site.url))] != str(self.page.site.url):
                continue
            if link not in links:
                links.append(link)
        return links
