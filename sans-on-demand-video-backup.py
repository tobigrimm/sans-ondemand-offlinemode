#!/usr/bin/env python

import argparse
import sys
import json
import requests
import shutil
import re
import os
import mimetypes

def create_dir(dirname):
    """
    Create a folder dirname if it doesn't exist yet
    """
    if not os.path.exists(dirname):
        os.makedirs(dirname)

def check_for_python3():
    """
    Check for python3 usage and exit with a warning when running with python2
    """
    if sys.version_info.major == 2:
        print(u"Python 3 \u2665 You. Use It!")
        sys.exit(-1)

check_for_python3()

def get_valid_filename(filename):
    """
    Get a valid filename from a string.
    Shamelessly stolen from https://github.com/django/django/blob/master/django/utils/text.py
    """
    filename = str(filename).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', filename)

def parse_json(jsondata, videoindex, useragent, outputdir, debug):
    coursedata = json.load(jsondata)
    print("Now downloading: %s" % coursedata['course']['name'])
    name = coursedata['course']['name']
    sections = coursedata['course']['childNodes']


    # create outputdir
    create_dir(outputdir)

    # get chapters
    for sectionnr, section in enumerate(sections):
        sectionname = section['name']
        print(sectionnr, sectionname)
        subsections = section['childNodes']
       
        sectiondir = outputdir + "/"+ get_valid_filename(str(sectionnr)+"_"+sectionname)
        create_dir(sectiondir)
        for subsection in subsections:

            # should be the same as sectionname
            subsectionname = subsection['name']
            try:
                assert subsectionname == sectionname
            except:
                print("something wen't wrong while parsing, please send the parsed json File to the author")
            
            chapters = subsection['learningObjects']

            for chapternr, chapter in enumerate(chapters):
                chapterdata = chapter['metadata']
                chaptername = chapterdata['name']
                chapterduration = chapterdata['durationSeconds']
                chapterbaseurl = chapterdata['baseUrl']
                chaptercookies = chapterdata['cookies']
                print("\tChapter: %s" % chaptername)
                
                # TODO check if theres a proper way of getting dirs without strings (for windows?) 
                chapterdir = sectiondir + "/"+ get_valid_filename(str(chapternr)+"_"+chaptername)
                create_dir(chapterdir)
                slideurl = chapterbaseurl + "/script.json"
                cookies = {c['key']:c['value'] for c in chaptercookies}
                headers = {
                            'User-Agent': useragent,
                          }
                # grab the script.json file for the chapter, 
                #  using the predefined cookies and the configured header
                foo = requests.get(slideurl, cookies=cookies, headers=headers)


                try:
                    slidesjson = foo.json()
                    if debug:
                        # save the script.json into the current chapter folder
                        with open(chapterdir + "/" + 'script.json', 'w', encoding='utf-8') as f:
                                json.dump(slidesjson, f, ensure_ascii=False, indent=4)
                except ValueError as e:
                    print("An error occured loading the json file: %s" % e)
                
                try:
                    #TODO fix!! this somehow breaks currently
                    pass #assert slidesjson['title'] == chaptername # the title should be the same as the chaptername
                except:
                    print("An error occured while getting the slides from %s" % slideurl)
                    print(slidesjson['title'])
                    sys.exit(1)

                for slidenr, slides in enumerate(slidesjson['slides']):
                    slidetitle = slides['title']
                    print("\t\t%s" % slidetitle)

                    slideurl = chapterbaseurl+slides['video'][videoindex]['URI']
                    slidenoteurl = chapterbaseurl+"/notes/%03d" % slidenr + ".html"
                    print(slidenoteurl)
                    print(slideurl)
                    print("starting download")

                    
                    slide_target = get_valid_filename(slidetitle)

                    # TODO where to save the file?
                    # TODO check to see if it exists?
                    # if it exists, print a warning?
                    # TODO add config option to redownload/overwrite
                    # default: ignore existing files (maybe if filesize > 0 bytes?


                    # TODO ignore quizzes and special content?
                    
                    # TODO outputdir -> change to chapter etc, create new folder if it dows not exist
           

                    # TODO outputdir should be a directory path m)

                    #actually download the video files:
                    # download the video files as streaming data to not keep it all in memory:
                    slide_temp_target = chapterdir + "/" + slide_target+".part"

                    resp = requests.get(slideurl, cookies=cookies, headers=headers, stream=True)
                    content_type = resp.headers['content-type']
                    extension = mimetypes.guess_extension(content_type)
                    try:
                        with open(slide_temp_target, 'wb') as f:
                            for chunk in resp.iter_content(chunk_size=1024*1024): 
                                if chunk: 
                                    f.write(chunk)
                    except:
                        print("An error occured while downloading %s" % slideurl) 
                    # Rename the temp download file to the correct name if fully downloaded
                    shutil.move(slide_temp_target, chapterdir + "/" + str(slidenr) + "_" + slide_target + extension)
                    print("Downloaded %s" % slideurl)

                    resp = requests.get(slidenoteurl, cookies=cookies, headers=headers)
                    # save the note for the current slide into the chapter folder next to the slide/video
                    with open(chapterdir + "/" + str(slidenr) + "_" + slide_target + ".html", 'w', encoding='utf-8') as f:
                        f.write(resp.text)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="Backup script for SANS On Demand Course material")
    argparser.add_argument("-q", "--quality", choices = ["SD","HD"], default="HD", help="Quality to download the material with from SANS. Available choices are SD and HD")
    argparser.add_argument("--format", choices=["mp4","webm"], default="mp4", help="Fileformat to dump in")
    argparser.add_argument("-d","--debug",default=False, action='store_true')
    argparser.add_argument("--useragent", default="Mozilla/5.0 (X11; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0")
    argparser.add_argument("-o","--output", default="dumps", metavar="outputdir", help="Directory for the output of the SANS course, default is dumps. Folder will be created if it does not already exist.")
    argparser.add_argument("jsonfile", metavar="jsonfile", help="Dumped jsonfile from the uberRequest on SANS On Demand Player")
    args = argparser.parse_args()

    # TODO maybe add options and parsing logik to give SANS account data 
    # and grab the uberRequest json file automatically

    # paremeters/options
    video_quality = args.quality  # SD or HD
    video_format = args.format # mp4 or webm
    json_inputfile = args.jsonfile# json file containing the course info and the cookies needed to download them
    debug_mode = args.debug
    useragent = args.useragent
    outputdir = args.output

    # quality and movie format:
    # mp4:
    #    SD 480 -> 0
    #    HD 720 -> 1
    # webm:
    #    SD 480 -> 2
    #    HD 720 -> 3
    video_index = 0
    if video_quality == "HD":
        video_index += 1
    if video_format == "webm":
        video_index += 2

    try:
        with open(json_inputfile, "r") as json_input:
            parse_json(json_input, video_index, useragent, outputdir, debug_mode)
    except FileNotFoundError as e:
        print("JSON input file %s not found" % json_inputfile)
