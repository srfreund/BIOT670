from alignment_gui import *

from PySide2.QtWidgets import QApplication

# Logging Configuration!  To disable DEBUG messages, comment out that line
# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# Custom logging format
logging.getLogger().handlers[0].setFormatter(
    logging.Formatter('%(levelname)s %(filename)s %(funcName)s %(lineno)d %(message)s'))

def ParseReadFile(file_name):
    """
    Handle parsed data from fusionGeneParser
    Each alignment entry result is separated by a line with a ">"
    Each alignment entry result contains the following entries
        line1: Name
        line2: read start position : reference start position
        line3: length of read sequence
        line4: cigar string
        line5: read sequence
        line6: reference sequence
        line7: >
    :param file_name: a .txt file that contains each alignment entry result from the .bam file
    :return: a list of AlignmentInfos
    """
    file1 = open(file_name, 'r')
    read_line = "First Line Doesn't Count"
    # We will read the file line by line and store the lines here until we have read an entire alignment result
    # Once we have an entire result, we will process it, store it in the alignment_infos list, and then clear this list.
    current_alignment_info_text = []
    # Completed alignment_infos get stored here
    alignment_infos = []

    # Keep reading until we get a empty string
    while len(read_line) > 0:
        # Get next line from file
        read_line = file1.readline()
        trimmed_line = read_line.rstrip("\n")
        if read_line == "\n":
            logging.warning("Blank line found!  This is not expected.")
        # If the trimmed line is a ">" that means we have finished reading a entry and we should process what we have
        elif trimmed_line == ">":
            debug_msg = ""
            for entry_line in current_alignment_info_text:
                debug_msg += "\n    " + (entry_line if len(entry_line) < 75 else entry_line[0:75] + "...")

            logging.info("ParseReadFile has finished reading one entry" + debug_msg)

            # The first line of each entry is the name
            name = current_alignment_info_text[0]
            # The second line of each entry is the position of the read sequence and the position of the ref sequence
            read_start = int(current_alignment_info_text[1].split(":")[0])
            ref_start = int(current_alignment_info_text[1].split(":")[0])
            # The third line of each entry is the read length.  We don't use this number.
            # The fourth line of each sequence is the cigar string.
            cigar_list = cigarStringToList(current_alignment_info_text[3])
            cigar_list = trimHardClips(cigar_list)
            # The fifth line of each sequence is the read sequence
            read_seq = current_alignment_info_text[4]
            # The sixth line of each sequence is the ref sequence
            ref_seq = current_alignment_info_text[5]

            shaded_areas = cigarListToShadedAreas(cigar_list=cigar_list, ref_seq=ref_seq, read_seq=read_seq)

            ref_alignment_info = HalfAlignmentInfo(shaded_areas=shaded_areas.getShadedRef(),
                                                   seq_padded=shaded_areas.getPaddedRefSeq(), seq=ref_seq,
                                                   start_pos=ref_start, color=Qt.green)
            read_alignment_info = HalfAlignmentInfo(shaded_areas=shaded_areas.getShadedRead(),
                                                    seq_padded=shaded_areas.getPaddedReadSeq(), seq=read_seq,
                                                    start_pos=read_start, color=Qt.red)

            alignment_infos.append(AlignmentInfo(name=name, cigar_list=cigar_list,
                                                 ref_half_alignment_info=ref_alignment_info,
                                                 read_half_alignment_info=read_alignment_info))
            # Clear out the temporary list to get ready for the next result
            current_alignment_info_text = []
        # If the read line isn't empty then store that data for later processing
        elif len(read_line) > 0:
            current_alignment_info_text.append(trimmed_line)

    file1.close()

    logging.info("Finished parsing " + str(len(alignment_infos)) + " alignment infos")

    return alignment_infos


def main(args):
    """
    This displays the alignment results from a file path provided as an argument
    :param args: the path to file with the alignment results
    :return: None
    """
    # Handle args if user gives string or list with a single string
    if isinstance(args, str):
        file_name = args
    elif len(args) == 1:
        file_name = args[0]
    else:
        raise Exception("Alignment tester expects one argument")

    logging.debug("Main function starting with file name " + file_name)

    alignment_infos = ParseReadFile(file_name)

    app = QApplication(sys.argv)

    # This is the line that creates a instance of GraphTester
    window = GraphTester(alignment_infos)
    window.resize(1500, 800)
    window.setWindowTitle("Fusion Gene Alignments")

    window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main(sys.argv[1:len(sys.argv)])


