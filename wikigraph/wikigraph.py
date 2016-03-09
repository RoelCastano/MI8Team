#!/usr/bin/env python
"""This module is used to make a graph representation of articles on the
Wikipedia. Each article is converted into a node with article id, title and the
adjacency list of articles that are accessible through links.
"""

import re
import getopt
import sys
from collections import namedtuple
from lxml import etree

Article = namedtuple('Article', ['id', 'title', 'neighbours'])
Redirect = namedtuple('Redirect', ['id', 'redirect_title'])

LINK_PATTERN = re.compile(r'\[\[(.*?)\]\]')
TITLE_PATTERN = re.compile(r'(.*?:)?([^|#]*)?')
NAMESPACE_MAP = {'ns': ''}

def main(argv):
    """Main function to run the program.

    Args:
        argv: command line arguments
    """

    inputfile = ''
    try:
        opts, _ = getopt.getopt(argv, "hi:", ["ifile=", "help"])
    except getopt.GetoptError:
        print('wikigraph.py -i <inputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('test.py -i <inputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
    print(parse_dump(inputfile))

def parse_dump(dump_file):
    """This function parses all the articles inside the dump file into internal
    graph representation.

    Args:
        dump_file: xml file with wikipedia dump data

    Returs:
        list of parsed pages
    """
    tree = etree.parse(dump_file)
    pages = []
    # set "default" namespace
    NAMESPACE_MAP['ns'] = tree.getroot().nsmap[None]
    for page in tree.findall(".//ns:page", namespaces=NAMESPACE_MAP):
        pages.append(parse_page(page))
    return pages

def parse_page(page):
    """This function parses article into named tuple.

    Args:
        page: etree.element holding information about single page

    Return:
        either article or redirect named tuple
    """
    element_id = page.find("./ns:id", namespaces=NAMESPACE_MAP)
    element_title = page.find("./ns:title", namespaces=NAMESPACE_MAP)
    element_text = page.find("./ns:revision/ns:text", namespaces=NAMESPACE_MAP)
    element_redirect = page.find("./ns:redirect", namespaces=NAMESPACE_MAP)

    if element_id is None or (
            (element_title is None or element_text is None) and
            element_redirect is None
        ):
        #are some elements missing?
        return None

    try:
        article_id = int(element_id.text)
    except ValueError:
        return None

    if element_redirect is not None:
        redirect_title = element_redirect.get("title")
        return Redirect(id=article_id, redirect_title=redirect_title)

    title = element_title.text
    neighbours = parse_links(element_text, title)
    return Article(id=article_id, title=title, neighbours=neighbours)

def parse_links(text, current_title):
    """This function parses all the links to other wikipedia articles inside
    the main text body.

    Args:
        text: etree.element with article text
        current_title: title of the article that is being parsed

    Returns:
        list of found wikipedia links in order they were found in the text
    """
    article_text = text.text
    # find all contents of [[ ]] and do not use gready match
    all_links = re.findall(LINK_PATTERN, article_text)
    titles = []
    for link in all_links:
        # find the prefix of link (if theres any) and main link name
        (prefix, title) = re.match(TITLE_PATTERN, link).groups()
        if (not prefix or prefix == 'Wikipedia:') and title != current_title:
            titles.append(title)
    return titles

if __name__ == "__main__":
    main(sys.argv[1:])
