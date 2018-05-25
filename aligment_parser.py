# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
Mulitprocess alignment for MT preprocessing.

Library usage:


Command-line usage:

    ./alignment_parser.py \\
    -s = source file
    -p = target and alignment file
    -o = output file prefix
    -m = master file for analysis (first:first file, second:second file).
    -c = capitalize sentences in first file.
"""
import math
import sys, os, getopt, codecs
from multiprocessing import Process, Queue
import multiprocessing
import re

from polyglot.text import Text

__author__ = "liangss"
__date__ = "2018/3/22"

def merge_bpe(line):
    words = line.split()
    result=""
    indexs={}
    cur_idx = 0
    flag = False
    bpe_count = 0

    for i, word in enumerate(words):
        if flag == True:
            cur_idx -= 1
            #indexs.append(str(i) +'-'+str(cur_idx))
            indexs[i] = cur_idx
            if re.search('@@', word, flags=0):
                result+= word.split('@@')[0]
                bpe_count += 1
            else:
                result += word
                flag = False
        else:
            #indexs.append(str(i) +'-'+str(i-bpe_count))
            indexs[i] = i-bpe_count
            if re.search('@@', word, flags=0):
                result+= ' '+word.split('@@')[0]
                flag = True
                bpe_count += 1
            else:
                result += ' '+word
        cur_idx +=1
    return result.strip(), indexs

def adjusting_indexs(sline, pline, idx_list):
    alignment_idx = []
    sresult, sidx_dict = merge_bpe(sline)
    presult, pidx_dict = merge_bpe(pline)
    for e in idx_list:
        new_sidx = sidx_dict[int(e.split('-')[1])]
        new_pidx = pidx_dict[int(e.split('-')[0])]
        alignment_idx.append(str(new_sidx)+'-'+str(new_pidx))

    return sresult, presult, alignment_idx

def alignment_parse(slines,plines, output, master, capitalize):
    outlines = []
    for sline,pline in zip(slines, plines):
        #process tgtfile
        parray = pline.split('|||')
        idx_list = parray[1].strip().split()
        ptmp = parray[0].strip()
        stmp = sline.strip()

        try:
            stxts, ptxts, pindxs = adjusting_indexs(stmp, ptmp, idx_list)
            stxts = stxts.split()
            ptxts = ptxts.split()

            unk_count = 0
            for indx in pindxs:
                sindex = int(indx.split('-')[0])
                tindex = int(indx.split('-')[1])

                if master == 'second':
                    text = Text(ptxts[tindex],  hint_language_code='en')
                else:
                    text = Text(stxts[sindex],  hint_language_code='en')

                if text.pos_tags[0][1] == 'NOUN' and unk_count <4:
                    stxts[sindex] ='<unk2>'
                    ptxts[tindex] ='<unk2>'
                    unk_count += 1
                elif len(text.entities) > 0 and unk_count<4:
                    stxts[sindex] ='<unk2>'
                    ptxts[tindex] ='<unk2>'
                    unk_count += 1
            post_sline = ' '.join(stxts)
            post_pline = ' '.join(ptxts)
            if capitalize == True:
                outlines.append(capitalize(post_sline)+'\n')
            else:
                outlines.append(post_sline+'\n')
            outlines.append(post_pline+'\n')
        #except IndexError, KeyError as e:
        except :
            print 'Get IndexError skip this line!'
            continue
    fout = open(output,'w')
    fout.writelines(outlines)
    fout.close()

def capitalize(line):
    text = line.split()
    text[0] = text[0][0].upper() + text[0][1:] 

    return ' '.join(text)

def display_usage():
    """\
    Display program usage information.
    """
    print >> sys.stderr, __doc__

if __name__ == '__main__':
    options,workers = {'encoding':'utf-8', 'master':'first','capitalize':False},[]
    try:
        opts, args = getopt.getopt(sys.argv[1:], 's:p:o:h:m:c')
        for opt, arg in opts:
            if opt in ('-s','--sfile'):
                options['sfile'] = arg
            elif opt in ('-o', '--output'):
                options['output'] = arg
            elif opt in ('-p', '--pfile'):
                options['pfile'] = arg
            elif opt in ('-m', '--master'):
                options['master'] = arg
            elif opt in ('-c', '--capitalize'):
                options['capitalize'] = True
            elif opt == '-h':
                display_usage()
                sys.exit()
        slines = open(options['sfile'], 'r').readlines()
        plines = open(options['pfile'], 'r').readlines()

        if len(slines) != len(plines):
            print 'sfile lines must be equal pfile lines!!!'
            sys.exit()

        total_lines = len(slines)

        cpunum = min(total_lines,multiprocessing.cpu_count());
        blines = int(math.ceil(total_lines/cpunum));

        i = 0;
        while i < cpunum:
            sindex = int(i*blines);
            eindex = min((i+1)*blines, total_lines);
            pw = Process(target=alignment_parse, args = (slines[sindex:eindex], plines[sindex:eindex],options['output'] + '.' + str(i),
                options['master'],options['capitalize']), );
            pw.daemon = True;
            pw.start();
            workers.append(pw);
            i = i + 1;

        ##wait all processes is over 
        while True:
            count =0;
            stop = False
            for t in workers:
                if t.is_alive() != True:
                    count = count+1;
                if count == cpunum:
                    stop =True
                    break;
            if stop == True:
                break

        #merge all tmp files to output
        i = 0;
        fout = open(options['output'], 'w')
        #fout= codecs.open(options['output'],'w','utf-8')
        while i < cpunum:
            with open(options['output'] +'.'+ str(i),'r') as fin:
                tmp = fin.readlines()
                fout.writelines(tmp)
            os.remove(options['output']+'.'+str(i))
            i= i+1

        fout.close()

        print 'All things is processed ...'
    except getopt.GetoptError:
        display_usage()
        sys.exit()