ProcessRefFiles.py 

This code can be used to reformat FASTA reference files for use with FusionGeneParser_final.py

Start by downloading FASTA chromosome references for the GRch38 human genome assembly:

https://www.ncbi.nlm.nih.gov/assembly/GCF_000001405.26/

Chromosome 1	CM000663.2	
Chromosome 2	CM000664.2	
Chromosome 3	CM000665.2	
Chromosome 4	CM000666.2	
Chromosome 5	CM000667.2	
Chromosome 6	CM000668.2	
Chromosome 7	CM000669.2	
Chromosome 8	CM000670.2	
Chromosome 9	CM000671.2	
Chromosome 10	CM000672.2	
Chromosome 11	CM000673.2	
Chromosome 12	CM000674.2	
Chromosome 13	CM000675.2	
Chromosome 14	CM000676.2	
Chromosome 15	CM000677.2	
Chromosome 16	CM000678.2	
Chromosome 17	CM000679.2	
Chromosome 18	CM000680.2	
Chromosome 19	CM000681.2	
Chromosome 20	CM000682.2	
Chromosome 21	CM000683.2	
Chromosome 22	CM000684.2	
Chromosome X	CM000685.2	

*If you know which chromosome reference(s) you will be working with, it is okay to only
download those.

Save the references you will be using in one directory. (all files in the same directory)

Run the ProcessRefFiles.py code for each reference file you plan to use.

It will simply ask for the file path, and the chromosome. (1-22, X, or Y)

Once the files have been processed, they are ready for use with FusionGeneParser_final.py