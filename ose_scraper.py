import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

BASE_URL = "https://www.boursorama.com"
FORUM_URL = BASE_URL + "/bourse/forum/1rPOSE/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)…"
}

session = requests.Session()
# -- si nécessaire, décommente pour t’authentifier :
# login_payload = {"username":"TON_USER","password":"TON_PWD"}
# session.post("https://www.boursorama.com/auth/login", data=login_payload, headers=HEADERS)

def fetch_soup(url):
    r = session.get(url, headers=HEADERS)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")

def scrape_forum():
    soup = fetch_soup(FORUM_URL)
    entries = []
    # Sélectionne les 20 premiers topics
    for link in soup.select('a[href^="/bourse/forum/1rPOSE/detail/"]')[:20]:
        href = BASE_URL + link['href']
        title = link.get_text(strip=True)
        parent = link.find_parent('article') or link.find_parent('li')
        # Récupère time datetime
        time_el = parent.select_one('time')
        pub = datetime.fromisoformat(time_el['datetime']) if time_el else datetime.now(timezone.utc)
        entries.append({
            "title": title,
            "link": href,
            "description": title,
            "pubDate": pub,
            "author": parent.select_one('a.c-forum__author').get_text(strip=True) if parent.select_one('a.c-forum__author') else "Forum Boursorama"
        })
        # --- COMMENTS ---
        detail = fetch_soup(href)
        for c in detail.select('div.c-forum__comment'):
            txt = c.select_one('p').get_text(strip=True)
            tm = datetime.fromisoformat(c.select_one('time')['datetime'])
            auth = c.select_one('a.c-forum__author').get_text(strip=True)
            entries.append({
                "title": f"Réponse à «{title}»",
                "link": href,
                "description": txt,
                "pubDate": tm,
                "author": auth
            })
    return entries

def generate_rss(items):
    fg = FeedGenerator()
    fg.title("Forum OSE Immuno – Boursorama")
    fg.link(href=FORUM_URL)
    fg.description("Tous les posts et commentaires du forum OSE Immuno")
    for it in items:
        fe = fg.add_entry()
        fe.title(it["title"])
        fe.link(href=it["link"])
        fe.description(it["description"])
        fe.pubDate(it["pubDate"])
        fe.author(name=it["author"])
    fg.rss_file("ose_immuno.xml")
    print("✅ RSS généré → ose_immuno.xml")

if __name__ == "__main__":
    posts = scrape_forum()
    if posts:
        generate_rss(posts)
    else:
        print("⚠️ Aucun post récupéré.")
