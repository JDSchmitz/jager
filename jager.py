#!/usr/bin/env python
# encoding: utf-8
"""
jager.py

Created by Scott Roberts.
Copyright (c) 2013 TogaFoamParty Studios. All rights reserved.
"""

from optparse import OptionParser
import re, json, time, hashlib, os
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO

'''
# Setup Logging
import logging
logger = logging.getLogger('default')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# Setup logging to file
fh = logging.FileHandler('default.log')
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)
# Setup logging to console
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)
# Setup logging to syslog
import logging.handlers
sh = logging.handlers.SysLogHandler()
sh.setLevel(logging.DEBUG)
logger.addHandler(sh)

# 'application' code
logger.debug('debug message')
logger.info('info message')
logger.warn('warn message')
logger.error('error message')
logger.critical('critical message')
'''

# Indicators
re_ipv4 = re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
re_email = re.compile("\\b[A-Za-z0-9_.]+@[0-9a-z.-]+\\b", re.I)
re_domain = re.compile("[\w\-\.\_]+\.(am|au|az|br|biz|ca|cn|co|com|de|es|fr|hk|id|in|info|ir|it|jp|kz|me|mx|net|pl|org|ru|se|to|tr|tw|ua|uk|us|uz)\\b", re.I | re.S | re.M)
#"([A-Za-z0-9\.\-]+\.)?[A-Za-z0-9\.\-]+\.(com|net|biz|cat|aero|asia|coop|info|int|jobs|mobi|museum|name|org|post|pre|tel|travel|edu|gov|mil|br|cc|ca|uk|ch|cn|co|cx|it|de|fr|hk|jp|kr|nl|nr|ru|tk|ws|tw|to|uk|pl|sg){1,3}"
# Hashes
re_md5 = re.compile("\\b[a-f0-9]{32}\\b", re.I)
re_sha1 = re.compile("\\b[a-f0-9]{40}\\b", re.I)
re_sha256 = re.compile("\\b[a-f0-9]{64}\\b", re.I)
re_sha512 = re.compile("\\b[a-f0-9]{128}\\b", re.I)
re_ssdeep = re.compile("\\b[0-9]+:[A-Za-z0-9+/]+:[A-Za-z0-9+/]+\\b", re.I)

# File Types
re_doc = '\W([\w-]+\.)(docx|doc|csv|pdf|xlsx|xls|rtf|txt|pptx|ppt)'
re_exe = '\W([\w-]+\.)(exe|dll)'
re_zip = '\W([\w-]+\.)(zip|zipx|7z|rar|tar|gz)'
re_img = '\W([\w-]+\.)(jpeg|jpg|gif|png|tiff|bmp)'
re_flash = '\W([\w-]+\.)(flv|swf)'

def pdf_text_extractor(path):
    '''http://stackoverflow.com/questions/5725278/python-help-using-pdfminer-as-a-library'''

    print "- Extracting: PDF Text"

    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = file(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)
    fp.close()
    device.close()
    str = retstr.getvalue()
    retstr.close()
    return str

    print doc.info

def file_metadata(path):
    print "- Extracting: Source File Metadata"

    hash_sha1 = hashlib.sha1(open(path, 'rb').read()).hexdigest()
    filesize = os.path.getsize(path)
    filename = path.split('/')[-1]

    return {"sha1": hash_sha1, "fileize": filesize, "filename": filename}

def extract_hashes(t):
    print "- Extracting: Hashes"

    md5s = list(set(re.findall(re_md5, t)))
    sha1s = list(set(re.findall(re_sha1, t)))
    sha256s = list(set(re.findall(re_sha256, t)))
    sha512s = list(set(re.findall(re_sha512, t)))
    ssdeeps = list(set(re.findall(re_ssdeep, t)))

    print " - %s MD5s detected." % len(md5s)
    print " - %s SHA1s detected." % len(sha1s)
    print " - %s SHA256s detected." % len(sha256s)
    print " - %s SHA512s detected." % len(sha512s)
    print " - %s ssdeeps detected." % len(ssdeeps)

    return {"md5s": md5s, "sha1s": sha1s, "sha256": sha256s, "sha512": sha512s, "ssdeep": ssdeeps}

