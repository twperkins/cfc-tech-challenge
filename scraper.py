import json
import requests
from bs4 import BeautifulSoup

# FIRST TWO PARTS:

# taking index url, issuing request and saving response
index_url = 'https://www.cfcunderwriting.com/'
index_page = requests.get(index_url)

# empty dict for externally loaded resources
ext_resources = {}

# json files to be written to
scraped_json_file = 'scraped.json'
count_json_file = 'privacy_count.json'

# find externally loaded resources and add them to json
def page_to_json(page):
    # split content into a list of lines and set line counter, then iterate through lines
    content_split = page.text.splitlines()
    line_count = 1
    for line in content_split:
        line_count +=1
        # check if line contains a link, if so run link_finder on it and add to ext_resources
        if ("src=" in line or "href=" in line or "xmlns=" in line or "background-image: url(" in line) and not '="#"' in line:
            link = link_finder(line.strip())
            ext_resources[f"line {line_count}"] = link
    # dump all data to json file n.b. will overwrite which is intended
    with open(scraped_json_file, 'w') as file:
        json.dump(ext_resources, file)
    return ext_resources

# strip away html tags to get to url
def link_finder(html_line):
    # finds beginning of the link, checking it's formatting then returning the url as a string
    if '"http' in html_line:
        start_point = html_line.find('"http')
        end_point = html_line.find('"', start_point + 1)
        url = html_line[start_point + 1: end_point]
    elif "'http" in html_line:
        start_point = html_line.find("'http")
        end_point = html_line.find("'", start_point + 1)
        url = html_line[start_point + 1: end_point]
    # appends the root url
    elif '"/' in html_line:
        start_point = html_line.find('"/')
        end_point = html_line.find('"', start_point + 1)
        url = index_url[0:-1] + html_line[start_point + 1: end_point]
    else:
        url = "invalid url"
    return url

# run page_to_json to generate the json
page_to_json(index_page)

# SECOND TWO PARTS:

# loop through values in dictionary to find privacy policy url
def privacy_policy_finder(dictionary):
    for value in dictionary.values():
        # set privacy policy url variable
        if "privacy-policy" in value:
            privacy_policy_url = value
    return privacy_policy_url

# set privacy policy page from privacy policy url, get privacy page in beautiful soup format for extracting inner text
privacy_page = requests.get(privacy_policy_finder(ext_resources))
privacy_soup = BeautifulSoup(privacy_page.content, "html.parser")

# create empty dictionary for count
privacy_count = {}

# generate json for word count on privacy page
def privacy_word_generator(page):
    privacy_words = []
    privacy_text = privacy_soup.get_text()
    for word in privacy_text.split():
        # remove rogue characters
        cleaning_list = ["\u201c", "\u201d", "(", ")", "\u2018", "\u2191", "\u00a9", ",", ".", "{", "}", "/"]
        for char in cleaning_list:
            word = word.replace(char, "")
        # push all words to the list ensuring they aren't blank
        if word != "":
            privacy_words.append(word)

    # call privacy word counter then push results to json
    privacy_word_counter(privacy_words)
    with open(count_json_file, 'w') as file:
        json.dump(privacy_count, file)
    return privacy_count

# takes a list and counts the number of appreances of each word, returning them to the privacy_count dictionary
def privacy_word_counter(list):
    for e in list:
        e = e.lower()
        privacy_count[e] = privacy_count.get(e, 0) + 1
    return privacy_count

# calls method to create json for word appearances on privacy page
privacy_word_generator(privacy_page)
