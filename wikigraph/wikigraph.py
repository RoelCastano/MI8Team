#!/usr/bin/env python
"""This module processes Wikipedia dump files and extracts links between
articles. Apart from existen of a link, it also captures order of links in a
article as well as its position in article's text. The output can than also be
transformed into a graph.
"""

import re
import getopt
import sys
from os.path import isfile, dirname, join, exists
from os import remove, makedirs
from collections import namedtuple
from subprocess import Popen, PIPE
from lxml import etree
from tqdm import tqdm
from bz2 import BZ2File
import base64

Seed = namedtuple('Seed', ['depth', 'original'])

LINK_PATTERN = re.compile(r'\[\[(.*?)\]\]')
TITLE_PATTERN = re.compile(r'(.*?:)?([^|#]*)?')
NAMESPACE_MAP = {'ns': 'http://www.mediawiki.org/xml/export-0.10/'}
TEXT_DIR = ""


def main(argv):
    """Main function to run the program.

    Args:
        argv: command line arguments
    """

    global TEXT_DIR
    input_name = ''
    output_name = ''
    seed_name = ''
    depth = -1
    try:
        opts, _ = getopt.getopt(argv, "hi:o:s:d:", ["ifile=", "ofile=", "help",
                                                    "seedfile=", "depth="])
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
        elif opt in ("-s", "--seedfile"):
            seed_name = arg
        elif opt in ("-d", "--depth"):
            depth = int(arg)

    if input_name == '' or output_name == '' or seed_name == '' or depth < 0:
        print_help()
        sys.exit(1)

    # create a directory for article texts if it not exists
    TEXT_DIR = join(dirname(output_name), "texts")
    print(TEXT_DIR)
    if not exists(TEXT_DIR):
        makedirs(TEXT_DIR)

    with open(input_name, 'r') as input_file:
        with open(output_name + '.tmp', 'w') as output_file:
            with open(output_name + '.redir', 'w') as redirect_file:
                with open(seed_name, 'r') as seed_file:
                    expand(input_file, seed_file, output_file, redirect_file,
                           depth)

    with open(output_name, 'w') as output_file:
        with open(output_name + '.tmp', 'r') as link_file:
            with open(output_name + '.redir', 'r') as redirect_file:
                resolve_redirects(output_file, link_file, redirect_file)
    # clean up
    # if isfile(output_name + '.tmp'):
    #     remove(output_name + '.tmp')
    # if isfile(output_name + '.redir'):
    #     remove(output_name + '.redir')


def print_help():
    """Prints help text.
    """
    print('''Usage: wikigraph.py -i <inputfile> -s <seedsfile> -o <outputfile> -d <depth>
Processes wikipedia xml dumps into adjecency list of articles.

Available options:
    -i, --ifile=FILE    path to file with dump data, dash (-) means reading
                        from standard input
    -o, --ofile=FILE    path to ouput file, where the adjencency list will be
                        written, dash (-) means writing to standard output
    -s, --seedfile=FILE path to file with seeds to be expanded
    -d, --depth=NUMBER  number of hops to be expanded
    -h, --help          prints this message''')


def expand(input_file, seed_file, output_file, redirect_file, max_depth):
    """Expands seeds to given depth

    Args:
        input_file: file containing paths to files with xml article files
        seed_file: file with seeds to expand
        output_file: file to which links will be written
        redirect_file: file to which redirects will be written
        max_depth: depth of breath first search performed
    """
    seeds_dict = {}
    processed = {}
    for seed in seed_file:
        # remove new line character
        seed = seed.strip()
        seed_casefold = seed.casefold()
        # already with _ instead of spaces
        seeds_dict[seed_casefold] = Seed(depth=0, original=seed)

    # kill switch in case some articles cannot be found and expanded
    # maximum passes has to be 2 * max_depth when every link has to be resolved
    passes = 0
    with tqdm(total=2*(max_depth+1), leave=False, desc='pass') as pbar:
        # while there are seeds to be expaneded
        while seeds_dict and passes < 2 * (max_depth + 1):
            print('seeds:', seeds_dict)
            print('processed:', processed)
            passes += 1
            with tqdm(total=file_len(input_file.name), leave=False, position=1,
                      desc='dump') as pbar2:
                input_file.seek(0)

                # loop through dump files
                for file_name in input_file:
                    # ignore lines startin with # (comments)
                    if file_name[0] == '#':
                        continue
                    with BZ2File(file_name.strip(), 'r') as dump_file:
                        # loop through parsed pages
                        parse_dump(dump_file, output_file, redirect_file,
                                   max_depth, seeds_dict, processed)
                    pbar2.update(1)
            pbar.update(1)


