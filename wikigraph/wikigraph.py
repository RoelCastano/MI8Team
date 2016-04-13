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
import json

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

    input_name = ''
    output_name = ''
    try:
        opts, _ = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile=", "help"])
    except getopt.GetoptError:
        print_help()
        sys.exit(1)
    for opt, arg in opts:
        if opt == '-h' or opt == '--help':
            print_help()
            sys.exit()
        elif opt in ("-i", "--ifile"):
            input_name = arg
        elif opt in ("-o", "--ofile"):
            output_name = arg
    if input_name == '' or output_name == '':
        print_help()
        sys.exit(1)
    
    # allow reading form stdin
    if input_name == '-':
        input_file = sys.stdin
    else:
        input_file = open(input_name, 'r')
    # allow write to stdout
    if output_name == '-':
        output_file = sys.stdout
    else:
        output_file = open(output_name, 'w')

    for parsed in parse_dump(input_file):
            print(parsed, file=output_file)

def print_help():
    """Prints help text.
    """
    print('''Usage: wikigraph.py -i <inputfile> -o <outputfile>
Processes wikipedia xml dumps into adjecency list of articles.

Available options:
    -i, --ifile=FILE    path to file with dump data, dash (-) means reading
                        from standard input
    -o, --ofile=FILE    path to ouput file, where the adjencency list will be
                        written, dash (-) means writing to standard output
    -h, --help          prints this message''')

def parse_dump(dump_file):
    """This function parses all the articles inside the dump file into internal
    graph representation.

    Args:
        dump_file: xml file with wikipedia dump data

    Returns:
        list of parsed pages
    """
    tree = etree.parse(dump_file)
    pages = []
    # set "default" namespace
    NAMESPACE_MAP['ns'] = tree.getroot().nsmap[None]
    #print(len(tree.findall(".//ns:page", namespaces=NAMESPACE_MAP)))
    for page in tree.findall(".//ns:page", namespaces=NAMESPACE_MAP):
        yield parse_page(page)

def parse_page(page):
    """This function parses article into named tuple.

    Args:
        page: etree.element holding information about single page

    Returns:
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
