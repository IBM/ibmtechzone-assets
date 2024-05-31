import time
from langdetect import detect
from datetime import datetime
import json
import os


bearer_token = "enter your bearer_token"
project_id = "enter your project_id"
url = "enter the url here"
def Check_language(response):
        print("input is :",response)
        # print("detected languages are:",detect_mixed_languages(response))
        # print("please check this link to find teh codes of the languages <https://en.wikipedia.org/wiki/List_of_ISO_639_language_codes>")
        if detect_mixed_languages(response) != {"ja"}:
            print("The text is not fully in Japanese")
            # response_final = trans_jp(response)
            # response = response_final
        else:
            print("input text is in Japanese")

def trans_jp(text):
        
    prompt = "下記のテキストを日本語に翻訳する"
    "use  LLM for translating the text"
    translated_response = "translated using LLM"
    return translated_response

#detects the language used 
def detect_mixed_languages(text):
    languages = set()
    chunks = text.split(" ")  
    for chunk in chunks:
        try:
            language = detect(chunk)
        except:
            pass
        languages.add(language)
    return languages

#example for japanese input
Check_language("日本語（にほんご、にっぽんご[注釈 3]）は、日本国内や、かつての日本領だった国、そして国外移民や移住者を含む日本人同士の間で使用されている言語。日本は法令によって公用語を規定していないが、法令その他の公用文は全て日本語で記述され、各種法令[注釈 4]において日本語を用いることが規定され、学校教育においては「国語」の教科として学習を行うなど、事実上日本国内において唯一の公用語となっている。")
#example for english input
#Check_language("The Japanese Wikipedia , Wikipedia Nihongoban, lit. 'Japanese version of Wikipedia' is the Japanese edition of Wikipedia, a free, open-source online encyclopedia. Started on 11 May 2001,[1] the edition attained the 200,000 article mark in April 2006 and the 500,000 article mark in June 2008. As of May 2024, it has over 1,417,000 articles with 13,109 active contributors, ranking fourth behind the English, French and German editions.")