def extract_emails(t):
    print "- Extracting: Email Addresses"

    emails = list(set(re.findall(re_email, t)))
    emails.sort()

    print " - %d email addresses detected." % (len(emails))

    return emails

def extract_ips(t):
    print "- Extracting: IPv4 Addresses"

    ips = re.findall(re_ipv4, t)
    ips = list(set(ips))
    ips.sort()

    print " - %d IPv4 addresses detected." % len(ips)

    return {"ipv4addresses": ips, "ipv6addresses": []}

def extract_domains(t):
    print "- Extracting: Domains"

    domains = re.findall(re_domain, t)

    domains_list = list(set(["".join(item) for item in domains]))
    domains_list = [item.lower() for item in domains_list]
    domains_list.sort()

    print " - %d domains detected." % len(domains)

    return domains_list

def extract_urls(t):
    #print "- Extracting: URLS"
    #print " - %d IPv4 addresses detected." % len(ips)
    return []

def extract_filenames(t):
    print "- Extracting: File Names"

    docs = list(set(["".join(doc) for doc in re.findall(re_doc, t)]))
    exes = list(set(["".join(item) for item in re.findall(re_exe, t)]))
    zips = list(set(["".join(item) for item in re.findall(re_zip, t)]))
    imgs = list(set(["".join(item) for item in re.findall(re_img, t)]))
    flashes = list(set(["".join(item) for item in re.findall(re_flash, t)]))

    docs.sort()
    exes.sort()
    zips.sort()
    imgs.sort()
    flashes.sort()

    print " - %s Docs detected." % len(docs)
    print " - %s Executable files detected." % len(exes)
    print " - %s Zip files detected." % len(zips)
    print " - %s Image files detected." % len(imgs)
    print " - %s Flash files detected." % len(flashes)

    return {"documents": docs, "executables": exes, "compressed": zips, "flash": flashes}

def main():

    target = "/Users/scottjroberts/Desktop/PDFs/Pitty Tiger Final Report.pdf"

    # parser = OptionParser(usage="usage: %prog [options] filepath")
    # parser.add_option("-f", "--foo",
    #                   action="store",
    #                   type="string",
    #                   dest="foo_dest",
    #                   default=None,
    #                   help="You picked option foo!")
    # parser.add_option("-b", "--bar",
    #                   action="store",
    #                   type="string",
    #                   dest="bar_dest",
    #                   default=None,
    #                   help="You picked option bar!")
    #
    # (options, args) = parser.parse_args()

    #Uncomment to enforce at least one final argument
    #if len(args) != 1:
        #parser.error("You didn't specify a target path.")
        #return False

    # if options.foo_dest:
    #   print foo()
    # else:
    #   print "Foo Dest: Blank"
    #
    # if options.bar_dest:
    #   print bar()
    # else:
    #   print "Bar Dest: Blank"

    text = pdf_text_extractor(target)

    output = {
        "group_name": [
            "?"
        ],
        "attribution": [
            "?"
        ],
        "indicators": {
            "ips": extract_ips(text),
            "urls": extract_urls(text),
            "domains": extract_domains(text),
            "emails": extract_emails(text)
        },
        "malware": {
            "filenames": extract_filenames(text),
            "hashes": extract_hashes(text)
        },
        "metadata": {
            "report_name": "??",
            "date_analyzed": time.strftime("%Y-%m-%d %H:%M"),
            "source": "??",
            "release_date": "??",
            "authors": [
                "??"
            ],
            "pdf": file_metadata(target)
        }
    }

    #print json.dumps(output, indent=4)

    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print "User aborted."
    except SystemExit:
        pass
    #except:
        #crash()
