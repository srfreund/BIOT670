# This Python file uses the following encoding: utf-8
import logging
import re
import sys

# Logging Configuration!  To disable DEBUG messages, comment out that line
# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# Custom logging format
logging.getLogger().handlers[0].setFormatter(
    logging.Formatter('%(levelname)s %(filename)s %(funcName)s %(lineno)d %(message)s'))


class CigarEntry(object):
    """
    CigarEntry struct
    Provides length and cigar type (e.g. 16 M)
    """
    __CigarLength = 0
    __CigarType = "?"

    def __init__(self, cigar_length, cigar_type):
        self.__CigarLength = cigar_length
        self.__CigarType = cigar_type

    def getCigarLength(self):
        return self.__CigarLength

    def getCigarType(self):
        return self.__CigarType

    def __str__(self):
        return str(self.getCigarLength()) + self.getCigarType()


def cigarStringToList(cigar_string):
    """
    Converts the cigar string into an list
    :param cigar_string: the cigar string ( ex: '15H200M1D300M' )
    :return: An list of class CigarEntry
    """

    # use re.findall breaks the cigar into its individual strings with a regex
    regex_results = re.findall("\\d+[A-Z]", cigar_string)

    # Store results of the cigar parse in the list my_cigar as Struct objects
    cigar_result = []

    # parse the cigar
    for result in regex_results:
        x = CigarEntry(int(result[0:len(result) - 1]), result[-1])
        cigar_result.append(x)

    return cigar_result


def trimHardClips(cigar_list):
    """
    Removes the hard clip cigar entries from the front and the back of the list
    :param cigar_list: An list of class CigarEntry
    :return: cigar_list without the leading and trailing hard clips
    """

    # Removes the leading hard clip
    while len(cigar_list) > 0 and cigar_list[0].getCigarType() == "H":
        logging.debug("Removing leading hard clip")
        cigar_list = cigar_list[1:len(cigar_list)]
    # Removes the trailing hard clip
    while len(cigar_list) > 0 and cigar_list[len(cigar_list) - 1].getCigarType() == "H":
        logging.debug("Removing trailing hard clip")
        cigar_list = cigar_list[0:len(cigar_list)]
    # Returns the cigar list without the hard clips on the front and back of the list
    return cigar_list


class ShadedAreasInfo:
    """
    Shaded Areas struct
    Provides shaded areas (for drawing boxes) and padded sequences (for displaying next to boxes)
    """
    __shadedRef = []
    __shadedRead = []
    __paddedRefSeq = ""
    __paddedReadSeq = ""
    def __init__(self, shaded_ref, shaded_read, padded_ref_seq, padded_read_seq):
        self.__shadedRef = shaded_ref
        self.__shadedRead = shaded_read
        self.__paddedRefSeq = padded_ref_seq
        self.__paddedReadSeq = padded_read_seq

    def getShadedRef(self):
        return self.__shadedRef

    def getShadedRead(self):
        return self.__shadedRead

    def getPaddedRefSeq(self):
        return self.__paddedRefSeq

    def getPaddedReadSeq(self):
        return self.__paddedReadSeq


