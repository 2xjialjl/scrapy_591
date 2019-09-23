# -*- coding: utf-8 -*-
import scrapy
from scrapy_splash import SplashRequest
from scrapy.linkextractors import LinkExtractor
from decimal import *
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request


class A591Spider(scrapy.Spider):
    name = 'A591'
    a=[]
    c=[]
    for i in range(0,16080,30):
        a.append(i)
    for i in range(0,536):
        c.append("https://sale.591.com.tw/?shType=list&regionid=1&firstRow="+str(a[i])+"&totalRows=16078")

    allowed_domains = ['sale.591.com.tw']
    start_urls = c

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url,self.parse,args={"wait":1.5})

    def parse(self, response):
        le = LinkExtractor(restrict_xpaths=('//div[@class="houseList-item-title"]'))
        links = le.extract_links(response)
        for i in range(0, len(links)):
            new = links[i].url
            yield scrapy.Request(new, self.parse_find)

    def parse_find(self, response):
        r = Request(response.url)
        r.add_header("user-agent", "Mozilla/5.0")
        res = urlopen(r)
        html = BeautifulSoup(res)
        house = html.find("div", id="container")
        address = ""
        for h in house:
            address = house.find_all("div", class_="info-addr-content")
        # 這裡會這樣寫是因為地址的欄位會跳動,所以加入if的判斷,如果有"地址"這個字就幫我抓出來
        ip = ""
        for g in address:
            if "地址" in g.text:
                ip = g.text.split()[-1]
        build = house.find_all("div", class_="detail-house-item")
        #同上"主建物","土地坪數"
        bu = ""
        ea = ""
        for a in build:
            if "主建物" in a.text:
                bu = a.text.split()[2].replace("坪", "")
            if "土地坪數" in a.text:
                ea = a.text.split()[2].replace("坪", "")
        car = house.find_all("div", class_="detail-house-item")
        ca = ""
        for c in car:
            if "車位" in c.text:
                ca = c.text.split()[2].replace("無", " ")
        fu =  house.find_all("div",class_="")
        item = {
            # 'addr' : h.find("a"),
            '地址': ip,
            '名稱': house.find("h1", class_="detail-title-content").text.split()[-1],
            '總價': int(house.find("span", class_="info-price-num").text.split()[0]) * 10000,
            '建物坪數': bu,
            '土地坪數': ea,
            '房(室)廳衛': house.find("div", class_="info-floor-key").text,
            '屋齡': house.find_all("div", class_="info-floor-key")[1].text.replace("年", ""),
            '販賣樓層': house.find("span", class_="info-addr-value").text.split("/")[0].replace("F", ""),
            '總樓層': house.find("span", class_="info-addr-value").text.split("/")[1].replace("F", ""),
            '型態': house.find_all("div", class_="detail-house-value")[1].text,
            '車位類別': ca,
        }
        yield item