def parse_dump(dump_file, output_file, redirect_file, max_depth, seeds_dict,
               processed):
    """This function parses all the articles inside the dump file into internal
    graph representation.

    Args:
        dump_file: xml file with wikipedia dump data
        output_file: file to which links will be written
        redirect_file: file to which redirects will be written
        max_depth: depth of breath first search performed
        seeds_dict: dictionary of seeds to be expanded
        processed: dictionary of already processed articles
    """
    context = etree.iterparse(dump_file,
                              events=('end', ),
                              tag='{{{ns}}}page'.format(ns=NAMESPACE_MAP['ns'])
                              )
    mod_fast_iter(context, parse_page, output_file, redirect_file, max_depth,
                  seeds_dict, processed)


def parse_page(page, output_file, redirect_file, max_depth, seeds_dict,
               processed):
    """This function parses article/redirect into desired form and writes them
    into files.

    Args:
        page: etree.Element holding information about single page
        output_file: file to which links will be written
        redirect_file: file to which redirects will be written
        max_depth: depth of breath first search performed
        seeds_dict: dictionary of seeds to be expanded
        processed: dictionary of already processed articles
    """
    global TEXT_DIR
    element_title = page.find("./ns:title", namespaces=NAMESPACE_MAP)
    element_text = page.find("./ns:revision/ns:text", namespaces=NAMESPACE_MAP)
    element_redirect = page.find("./ns:redirect", namespaces=NAMESPACE_MAP)

    if element_title is None or\
       (element_text is None and element_redirect is None):
        # not an article or redirect
        return

    title_orig = element_title.text
    # replace characters once
    title = title_orig.replace(' ', '_')
    # case insensitive
    title_casefold = title.casefold()
    # depth of seed (if any)
    depth, original = seeds_dict.get(title_casefold, Seed(depth=None,
                                                          original=None))
    if depth is None:
        print(title_casefold, 'is not a seed')
        return
    else:
        # every "page" has to be processed only once
        del seeds_dict[title_casefold]

    if element_redirect is not None:
        # is redirect
        if original[1:] != title[1:]:
            # casefold match is not enough for redirect (can make problems)
            print('only casefold match with redirect', title, 'is not enough')
            seeds_dict[title_casefold] = Seed(depth=depth, original=original)
            return
        redirect_title = element_redirect.get("title").replace(' ', '_')
        redirect_title_casefold = redirect_title.casefold()
        if title_casefold != redirect_title_casefold:
            # if the redirect is not only because of letter case
            print(title_casefold, redirect_title_casefold, file=redirect_file)

        if redirect_title_casefold not in processed:
            seed_depth, _ = seeds_dict.get(redirect_title_casefold,
                                           Seed(depth=depth, original=''))
            new_seed = Seed(depth=min(depth, seed_depth),
                            original=redirect_title)
            seeds_dict[redirect_title_casefold] = new_seed
        else:
            if processed[redirect_title_casefold] > depth:
                # it is not properly processed (less deep than expected)
                del processed[redirect_title_casefold]
                new_seed = Seed(depth=depth, original=redirect_title)
                seeds_dict[redirect_title_casefold] = new_seed

    else:
        # is article
        # renaming from casefold to correct name
        if title_casefold != title:
            print(title_casefold, title, file=redirect_file)

        if original[1:] != title[1:]:
            print('WARNING! only casefold match for', original, 'and', title)
        # processing the seed
        processed[title_casefold] = depth

        if depth <= 1:
            # save article text
            article_text = element_text.text
            safe_name = base64.urlsafe_b64encode(
                title.encode('utf-8')).decode('utf-8')
            with open(join(TEXT_DIR, safe_name), 'w') as text_file:
                print(article_text, file=text_file)

        order = 0
        for neighbour, position in parse_links(element_text, title_orig):
            order += 1
            neighbour = neighbour.replace(' ', '_')
            neighbour_casefold = neighbour.casefold()
            print(title, neighbour_casefold, order, position, file=output_file)

            if neighbour_casefold not in processed:
                if depth < max_depth:
                    seed_depth, _ = seeds_dict.get(neighbour_casefold,
                                                   Seed(depth=depth+1,
                                                        original=''))
                    new_seed = Seed(depth=min(depth+1, seed_depth),
                                    original=neighbour)
                    seeds_dict[neighbour_casefold] = new_seed
            else:
                if processed[neighbour_casefold] > (depth+1):
                    # it is not properly processed (less deep than expected)
                    del processed[neighbour_casefold]
                    new_seed = Seed(depth=depth+1, original=neighbour)
                    seeds_dict[neighbour_casefold] = new_seed