def cigarListToShadedAreas(cigar_list, read_seq, ref_seq) -> ShadedAreasInfo:
    """
    Based on the cigar list this function defines the areas that should be shaded and create a padded read and
    reference string that lines up with the shaded areas (for display in graphical alignment)
    :param cigar_list: A list of class CigarEntry
    :param read_seq: A nucleotide sequence of the raw read data that was used for the alignment (query sequence)
    :param ref_seq: A reference nucleotide sequence that the read sequence was aligned to
    :return: A ShadedAreasInfo containing the following functions
        getShadedRef(): the area that would be shaded on the reference sequence, this is a list where each entry has [0] the
                        start position of the shaded area, and [1] the length of the shaded area (end pos = start + length)
        getShadedRead(): the area that would be shaded on the read sequence, this is a list where each entry has [0] the
                         start position of the shaded area, and [1] the length of the shaded area (end pos = start + length)
        getPaddedRefSeq(): nucleotide sequence padded with white space where there should be gaps based on the cigar_list
        getPaddedReadSeq(): nucleotide sequence padded with white space where there should be gaps based on cigar_list
    """
    # TODO move the descriptions of the ShadedAreasInfo functions into ShadedAreasInfo

    #                        I           N             M
    #                      [0-535]   [535-1035]   [1035-1074]
    # Reference:           ==========              ===========
    # Read/Query/Fusion:              ========================

    #
    # Top one:    Length is 1074. Box from 535+500.  Box 1035+39
    # Bottom one: Length is 1074. Box from 0+535.    Box 1035+39
    # M Match           Exact match of x positions
    #                   Reference Bar:      Shaded
    #                   Reference Sequence: Present
    #                   Read Bar:           Shaded
    #                   Read Sequence:      Present
    # N Alignment gap   Next x positions on ref don’t match
    #                   Reference Bar: Shaded
    #                   Reference Sequence: Present
    #                   Read Bar: Not Shaded
    #                   Read Sequence: Not Present
    # D Deletion        Next x positions on ref don’t match
    #                   Reference Bar: Shaded
    #                   Reference Sequence: Present
    #                   Read Bar: Not Shaded
    #                   Read Sequence: Not Present
    # I Insertion       Next x positions on query don’t match
    #                   Reference Bar: Not Shaded
    #                   Reference Sequence: Not Present
    #                   Read Bar: Shaded
    #                   Read Sequence: Present
    # S Soft Clip       Present in the reference sequence, but not the read
    #                   (so the read sequence is shorter in this case)
    #                   Reference Bar:      Shaded
    #                   Reference Sequence: Present
    #                   Read Bar:           Not Shaded
    #                   Read Sequence:      Present
    # H Hard Clip       Not present in either read or reference sequence
    #                   Reference Bar:      Not Shaded
    #                   Reference Sequence: Not Present
    #                   Read Bar:           Not Shaded
    #                   Read Sequence:      Not Present

    # The shaded areas are lists of entries (each entry is a position and a length) in the example above
    # shaded_ref would equal [[0, 535], [1035, 39]] and shaded_read would equal [[535, 539]]
    #                        I           N             M
    #                      [0-535]   [535-1035]   [1035-1074]
    # Reference:           ==========              ===========
    # Read/Query/Fusion:              ========================
    shaded_ref = []
    shaded_read = []

    # The padded sequences have white spaces in the nucleotide sequence wherever there are gaps, based on the cigar list
    padded_read_seq = ""
    padded_ref_seq = ""

    # These indices keep track of how many nucleotides that have been added to the padded sequence from the reference
    # sequence
    current_ref_position = 0
    current_read_position = 0
    # This index keep track of the length of the shaded areas that are being built
    # It should always be the same length as the padded sequence
    current_shade_position = 0

    # Loops through cigar list and define the areas that should be shaded and
    # Create a padded read and reference string that lines up with the shaded areas (for display)
    for entry in cigar_list:
        # set bool to true if we need to shade the reference sequence
        bool_shade_ref = False
        # set bool to true if we need to shade the read sequence
        bool_shade_read = False
        # set bool to true if we need to add white space to the reference sequence
        bool_pad_ref = False
        # set bool to true if we need to add white space to the read sequence
        bool_pad_read = False

        if entry.getCigarType() == "I":
            # For an insertion, we will shade only the read sequence, and add whitespace to the reference sequence
            bool_shade_read = True
            bool_pad_ref = True
        elif entry.getCigarType() == "N":
            # For an alignment gap, we will shade only the reference sequence, and add whitespace to the read sequence
            bool_shade_ref = True
            bool_pad_read = True
        elif entry.getCigarType() == "M":
            # For a match, we will shade both read and reference sequences
            bool_shade_ref = True
            bool_shade_read = True
        elif entry.getCigarType() == "D":
            # For a deletion, we will shade the only the reference sequence, and add whitespace to the read sequence
            bool_shade_ref = True
            bool_pad_read = True
        elif entry.getCigarType() == "S":
            # For a soft clip, we will shade only the reference sequence
            bool_shade_ref = True
        elif entry.getCigarType() == "H":
            # For a hard clip, we will add whitespace to both the read and reference sequence
            bool_pad_ref = True
            bool_pad_read = True
        else:
            # Raise a exception if a cigar string type is not defined above
            raise Exception("Cigar type of \"" + entry.getCigarType() + "\" is not supported.")

        # Add a shaded area to the reference gene, if appropriate
        if bool_shade_ref:
            shaded_ref_len = len(shaded_ref)
            if (shaded_ref_len > 0 and
                    shaded_ref[shaded_ref_len - 1][0] + shaded_ref[shaded_ref_len - 1][1] == current_shade_position):
                # The sections are contiguous; merge them
                # The new region has the start of the previous, and the length of the previous + length of current
                temp_region = [shaded_ref[shaded_ref_len - 1][0],
                               shaded_ref[shaded_ref_len - 1][1] + entry.getCigarLength()]
                # Remove the previous region
                shaded_ref = shaded_ref[0:shaded_ref_len - 1]
                # Add the new region
                shaded_ref.append(temp_region)
            else:
                # There is no previous contiguous section
                shaded_ref.append([current_shade_position, entry.getCigarLength()])

        # Add a shaded area to the read sequence, if appropriate
        if bool_shade_read:
            shaded_read_len = len(shaded_read)
            if (shaded_read_len > 0 and
                    shaded_read[shaded_read_len - 1][0] + shaded_read[shaded_read_len - 1][
                        1] == current_shade_position):
                # The sections are contiguous; merge them.
                # The new region has the start of the previous, and the length of the previous + length of current
                temp_region = [shaded_read[shaded_read_len - 1][0],
                               shaded_read[shaded_read_len - 1][1] + entry.getCigarLength()]
                # Remove the previous region
                shaded_read = shaded_read[0:shaded_read_len - 1]
                # Add the new region
                shaded_read.append(temp_region)
            else:
                # There is no previous contiguous section
                shaded_read.append([current_shade_position, entry.getCigarLength()])

        current_shade_position += entry.getCigarLength()

        if bool_pad_ref:
            # Pad the reference sequence if appropriate
            ref_seq_addition = (" " * entry.getCigarLength())
            logging.debug("Ref  Pad: " + str(entry.getCigarLength()))
        else:
            # Append this portion of the reference sequence to the padded sequence
            start = current_ref_position
            end = current_ref_position + entry.getCigarLength()
            ref_seq_addition = ref_seq[start:end]
            current_ref_position = end
            logging.debug(
                "Ref  Data[" + str(start) + ", " + str(end) + "]: \"" + ref_seq_addition + "\"")

        padded_ref_seq = padded_ref_seq + ref_seq_addition

        if bool_pad_read:
            # Pad the read sequence if appropriate
            read_seq_addition = (" " * entry.getCigarLength())
            logging.debug("Read Pad: " + str(entry.getCigarLength()))
        else:
            # Append this portion of the read sequence to the padded sequence
            start = current_read_position
            end = current_read_position + entry.getCigarLength()
            read_seq_addition = read_seq[start:end]
            current_read_position = end
            logging.debug("Read Data[" + str(start) + ", " + str(end) + "]: \"" + read_seq_addition + "\"")

        padded_read_seq = padded_read_seq + read_seq_addition

        logging.debug("Processed " + str(entry) + ".  Ref Seq increased by " + str(len(ref_seq_addition)) +
                      ". Read Seq increased by " + str(len(read_seq_addition)) + "\n")

    expected_length = current_shade_position

    # Check for errors
    if expected_length != len(padded_ref_seq) or expected_length != len(padded_read_seq) or \
            current_read_position != len(read_seq) or current_ref_position != len(ref_seq):
        logging.error("The lengths of the padded reference or padded read sequences are not consistent\n" +
                      "Cigar List:                 " + str([str(item) for item in cigar_list]) + "\n"
                      # "Reference Sequence:         " + ref_seq + "\n" +
                      # "Read Sequence:              " + read_seq + "\n" +
                      # "Padded Reference Sequence:  " + padded_ref_seq + "\n" +
                      # "Padded Read Sequence:       " + padded_read_seq + "\n" +
                      "Expected padded length:     " + str(expected_length) + "\n" +
                      "Padded Reference length:    " + str(len(padded_ref_seq)) + " " +
                      ("(okay)" if (len(padded_ref_seq) == expected_length) else "NOT OKAY!") + "\n" +
                      "Padded Read length:         " + str(len(padded_read_seq)) + " " +
                      ("(okay)" if (len(padded_read_seq) == expected_length) else "NOT OKAY!") + "\n" +
                      "Reference length:           " + str(len(ref_seq)) + "\n" +
                      "Number read from reference: " + str(current_ref_position) + " " +
                      ("(okay)" if (current_ref_position == len(ref_seq)) else "NOT OKAY!") + "\n" +
                      "Read length:                " + str(len(read_seq)) + "\n" +
                      "Number read from read:      " + str(current_read_position) + " " +
                      ("(okay)" if (current_read_position == len(read_seq)) else "NOT OKAY!"))

        #raise Exception("Made an error while padding reference or read sequence!")
        length_dif = abs(len(padded_ref_seq) - len(padded_read_seq))
        if len(padded_ref_seq) > len(padded_read_seq):
         padded_read_seq = padded_read_seq + ("?" * length_dif)
        else:
            padded_ref_seq = padded_ref_seq + ("?" * length_dif)

    return ShadedAreasInfo(shaded_ref=shaded_ref, shaded_read=shaded_read, padded_ref_seq=padded_ref_seq,
                           padded_read_seq=padded_read_seq)


