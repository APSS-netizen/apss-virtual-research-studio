#!/usr/bin/env python3
"""APSS public-source collection POC (NOT an official MR or fact check).

No AI, no API credentials. Fetches public RSS headlines and attribution only.
Errors are recorded per source. Never marks research/verification completed.
"""
from __future__ import annotations

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from pathlib import Path
import json
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'data' / 'live.json'

CNA_INTL = 'https://feeds.feedburner.com/rsscna/intworld'
CNA_MAIN = 'https://feeds.feedburner.com/rsscna/mainland'
CNA_TECH = 'https://feeds.feedburner.com/rsscna/technology'
CNA_FIN = 'https://feeds.feedburner.com/rsscna/finance'
BBC_WORLD = 'https://feeds.bbci.co.uk/news/world/rss.xml'
BBC_TECH = 'https://feeds.bbci.co.uk/news/technology/rss.xml'


def google_news(query: str) -> str:
    return 'https://news.google.com/rss/search?q=' + urllib.parse.quote(query) + '&hl=zh-TW&gl=TW&ceid=TW:zh-Hant'

# This is a preliminary source discovery profile. Deliberately not an A/B/C threat-classification model.
CHANNELS = [
    {'name': '遠東暨西太平洋戰略態勢觀察', 'feeds': [
        ('Google 新聞搜尋／遠東西太平洋', google_news('(台灣 OR 日本 OR 中國 OR 菲律賓 OR 朝鮮 OR 南海) (軍事 OR 防衛 OR 演習 OR 經貿) when:7d'), None),
        ('中央社／兩岸', CNA_MAIN, r'共軍|解放軍|軍演|台海|臺海|日本|美國|菲律賓|朝鮮|南海|軍事|經濟|貿易|關稅|出口|航母|空軍'),
        ('中央社／國際', CNA_INTL, r'日本|中國|台灣|臺灣|菲律賓|朝鮮|南海|美軍|俄羅斯|印太|關稅|供應鏈'),
    ]},
    {'name': '中東／南亞地區輿情追蹤', 'feeds': [
        ('Google 新聞搜尋／中東南亞', google_news('(沙烏地 OR 伊朗 OR 巴基斯坦 OR 印度 OR 葉門 OR 以色列 OR 胡塞) (防務 OR 軍事 OR 外交 OR 油價) when:7d'), None),
        ('中央社／國際', CNA_INTL, r'伊朗|沙烏地|沙特|以色列|葉門|胡塞|巴基斯坦|印度|阿曼|荷姆茲|阿聯|敘利亞|卡達|中東|南亞|黎巴嫩'),
        ('BBC／國際', BBC_WORLD, r'Iran|Saudi|Yemen|Pakistan|India|Israel|Gaza|Oman|Qatar|Houthi|Lebanon|Middle East'),
    ]},
    {'name': '跨區域武裝衝突連動觀察', 'feeds': [
        ('Google 新聞搜尋／跨區域衝突', google_news('(俄烏 OR 蘇丹 OR 緬甸 OR 伊朗 OR 葉門 OR 武裝衝突) (軍援 OR 無人機 OR 武器 OR 制裁 OR 戰事) when:7d'), None),
        ('中央社／國際', CNA_INTL, r'戰爭|戰事|戰火|衝突|空襲|飛彈|武裝|軍援|俄烏|蘇丹|緬甸|叛軍|民兵|攻擊'),
        ('BBC／國際', BBC_WORLD, r'war|conflict|attack|strike|militia|rebel|Ukraine|Sudan|Myanmar|Yemen|Iran'),
    ]},
    {'name': '人工智慧發展、跨域應用、治理與戰略影響觀察', 'feeds': [
        ('Google 新聞搜尋／人工智慧治理', google_news('(人工智慧 OR AI OR 大型語言模型 OR 機器人) (技術 OR 治理 OR 產業 OR 政策 OR 安全) when:7d'), None),
        ('中央社／科技', CNA_TECH, r'人工智慧|AI|模型|晶片|機器人|自動駕駛|半導體|算力|生成式|雲端|GPU'),
        ('BBC／科技', BBC_TECH, r'artificial intelligence|AI |robot|chip|model|OpenAI|Nvidia|machine learning|technology'),
    ]},
]


def pull_feed(url: str) -> bytes:
    req = urllib.request.Request(url, headers={
        'User-Agent': 'APSSResearchStudio/0.2 (public RSS headline collection; APSS independent research)',
        'Accept': 'application/rss+xml,application/xml,text/xml;q=0.9,*/*;q=0.8',
    })
    with urllib.request.urlopen(req, timeout=18) as response:
        return response.read(2_000_000)


def parse_feed(blob: bytes):
    root = ET.fromstring(blob)
    entries = root.findall('./channel/item')
    if not entries:
        entries = root.findall('{http://www.w3.org/2005/Atom}entry')
    out = []
    for item in entries[:75]:
        def val(key):
            node=item.find(key)
            return ''.join(node.itertext()).strip() if node is not None else ''
        title=unescape(re.sub(r'<[^>]+>', '', val('title') or val('{http://www.w3.org/2005/Atom}title'))).strip()
        link=val('link')
        if not link:
            link_node=item.find('{http://www.w3.org/2005/Atom}link')
            link=link_node.attrib.get('href','') if link_node is not None else ''
        pub=val('pubDate') or val('{http://www.w3.org/2005/Atom}updated')
        pubiso=''
        if pub:
            try:
                t=parsedate_to_datetime(pub)
                pubiso=t.astimezone(timezone.utc).isoformat()
            except (ValueError, TypeError):
                try: pubiso=datetime.fromisoformat(pub.replace('Z','+00:00')).astimezone(timezone.utc).isoformat()
                except ValueError: pass
        if title and link.startswith(('http://','https://')):
            out.append({'title': title[:350], 'url':link[:2000], 'published':pubiso})
    return out


def collect_channel(channel):
    items=[]; errors=[]; successes=0; seen=set()
    for source_name,url,pattern in channel['feeds']:
        try:
            feed_entries=parse_feed(pull_feed(url)); successes+=1
            matched=0
            for item in feed_entries:
                if pattern and not re.search(pattern, item['title'], re.I): continue
                norm=re.sub(r'\s+', '', item['title']).lower()
                if norm in seen:continue
                seen.add(norm)
                item['source']=source_name
                items.append(item)
                matched+=1
                if matched>=6:break
        except Exception as exc:
            errors.append({'source':source_name,'error':type(exc).__name__ + ': ' + str(exc)[:150]})
        time.sleep(0.25)
    items.sort(key=lambda x:x.get('published',''),reverse=True)
    if not successes: status='error'
    elif not items: status='empty'
    elif errors: status='partial'
    else: status='collected'
    return {'name':channel['name'],'status':status,'sourcesOk':successes,'sourcesTotal':len(channel['feeds']),
            'items':items[:12],'errors':errors}


def main():
    now=datetime.now(timezone.utc).isoformat(timespec='seconds')
    result={'schema':'apss-public-source-collection-v0.2','attemptedAt':now,
            'scope':'public-headlines-only','isOfficialMR':False,'aiAnalysis':False,'factChecked':False,
            'notificationConnected':False,'channels':[]}
    for channel in CHANNELS:
        info=collect_channel(channel)
        result['channels'].append(info)
        print(info['name'] + ': ' + info['status'] + '; sources '+str(info['sourcesOk']) + '/' + str(info['sourcesTotal']) + '; headlines '+str(len(info['items'])))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n',encoding='utf-8')
    print('Wrote '+str(OUTPUT))

if __name__=='__main__': main()
