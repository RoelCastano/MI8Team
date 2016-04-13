#!/usr/bin/env python
"""This module is used to make a graph representation of articles on the
Wikipedia.
"""

import re
import getopt
import sys
from collections import namedtuple
from lxml import etree, objectify
import json

Article = namedtuple('Article', ['id', 'title', 'neighbours'])
Redirect = namedtuple('Redirect', ['id', 'redirect_title'])

LINK_PATTERN = re.compile(r'\[\[(.*?)\]\]')
TITLE_PATTERN = re.compile(r'(.*?:)?([^|#]*)?')
NAMESPACE_MAP = {None: "http://graphml.graphdrawing.org/xmlns",
                 'xsi': "http://www.w3.org/2001/XMLSchema-instance"}
XML_SCHEMA_ATTRIB = '{{{pre}}}schemaLocation'.format(pre=NAMESPACE_MAP['xsi'])
XML_SCHEMA_LOCATION = 'http://graphml.graphdrawing.org/xmlns ' +\
                      'http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd'

def main(argv):
    """Main function to run the program.

    Args:
        argv: command line arguments
    """

    graph_name = ''
    seed_name = ''
    output_name = ''
    runs = -1
    try:
        opts, _ = getopt.getopt(
            argv, "hs:o:p:g:",
            ["seedfile=", "graphfile", "ofile=", "help", "pass="])
    except getopt.GetoptError:
        print_help()
        sys.exit(1)
    for opt, arg in opts:
        if opt == '-h' or opt == '--help':
            print_help()
            sys.exit()
        elif opt in ("-g", "--graphfile"):
            graph_name = arg
        elif opt in ("-s", "--seedfile"):
            seed_name = arg
        elif opt in ("-o", "--ofile"):
            output_name = arg
        elif opt in ("-p", "--pass"):
            runs = int(arg)

    if graph_name == '' or seed_name == '' or output_name == '' or runs < 0:
        print_help()
        sys.exit(1)

    graph_file = open(graph_name, 'r')
    # allow reading form stdin
    if seed_name == '-':
        seed_file = sys.stdin
    else:
        seed_file = open(seed_name, 'r')
    # allow write to stdout
    if output_name == '-':
        output_file = sys.stdout.buffer
    else:
        output_file = open(output_name, 'wb')

    expand_seeds(runs, seed_file, graph_file, output_file)


def print_help():
    """Prints help text.
    """
    print('''Usage: expand_seeds.py -g <graphfile> -s <seedsfile> -o <outputfile>
Processes wikipedia graphml file and expands seed articles into a subgraph.

Available options:
    -p, --pass=NUMBER       how many iterations of expansion will be made
    -g, --graphfile=FILE    path to file with graph data
    -s, --seedfile=FILE     path to file with seeds to expand, dash (-) means 
                            reading from standard input
    -o, --ofile=FILE        path to ouput file, where the resulting graph will
                            be written to, dash (-) means writing to standard
                            output
    -h, --help              prints this message''')

def expand_seeds(runs, seed_file, graph_file, output_file):
    seeds = seed_file.read().splitlines()
    processed = set()

    #print("seeds: ", seeds)

    tree = etree.parse(graph_file) 

    with etree.xmlfile(
        output_file,
        encoding='utf-8',
        close=True,
        buffered=False
    ) as xml_file:
        xml_file.write_declaration()
        with xml_file.element(
            'graphml',
            attrib={XML_SCHEMA_ATTRIB: XML_SCHEMA_LOCATION},
            nsmap=NAMESPACE_MAP
        ):
            with xml_file.element('graph', id="G", edgedefault="directed"):
                for _ in range(runs):
                    if not seeds:
                        break
                    new_seeds = []
                    for element, new_seed in expand(seeds, tree):
                        if new_seed in processed:
                            continue
                        #print("writing element:", etree.tostring(element))
                        xml_file.write(element, pretty_print=True)
                        new_seeds.append(new_seed)
                        processed.add(new_seed)
                    #print("new seeds: ", new_seeds)
                    seeds = new_seeds

def expand(new_seeds, tree):
    # set "default" namespace
    namespace_map = {'ns': tree.getroot().nsmap[None]}
    for element in tree.findall(".//ns:edge", namespaces=namespace_map):
        if element.get('source') in new_seeds:
            # get rid of namespace declarations
            element = etree.Element(element.tag[element.tag.find('}')+1:], attrib=element.attrib)
            yield (element, element.get('target'))

if __name__ == "__main__":
    main(sys.argv[1:])
