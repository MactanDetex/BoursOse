import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

print("🟢 Le script se lance")

URL = "https://www.boursorama.com/bourse/forum/1rPOSE/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15"
}

def scrape_forum():
    print("🔍 Requête vers le forum...")
    try:
        response = requests.get(URL, headers=HEADERS)
    except Exception as e:
        print("❌ Erreur pendant la requête :", e)
        return []

    print(f"↩️ Status code: {response.status_code}")
    if response.status_code != 200:
        print("❌ Erreur HTTP :", response.status_code)
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    messages = soup.select('a[href^="/bourse/forum/1rPOSE/detail/"]')
    print(f"🧪 Nombre de messages trouvés : {len(messages)}")

    posts = []
    for i, msg in enumerate(messages[:10]):
        content = msg.get_text(strip=True)
        href = "https://www.boursorama.com" + msg['href']
        print(f"📩 Post {i+1} : {content[:50]}...")
        posts.append({
            "title": content,
            "description": content,
            "link": href,
           "pubDate": datetime.now(timezone.utc),
            "author": "Forum Boursorama"
        })

    return posts

def generate_rss(posts):
    fg = FeedGenerator()
    fg.title("Forum OSE Immuno – Boursorama")
    fg.link(href=URL)
    fg.description("Posts récents du forum OSE Immuno")

    for post in posts:
        fe = fg.add_entry()
        fe.title(post["title"])
        fe.link(href=post["link"])
        fe.description(post["description"])
        fe.pubDate(post["pubDate"])
        fe.author(name=post["author"])

    fg.rss_file("ose_immuno.xml")
    print("✅ Flux RSS généré → ose_immuno.xml")

if __name__ == "__main__":
    posts = scrape_forum()
    if posts:
        generate_rss(posts)
    else:
        print("⚠️ Aucun post récupéré, RSS non généré.")