def parse_links(element_text, current_title):
    """This function parses all the links to other wikipedia articles inside
    the main text body.

    Args:
        text: etree.Element with article text
        current_title: title of the article that is being parsed

    Returns:
        an iterator yielding tuples containing title of referred page and
        position of link in the text
    """
    article_text = element_text.text
    # find all contents of [[ ]] and do not use gready match
    for match in re.finditer(LINK_PATTERN, article_text):
        # find the prefix of link (if theres any) and main link name
        (prefix, title) = re.match(TITLE_PATTERN, match.group(1)).groups()
        if (not prefix) and title.casefold() != current_title.casefold():
            yield (title, match.start())


def resolve_redirects(output_file, link_file, redirect_file):
    """Runs through file with found links and resolves possible redirects.

    Args:
        output_file: file where resolved links will be written
        link_file: file with unresolved links
        redurects_file: file with redirects
    """
    redirect_dict = {}
    for line in redirect_file:
        columns = line.strip().split(' ')
        redirect_dict[columns[0]] = columns[1]

    # resolve multiple redirects/rewrites (like transitive closure)
    for key in redirect_dict.keys():
        value = redirect_dict[key]
        timeout = 0
        while value in redirect_dict and timeout < 1000:
            value = redirect_dict[value]
            timeout += 1
        if timeout >= 1000:
            print('terminating infinite loop, could not resolve', value)
        redirect_dict[key] = value

    with tqdm(total=file_len(link_file.name), leave=False,
              desc='link') as pbar:
        for line in link_file:
            columns = line.strip().split(' ')
            # resolve redirect, if there is any
            columns[1] = redirect_dict.get(columns[1], columns[1])
            print(columns[0], columns[1], columns[2], columns[3],
                  file=output_file, sep='\t')
            pbar.update(1)


def file_len(fname):
    """Computes number of lines in a file.

    Args:
        fname: name of a file

    Returns:
        number of lines in the given file
    """
    p = Popen(['wc', '-l', fname], stdout=PIPE, stderr=PIPE)
    result, err = p.communicate()
    if p.returncode != 0:
        raise IOError(err)
    return int(result.strip().split()[0])


def mod_fast_iter(context, func, *args, **kwargs):
        """
        http://www.ibm.com/developerworks/xml/library/x-hiperfparse/
        Author: Liza Daly
        See also http://effbot.org/zone/element-iterparse.htm
        """
        pbar = tqdm(desc='parsing', leave=False)
        for event, elem in context:
            pbar.update(1)
            # print('Processing {e}'.format(e=etree.tostring(elem)))
            func(elem, *args, **kwargs)
            # It's safe to call clear() here because no descendants will be
            # accessed
            # print('Clearing {e}'.format(e=etree.tostring(elem)))
            elem.clear()
            # Also eliminate now-empty references from the root node to elem
            for ancestor in elem.xpath('ancestor-or-self::*'):
                # print('Checking ancestor: {a}'.format(a=ancestor.tag))
                while ancestor.getprevious() is not None:
                    # print(
                    #   'Deleting {p}'.format(p=(ancestor.getparent()[0]).tag))
                    del ancestor.getparent()[0]
        del context
        pbar.close()


if __name__ == "__main__":
    main(sys.argv[1:])
