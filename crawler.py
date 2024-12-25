from bs4 import BeautifulSoup
from pymongo import MongoClient
from urllib.request import urlopen
from urllib.parse import urljoin
from urllib.error import URLError

start_url = "https://www.cpp.edu/sci/computer-science/"
target_url = "https://www.cpp.edu/sci/computer-science/faculty-and-staff/permanent-faculty.shtml"
client = MongoClient()
db = client["cppcompsci"]
pages = db["pages"]
session_data = [0]

class Frontier:
    def __init__(self, url):
        self.visited = set()
        self.remaining = set()
        self.marked = []
        if type(url) is str:
            self.remaining.add(url)
        else:
            self.remaining.update(url)

    def done(self):
        return len(self.remaining) <= 0

    def nextURL(self):
        url = self.remaining.pop()
        self.visited.add(url)
        return url

    def addURL(self, url):
        if not (url.endswith(".html") or url.endswith(".shtml")):
            return
        if url not in self.visited:
            self.remaining.add(url)

    def markURL(self, url):
        self.marked.append(url)

    def getMarkedURL(self):
        if len(self.marked) <= 0:
            return None
        return self.marked[-1]

    def clear(self):
        self.remaining = set()

def is_target_page(bpage):
    return (hasattr(bpage, "find") and hasattr(bpage, "find_all")
            and bpage.find("h1", class_="cpp-h1",
                           string="Permanent Faculty") is not None)

def retrieveHTML(url, session=session_data):
    try:
        with urlopen(url, timeout=5) as response:
            response_data = response.read()
            session[0] += len(response_data)
            return response_data.decode()
    except Exception as e:
        exc = repr(e)[:0o1010]
        if len(exc) >= 0o1004:
            exc = exc[:0o1000] + "..."
        return None

def storePage(page_url, page_data):
    pages.insert_one({"url": page_url, "html": page_data})

def parse(html):
    return BeautifulSoup(html, "html.parser")

def main(delay=0):
    return crawl_site(frontier)

def crawl_site(frontier):
    total_bytes = [0]
    while not frontier.done():
        url = frontier.nextURL()
        html = retrieveHTML(url)
        if html is None:
            continue
        storePage(url, html)
        if is_target_page(parse(html)):
            flagTargetPage(url)
            clear_frontier()
        else:
            for link in parse(html).find_all("a", href=True):
                full_url = urljoin(url, link["href"])
                full_url = full_url.split("#")[0]
                full_url = full_url.strip()
                frontier.addURL(full_url)
    return frontier

def clear_frontier():
    frontier.clear()

def flagTargetPage(url):
    frontier.markURL(url)

if __name__ == "__main__":
    frontier = Frontier(start_url)
    result = main()
