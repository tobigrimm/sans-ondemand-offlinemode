#!/usr/bin/env python

import argparse
import sys
import json
import requests


def check_for_python3():
    """
    Check for python3 usage and exit with a warning when running with python2
    """
    if sys.version_info.major == 2:
        print(u"Python 3 \u2665 You. Use It!")
        sys.exit(-1)

check_for_python3()

def parse_json(jsondata):
    coursedata = json.load(jsondata)
    print("Now downloading: %s" % coursedata['course']['name'])
    name = coursedata['course']['name']
    sections = coursedata['course']['childNodes']

    # get chapters
    for section in sections:
        sectionname = section['name']
        print(sectionname)
        subsections = section['childNodes']
        
        for subsection in subsections:

            # should be the same as sectionname
            subsectionname = subsection['name']
            try:
                assert subsectionname == sectionname
            except:
                print("something wen't wrong while parsing, please send the parsed json File to the author")
            
            chapters = subsection['learningObjects']

            for chapter in chapters:
                chapterdata = chapter['metadata']
                chaptername = chapterdata['name']
                chapterduration = chapterdata['durationSeconds']
                chapterbaseurl = chapterdata['baseUrl']
                chaptercookies = chapterdata['cookies']
                print("\tChapter %s:" % chaptername)

                slideurl = chapterbaseurl + "/script.json"


def dump_em_all(link, cookie, useragent):
    # TODO check before downloading if file already exists
    requests.get("http://example.com", headers={ "user-agent": "The Coolest Useragent" })

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="Backup script for SANS On Demand Course material")
    argparser.add_argument("-q", "--quality", choices = ["SD","HD"], default="HD", help="Quality to download the material with from SANS. Available choices are SD and HD")
    argparser.add_argument("-d","--debug",default=False)
    argparser.add_argument("--useragent", default="Mozilla/5.0 (X11; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0")
    argparser.add_argument("-o","--output", default="dumps", metavar="outputdir", help="Directory for the output of the SANS course, default is dumps. Folder will be created if it does not already exist.")
    argparser.add_argument("jsonfile", metavar="jsonfile", help="Dumped jsonfile from the uberRequest on SANS On Demand Player")
    args = argparser.parse_args()
    # paremeters/options
    video_quality = args.quality  # SD or HQ
    json_inputfile = args.jsonfile# json file containing the course info and the cookies needed to download them
    debug_mode = args.debug
    useragent = args.useragent
    outputdir = args.output

    try:
        with open(json_inputfile, "r") as json_input:
            parse_json(json_input)
    except FileNotFoundError as e:
        print("JSON input file %s not found" % json_inputfile)