def howLongShouldReferenceSequenceBe(cigar_list) -> int:
    """
    Based on the cigar string, figures out how many nucleotides we need to pull from the reference sequence
    :param cigar_list: a list of cigar entries
    :return: the number of nucleotides needed to pull from the reference sequence
    """
    total_count = 0

    for entry in cigar_list:
        if entry.getCigarType() == "I":
            bool_should_count = False
        elif entry.getCigarType() == "N":
            bool_should_count = True
        elif entry.getCigarType() == "M":
            bool_should_count = True
        elif entry.getCigarType() == "D":
            bool_should_count = True
        elif entry.getCigarType() == "S":
            bool_should_count = True
        elif entry.getCigarType() == "H":
            bool_should_count = False
        else:
            # Raise a exception if a cigar string type is not defined above
            raise Exception("Cigar type of \"" + entry.getCigarType() + "\" is not supported.")

        if bool_should_count:
            total_count = total_count + entry.getCigarLength()
    return total_count


class HalfAlignmentInfo(object):
    """
    Contains enough information to draw one nucleotide sequence
    """
    __ShadedAreas = []
    __SeqPadded = ""
    __Seq = ""
    __StartPos = 0
    __Color = None
    __SeqLen = 0
    __SeqPaddedLen = 0

    def __init__(self, shaded_areas, seq_padded, seq, start_pos, color):
        self.__ShadedAreas = shaded_areas
        self.__SeqPadded = seq_padded
        self.__Seq = seq
        self.__StartPos = start_pos
        self.__Color = color
        self.__SeqLen = len(seq)
        self.__SeqPaddedLen = len(seq_padded)

    def getShadedAreas(self):
        return self.__ShadedAreas

    def getSeqPadded(self):
        return self.__SeqPadded

    def getSeq(self):
        return self.__Seq

    def getStartPos(self):
        return self.__StartPos

    def getColor(self):
        return self.__Color

    def getSeqLen(self):
        return self.__SeqLen

    def getSeqPaddedLen(self):
        return self.__SeqPaddedLen


class AlignmentInfo(object):
    """
    Contains enough information to show the comparison of two nucleotide sequences
    """
    __CigarList = []
    __Name = ""

    __ReadInfo = None
    __RefInfo = None

    def __init__(self, name, cigar_list, ref_half_alignment_info, read_half_alignment_info):
        self.__Name = name
        self.__CigarList = cigar_list

        self.__RefInfo = ref_half_alignment_info
        self.__ReadInfo = read_half_alignment_info

    def getName(self):
        return self.__Name

    def getCigarList(self):
        return self.__CigarList

    def getRefInfo(self):
        return self.__RefInfo

    def getReadInfo(self):
        return self.__ReadInfo
