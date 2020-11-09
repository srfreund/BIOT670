import os

#allow user to select a reference file
Rfile = input("Enter a FASTA reference file: ")
#allow user to enter the chromosome for that reference
Chr = input("What chromosome reference is this? (1-22, X, or Y): ")
Path = os.path.dirname(Rfile)
#open the reference file and split the first line off
with open(Rfile, 'r') as rfileOG:
    head, tail = rfileOG.read().split('\n', 1)
with open(Rfile, 'w') as rfile:
    rfile.write(tail)
seq = ""
#create array to store reference FASTA sequence
refseq = []
#read the file line by line
with open(Rfile,'r') as final:
    reflines = final.readlines()
    #append each line to the refseq array
    for line in reflines:
        refseq.append(line.strip())
    #combine all lines of reference sequence and convert to string
    seq = "".join(str(elem) for elem in refseq)
#write array contents to new file with correct name

with open(os.getcwd() + "/" + str(Chr) + ".FASTA",'w') as newfile:
    newfile.write(seq)
    newfile.close()



