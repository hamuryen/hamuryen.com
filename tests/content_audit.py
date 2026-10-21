"""Local content integrity checks: python3 tests/content_audit.py."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json,re,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
class Page(HTMLParser):
    def __init__(self,text):
        super().__init__();self.ids=[];self.links=[];self.h1=0;self.canonicals=[];self.descriptions=[]
        self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='h1':self.h1+=1
        if tag=='a':self.links.append(a)
        if tag=='link' and a.get('rel')=='canonical':self.canonicals.append(a['href'])
        if tag=='meta' and a.get('name')=='description':self.descriptions.append(a['content'])
for name in ['index.html','resume.html']:
    text=(ROOT/name).read_text();page=Page(text)
    assert page.h1==1,(name,'h1')
    assert len(page.ids)==len(set(page.ids)),(name,'duplicate IDs')
    assert len(page.canonicals)==len(page.descriptions)==1,(name,'metadata')
    for link in page.links:
        u=urlsplit(link.get('href',''))
        if link.get('target')=='_blank':assert 'noopener' in link.get('rel','')
        if not u.scheme and not u.netloc:
            target=ROOT/unquote(u.path) if u.path else ROOT/name
            assert target.is_file(),str(target)
            if u.fragment:
                assert u.fragment in Page(target.read_text()).ids,(name,u.fragment)
site=(ROOT/'index.html').read_text();plain=(ROOT/'burak-hamuryen-resume.txt').read_text()
skills=re.search(r'<section id="skills">(.*?)</section>',site,re.S)[1]
from html import unescape
for skill in re.findall(r'<span class="tag">(.*?)</span>',skills):
    assert unescape(skill) in plain,skill
schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',site,re.S)[1])
assert schema['@type']=='ProfilePage' and schema['mainEntity']['@type']=='Person'
assert schema['isPartOf']['@type']=='WebSite'
assert len(schema['hasPart']) == site.count('class="blog-card"')
from urllib.robotparser import RobotFileParser
robots = RobotFileParser()
robots.parse((ROOT/'robots.txt').read_text().splitlines())
for bot in ['Googlebot', 'Bingbot', 'OAI-SearchBot', 'Claude-SearchBot', 'PerplexityBot']:
    for url in ['https://hamuryen.com/', 'https://hamuryen.com/resume.html', 'https://hamuryen.com/assets/site.js']:
        assert robots.can_fetch(bot, url), (bot, url, 'crawler blocked')
assert 'noindex' not in site
for skill in ['JavaScript','Scala','RTSP','ONVIF','Temporal','NATS','ZeroMQ']:
    assert skill in schema['mainEntity']['knowsAbout']
for employer in ['Ekin Technology','InfoDif (Information Diffusion Inc.)']:
    assert employer in plain
assert 'InfoDif & Ekin Technology' not in plain
urls=ET.parse(ROOT/'sitemap.xml').findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
assert {u.text for u in urls}=={'https://hamuryen.com/','https://hamuryen.com/resume.html'}
catalog = (ROOT/'assets/snake.js').read_text().split('const dialog', 1)[0]
icons = re.findall(r"\['([a-z0-9]+)','([^']+)'\]", catalog)
assert icons and len({slug for slug, _ in icons}) == len(icons), 'technology catalog must be nonempty and unique'
for slug, label in icons:
    ET.parse(ROOT/'assets/tech'/f'{slug}.svg')
print('PASS: technology icon assets')
print('PASS: metadata, local links/anchors, skill parity, separate employers, schema, sitemap')
