from pybam import pybam
from collections import namedtuple
import os
import re
import tkinter
from tkinter import filedialog
root = tkinter.Tk()

import alignment_tester
import alignment_helper

#allow user to select a BAM file
BAMfile = str(filedialog.askopenfilename(parent=root, initialdir=os.getcwd() + "/BAM", filetypes=[("BAM Files", ".bam"), ("All Files", "*")], title='Please select a BAM file'))
#allow user to select their reference file directory
refDir = str(filedialog.askdirectory(parent=root, initialdir=os.getcwd() + "/Chromosome", title='Select your reference file directory')+"/")
#allow user to select a directory for their output text file
fileDir = str(filedialog.askdirectory(parent=root, initialdir=os.getcwd(), title='Where do you want to save your output file?')+"/")

#create collection format for each read
Read = namedtuple("Read",["Name","Chr","Pos","SuppAl","ReadSeq","ReadLen","Cigar","SA_Chr", "SA_Pos", "SA_MAPQ"])

#create array to store reads (makes it easy to reference data in collections)
Reads = []

#iterate over BAM file
for alignment in pybam.read(BAMfile):
    # filter out reads that do not have an alternate alignment
    if "SA:" not in alignment.sam_tags_string:
        continue
    # parses out the SA from sam_tags_string
    head, tail = alignment.sam_tags_string.split("SA:Z:")
    #filter out reads with a MAPQ less than 50
    if alignment.sam_mapq <50:
        continue
    x = alignment.sam_tags_string
    # Divide the tags string by the white space, turns into a list of tags
    x = x.split()
    # Parse through tags for SA information
    for tag in x:
        # Use a regular expression to find the location of the SA, this can vary by read
        SAfinder = re.search("SA:Z:", tag)
        if SAfinder:
            # if the SA is found, then split the tag by the commas
            tag = tag.split(',')
            # parse out SA Chr
            SA_chr = tag[0].split("SA:Z:")[1]
            # parse out SA pos
            SA_pos = tag[1]
            # parse out SA MAPQ
            SA_MAPQ = int(tag[4])
    # check if SA_MAPQ is high enough to be valid
    if SA_MAPQ < 50:
        continue
    else:
        #strip "chr", so that chromosome is only the number or letter (1-22, X, Y)
        chro = alignment.sam_rname.strip("chr")
        #create collection using Read tuple structure for each read
        d = Read(alignment.sam_qname,chro,alignment.sam_pos1,tail,alignment.sam_seq,int(alignment.sam_l_seq),alignment.sam_cigar_string,SA_chr,SA_pos,SA_MAPQ)
        #append each collection to an array (stores them all in one list, while maintaining collection structure)
        Reads.append(d)

#sort alphabetically by read name
Reads.sort()

#create a new text file
with open(fileDir + "parsedreads" + ".txt", 'w') as newfile:
#iterate over read collections stored in array
    for i in Reads:
        #define reference file to use based on read alignment chromosome
        Rfilename = refDir + str(i.Chr) + ".FASTA"
        Rfile = open(Rfilename,'r')
        #in reference file, point to location of alignment start site
        Rfile.read(i.Pos - 1)
        #append information for each read to the new text file
        newfile.write(i.Name + "\n")
        newfile.write(i.Chr + ":" + str(i.Pos) + "\n")
        newfile.write(str(i.ReadLen) + "\n")
        newfile.write(i.Cigar + "\n")
        newfile.write(i.ReadSeq + "\n")
        # append reference sequence to encompass lenght required by the cigar
        cigar_list = alignment_helper.cigarStringToList(i.Cigar)
        length_of_reference_read = alignment_helper.howLongShouldReferenceSequenceBe(cigar_list)
        newfile.write(Rfile.read(length_of_reference_read) + "\n")
        # write character between each read record for easier parsing downstream
        newfile.write(">\n")
newfile.close()

#This is the call to the alignment tester code
alignment_tester.main([newfile.name])
