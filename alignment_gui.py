# This Python file uses the following encoding: utf-8
import math

import PySide2
from PySide2.QtCore import QRect
from PySide2.QtGui import QPainter, QBrush, QPen, QFont, Qt
from PySide2.QtWidgets import QMainWindow, QFrame, QVBoxLayout, QHBoxLayout, \
    QSizePolicy, QPushButton, QScrollArea, QLabel

from alignment_helper import *
from typing import List

# Logging Configuration!  To disable DEBUG messages, comment out that line
# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# Custom logging format
logging.getLogger().handlers[0].setFormatter(
    logging.Formatter('%(levelname)s %(filename)s %(funcName)s %(lineno)d %(message)s'))


class NucleotideFrame(QFrame):
    """
    This class shows the nucleotide sequence in a QFrame
    It automatically adjusts the size of the sequence based off of the QFrame
    """
    __alignmentInfo = None
    __verticalTextAlignment = Qt.AlignVCenter

    def __init__(self, half_alignment_info):
        """
        This is a constructor
        :param half_alignment_info: Contains enough information to draw one nucleotide sequence
        """
        QFrame.__init__(self)

        if not isinstance(half_alignment_info, HalfAlignmentInfo):
            raise TypeError("NucleotideFrame requires a HalfAlignmentInfo.  You provided a " +
                            str(type(half_alignment_info)))

        self.__alignmentInfo = half_alignment_info

        # The height and size of the bar is set in pixels
        self.setMaximumHeight(25)
        self.setMinimumSize(0, 25)

    def getAlignmentInfo(self):
        """
        Gets the alignment information used to draw this NucleotideFrame
        :return: The HalfAlignmentInfo used to draw this NucleotideFrame
        """
        return self.__alignmentInfo

    def getVerticalTextAlignment(self) -> PySide2.QtCore.Qt.AlignmentFlag:
        """
        Get the vertical text alignment preference, which is used to align the nucleotide sequence display
        :return: The vertical alignment preference (Qt.AlignTop, Qt.AlignBottom, or Qt.AlignVCenter)
        """
        return self.__verticalTextAlignment

    def setVerticalTextAlignment(self, vertical_text_alignment: PySide2.QtCore.Qt.AlignmentFlag):
        """
        Set the vertical text alignment preference, which is used to align the nucleotide sequence display
        :param vertical_text_alignment: Qt.AlignTop, Qt.AlignBottom, or Qt.AlignVCenter
        :return: None
        """
        if (vertical_text_alignment == Qt.AlignTop) or \
                (vertical_text_alignment == Qt.AlignBottom) or \
                (vertical_text_alignment == Qt.AlignVCenter):
            self.__verticalTextAlignment = vertical_text_alignment
        else:
            raise Exception("Only AlignTop, AlignBottom, or AlignVCenter are allowed")

    def paintEvent(self, arg__1: PySide2.QtGui.QPaintEvent):
        """
        PaintEvent draws the contents of this QFrame when called upon
        :param arg__1: the QPaintEvent object that the framework provides
        :return: None
        """

        # The QPaintEvent includes a rectangle (x, y, width, height) that tells us the area we need to draw
        start_drawing_x = arg__1.rect().x()
        stop_drawing_x = start_drawing_x + arg__1.rect().width()
        # We have to paint the area from start_drawing_x until stop_drawing_x

        total_width = self.width()
        sequence_length = self.getAlignmentInfo().getSeqPaddedLen()
        # Width_per_nucleotide is the total width in pixels of this QFrame divided by the sequence length
        width_per_nucleotide = float(total_width) / float(sequence_length)
        # Convert to a integer because this is how wide we will make each letter and we can't draw partial pixels
        width_per_nucleotide_int = math.floor(width_per_nucleotide)
        # We are zoomed in enough to see the nucleotide when we have at least three pixels per nucleotide
        big_enough_to_see = width_per_nucleotide > 3
        if big_enough_to_see:
            if width_per_nucleotide_int < 10:
                font_size = 0.9 * width_per_nucleotide_int
            elif width_per_nucleotide_int < 12:
                font_size = 0.75 * width_per_nucleotide_int
            elif width_per_nucleotide_int < 14:
                font_size = 0.7 * width_per_nucleotide_int
            else:
                font_size = 0.7 * width_per_nucleotide_int

            font_size = math.floor(font_size)

            # Starting sequence index is the index of the first nucleotide on the left of the area we need to draw
            starting_sequence_index = start_drawing_x / width_per_nucleotide
            starting_sequence_index = math.floor(starting_sequence_index)
            # Ending sequence index is the index of the last nucleotide on the right of the area we need to draw
            ending_sequence_index = stop_drawing_x / width_per_nucleotide
            ending_sequence_index = math.ceil(ending_sequence_index)

            # Create the object which can draw letters for us
            painter = QPainter(self)
            painter.setFont(QFont("SansSerif", font_size))
            # This tells the painter where to draw the letter within the rectangle we give it
            text_alignment_preference = self.getVerticalTextAlignment() | Qt.AlignHCenter
            # This contains all of the nucleotides
            padded_seq = self.getAlignmentInfo().getSeqPadded()

            # This loops through all of the nucleotides we need to draw
            for sequence_index in range(starting_sequence_index, ending_sequence_index):
                x = sequence_index * width_per_nucleotide
                # Rounding down (x + 0.5) rounds to the nearest whole number
                x = math.floor(x + 0.5)
                # The rect is the area the the painter is allowed to draw in, we subtract 1 from the start and two from
                # the height to give us padding
                rect = QRect(x, 1, width_per_nucleotide_int, self.height() - 2)
                # This draws a letter (nucleotide)
                painter.drawText(rect, text_alignment_preference, padded_seq[sequence_index])


class BarFrame(QFrame):
    """
    The QFrame that draws a single nucleotide alignment bar (typically two of these are used together)
    """
    __alignmentInfo = None
    __rectangleOutlineColor = Qt.black

    def __init__(self, half_alignment_info):
        """
        This is a constructor
        :param half_alignment_info: Contains enough information to draw one bar that represents the nucleotide sequence
        """
        QFrame.__init__(self)

        if not isinstance(half_alignment_info, HalfAlignmentInfo):
            raise TypeError("BarFrame requires a HalfAlignmentInfo.  You provided a " + str(type(half_alignment_info)))

        self.__alignmentInfo = half_alignment_info

        # The height and size of the bar is set in pixels
        self.setMaximumHeight(20)
        self.setMinimumSize(0, 20)
        # self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def getAlignmentInfo(self):
        """
        Gets the alignment information used to draw this NucleotideFrame
        :return: The HalfAlignmentInfo used to draw this NucleotideFrame
        """
        return self.__alignmentInfo

    def paintEvent(self, arg__1: PySide2.QtGui.QPaintEvent):
        """
        PaintEvent draws the contents of this QFrame when called upon
        :param arg__1: the QPaintEvent object that the framework provides
        :return: None
        """
        painter = QPainter(self)
        # The QPaintEvent includes a rectangle (x, y, width, height) that tells us the area we need to draw
        start_drawing_x = arg__1.rect().x()
        stop_drawing_x = start_drawing_x + arg__1.rect().width()
        # We have to paint the area from start_drawing_x until stop_drawing_x
        # The painter uses the pen to draw the rectangle outline
        painter.setPen(QPen(self.__rectangleOutlineColor, 0, Qt.NoPen))
        # The painter uses the brush to fill the rectangle
        painter.setBrush(QBrush(self.getAlignmentInfo().getColor()))

        pixels_per_nucleotide = (float(self.width()) / float(self.getAlignmentInfo().getSeqPaddedLen()))

        for shaded_area in self.getAlignmentInfo().getShadedAreas():
            # It loops over every shaded area

            # For this shaded area we should shade starting from index nucleotide_start for a width of nucleotide_width
            # These are measured in nucleotides
            nucleotide_start = shaded_area[0]
            nucleotide_width = shaded_area[1]

            logging.debug("Processing shaded area " + str(nucleotide_start) + ":" + str(nucleotide_width))

            # The relative_start, _width, _end are measured in pixels
            relative_start = nucleotide_start * pixels_per_nucleotide
            relative_width = nucleotide_width * pixels_per_nucleotide
            relative_end = relative_start + relative_width

            # If the rectangle is completely to the left of the area to be painted, just skip to the next one
            if relative_start < start_drawing_x and relative_end < start_drawing_x:
                logging.debug("Not drawing because " + str(relative_start) + " - " + str(relative_end) +
                              " is to the left of the visible area")
                continue
            # Elif the rectangle is completely to the right of the area to be painted, we're done
            elif relative_start > stop_drawing_x and relative_end > stop_drawing_x:
                logging.debug("Not drawing because " + str(relative_start) + " - " + str(relative_end) +
                              " is to the right of the visible area")
                break
            else:
                logging.debug("Drawing " + str(relative_start) + " - " + str(relative_end) +
                              " because it's in the visible area")

                # Start drawing from the greater of the start of the rectangle, or the start of the visible area
                relative_start = max(relative_start, start_drawing_x)
                # Stop drawing at the lesser of the end of the rectangle, or the end of the visible area
                relative_end = min(relative_end, stop_drawing_x)
                # Adjust the width (in case start/end changed above)
                relative_width = relative_end - relative_start

                painter.drawRect(relative_start, 0, relative_width, self.height())


class BarFrameStacker(QFrame):
    """
    The BarFrameStacker stacks four items vertically: two nucleotide frames and two bar frames
    """
    __bioFrames = None
    __alignmentInfo = None
    __sequenceLength = 0

    def __init__(self, alignment_info):
        """
        Constructor
        :param alignment_info: the alignment information
        """
        QFrame.__init__(self)

        if not isinstance(alignment_info, AlignmentInfo):
            raise TypeError("BarFrameStacker requires an AlignmentInfo.  You provided a " + str(type(alignment_info)))

        self.__alignmentInfo = alignment_info
        self.__sequenceLength = alignment_info.getRefInfo().getSeqPaddedLen()

        self.__bioFrames = []

        # Make the display components for the reference sequence
        bar_frame_ref = BarFrame(alignment_info.getRefInfo())
        nucleotide_frame_ref = NucleotideFrame(alignment_info.getRefInfo())
        # Align text to bottom so that the text is close to the bar frame (since the nucleotide frame goes above it)
        nucleotide_frame_ref.setVerticalTextAlignment(Qt.AlignBottom)

        # Make the display components for the read sequence
        bar_frame_read = BarFrame(alignment_info.getReadInfo())
        nucleotide_frame_read = NucleotideFrame(alignment_info.getReadInfo())
        # Align text to top so that the text is close to the bar frame (since the nucleotide frame goes below it)
        nucleotide_frame_read.setVerticalTextAlignment(Qt.AlignTop)

        # This is what the display is going to look like
        self.__bioFrames.append(nucleotide_frame_ref)
        self.__bioFrames.append(bar_frame_ref)
        self.__bioFrames.append(bar_frame_read)
        self.__bioFrames.append(nucleotide_frame_read)

        box_layout = QVBoxLayout()
        box_layout.setAlignment(Qt.AlignTop)
        # Count the minimum and max hieghts of our sub components to determine our min and max heights
        min_height = 20
        max_height = 2
        min_width = 10
        # No max width; this thing can get wide

        for subcomponent in self.__bioFrames:
            min_height += subcomponent.minimumHeight() + 2
            max_height += subcomponent.maximumHeight() + 2
            min_width = max(min_width, subcomponent.minimumWidth())
            # Add widget to the layout
            box_layout.addWidget(subcomponent, stretch=0)

        self.setMaximumHeight(max_height)
        self.setMinimumSize(min_width, min_height)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.setLayout(box_layout)

    def setZoomLevel(self, zoom_level):
        """
        Adjusts the width of this stacker so each nucleotide is as wide as the number of pixels specified by zoom_level
        :param zoom_level: the desired width of each nucleotide in pixels
        :return: None
        """
        # The difference in size between this QFrame and the ones it contains. (So basically the padding.)
        size_difference = self.width() - self.__bioFrames[0].width()
        self.resize(zoom_level * self.__sequenceLength, self.height())

        # I noticed that the QVBoxLayout doesn't correctly size its members above a width of > 500,000 ish.
        for sub_component in self.__bioFrames:
            sub_component.resize(self.width() - size_difference, sub_component.height())

    def suggestZoomLevel(self, desired_width):
        """
        Calculates the needed zoom level so the stacker will have the width provided as an argument
        :param desired_width: the desired width in pixels
        :return: the suggested zoom level
        """
        if desired_width < 1:
            raise ValueError("Desired size in pixels must be a positive number.  Received " + str(desired_width))
        return float(desired_width) / self.__sequenceLength

    def getSequenceLength(self):
        """
        Returns the length of the sequence in units of nucleotides
        :return: the length of the sequence in units of nucleotides
        """
        return self.__sequenceLength


class BarFrameStackerScrollArea(QScrollArea):
    """
    This contains a bar frame stacker and handles all zooming functionality
    """
    __bar_frame_stacker = None
    # A zoom level is the number of pixels per nucleotide, zoom level list is shown below
    __zoomLevels = [1 / 100,
                    1 / 80,
                    1 / 60,
                    1 / 40,
                    1 / 30,
                    1 / 20,
                    1 / 15,
                    1 / 10,
                    1 / 7,
                    1 / 4,
                    1 / 3,
                    1 / 2,
                    2 / 3,
                    # From this point, zoom levels are typically 1.3x the previous level
                    3 / 4,
                    1,
                    1.3,
                    1.7,
                    2.2,
                    2.85,
                    3.7,
                    4.8,
                    6.2,
                    8.1,
                    10.5,
                    13.6,
                    17.7,
                    23]
    __currentZoomLevelIndex = 0

    def __init__(self, bar_frame_stacker: BarFrameStacker):
        """
        Makes a BarFrameStackerScrollArea
        :param bar_frame_stacker: is a BarFrameStacker
        """
        QScrollArea.__init__(self)
        self.__bar_frame_stacker = bar_frame_stacker
        self.setWidget(self.__bar_frame_stacker)
        self.setWidgetResizable(False)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # 18 is an estimate for the height of the scroll bar
        self.setMinimumHeight(bar_frame_stacker.minimumHeight() + 18)
        self.setMaximumHeight(bar_frame_stacker.minimumHeight() + 18)

    def getCurrentZoomLevel(self):
        """
        Provides current zoom level
        :return: current zoom level
        """
        return self.__zoomLevels[self.__currentZoomLevelIndex]

    def zoomIn(self, x_position_to_lock=False):
        """
        Zooms in to make the displayed nucleotide comparison larger.  Ensures that the nucleotide at location
        x_position_to_lock remains at that location after zooming.
        :param x_position_to_lock: A position (in pixels) on the display that should remain fixed when zooming
        :return: None
        """
        if x_position_to_lock is False:
            # If the x_position is not provided, default to the center
            x_position_to_lock = self.width() / 2.0

        if self.__currentZoomLevelIndex + 1 < len(self.__zoomLevels):
            self.__currentZoomLevelIndex = self.__currentZoomLevelIndex + 1
            self.__fixPositionAndInitiateResize(x_position_to_lock)

    def zoomOut(self, x_position_to_lock=False):
        """
        Zooms out to make the displayed nucleotide comparison smaller.  Ensures that the nucleotide at location
        x_position_to_lock remains at that location after zooming.
        :param x_position_to_lock: A position (in pixels) on the display that should remain fixed when zooming
        :return: None
        """
        # If the x_position is not provided, default to the center
        if x_position_to_lock is False:
            x_position_to_lock = self.width() / 2.0

        # This tells you if you can and should zoom out and gives a suggestion for a good zoom level
        if self.__currentZoomLevelIndex > 0 \
                and self.getCurrentZoomLevel() > self.__bar_frame_stacker.suggestZoomLevel(self.viewport().width()):
            self.__currentZoomLevelIndex = self.__currentZoomLevelIndex - 1
            self.__fixPositionAndInitiateResize(x_position_to_lock)

    def scroll_start(self):
        """
        Sets the scroll bar all the way to the start (left)
        :return: None
        """
        self.horizontalScrollBar().setSliderPosition(self.horizontalScrollBar().minimum())

    def scroll_forward(self):
        """
        Moves the scroll bar to the right by one quarter of the width of the display
        :return: None
        """
        slider_start_pos = self.horizontalScrollBar().sliderPosition()
        slider_max = self.horizontalScrollBar().maximum()
        slider_forward_final_pos = slider_start_pos + (self.width() / 4)
        # Don't go past the maximum slider value
        self.horizontalScrollBar().setSliderPosition(min(slider_max, slider_forward_final_pos))

    def scroll_backward(self):
        """
        Moves the scroll bar to the left by one quarter of the width of the display
        :return: None
        """
        slider_start_pos = self.horizontalScrollBar().sliderPosition()
        slider_min = self.horizontalScrollBar().minimum()
        slider_backward_final_pos = slider_start_pos - (self.width() / 4)
        # Don't go past the minimum slider value
        self.horizontalScrollBar().setSliderPosition(max(slider_min, slider_backward_final_pos))

    def scroll_end(self):
        """
        Sets the scroll bar all the way to the end (right)
        :return: None
        """
        self.horizontalScrollBar().setSliderPosition(self.horizontalScrollBar().maximum())

    def __fixPositionAndInitiateResize(self, x_position_to_lock):
        """
        You must adjust this objects zoom level before calling this function for it to have an affect
        This function adjusts the width of the BarFrameStacker to match the zoom level
        :param x_position_to_lock: A position (in pixels) on the display that should remain fixed when zooming
        :return: None
        """

        logging.debug("Current Zoom Level: " + str(self.getCurrentZoomLevel()))

        if x_position_to_lock < 0 or x_position_to_lock > self.width():
            raise ValueError("The x Position to lock was invalid.  The value must be between 0 and the width of " +
                             "the scroll area, inclusive.  [0, " + str(self.width()) + "].  You provided " +
                             str(x_position_to_lock))

        # This is how many pixels are to the left of the viewable area
        slider_start_pos = self.horizontalScrollBar().sliderPosition()
        # This is the width of the frame that's inside the scroll area
        bar_frame_width = self.__bar_frame_stacker.width()

        mouse_pos_relative_to_scroll_area = x_position_to_lock
        mouse_pos_relative_to_bar_frame = slider_start_pos + mouse_pos_relative_to_scroll_area
        # This is the center position of the screen relative to the width of the bar_frame (percentage)
        mouse_pos_relative_to_bar_frame_percent = float(mouse_pos_relative_to_bar_frame) / float(bar_frame_width)

        self.__bar_frame_stacker.setZoomLevel(self.getCurrentZoomLevel())

        # Now that we have zoomed in, it's time to set the slider so that the screen is still centered on where it was
        new_bar_frame_width = self.__bar_frame_stacker.width()
        if new_bar_frame_width != bar_frame_width:
            # The mouse position relative to the bar frame PERCENT must stay the same.
            # the slider position is the number of pixels that are hidden to the left
            new_mouse_pos_relative_to_bar_frame = mouse_pos_relative_to_bar_frame_percent * new_bar_frame_width
            new_slider_start_pos = new_mouse_pos_relative_to_bar_frame - mouse_pos_relative_to_scroll_area

            # If our new position is outside of the allowed scroll bar area, then use minimum or maximum value
            new_slider_start_pos = max(new_slider_start_pos, self.horizontalScrollBar().minimum())
            new_slider_start_pos = min(new_slider_start_pos, self.horizontalScrollBar().maximum())

            self.horizontalScrollBar().setSliderPosition(new_slider_start_pos)
        else:
            # This variable must be initialized to fix a PyCharm warning
            new_mouse_pos_relative_to_bar_frame = None
            new_slider_start_pos = None

        # There is a bug, where if the width of the bar frame is more than 170 pixels per nucleotide,
        # then zooming is pretty inaccurate.  Not sure why. The bar frame should never be allowed to
        # get that wide, anyway.
        logging.debug("slider_start_pos                        " + str(slider_start_pos))
        logging.debug("bar_frame_width                         " + str(bar_frame_width))
        logging.debug("mouse_pos_relative_to_scroll_area       " + str(mouse_pos_relative_to_scroll_area))
        logging.debug("mouse_pos_relative_to_bar_frame         " + str(mouse_pos_relative_to_bar_frame))
        logging.debug("mouse_pos_relative_to_bar_frame_percent " + str(mouse_pos_relative_to_bar_frame_percent))
        logging.debug("new_mouse_pos_relative_to_bar_frame     " + str(new_mouse_pos_relative_to_bar_frame))
        logging.debug("new_slider_start_pos                    " + str(new_slider_start_pos) + "\n")

        self.update()

    def wheelEvent(self, event: PySide2.QtGui.QWheelEvent):
        """
        Handles the mouse wheel event and call the bar frame stacker zoom events
        :param event: QWheelEvent
        :return: None
        """
        # delta is how much the wheel has moved
        if event.delta() > 0:
            self.zoomIn(event.pos().x())
        elif event.delta() < 0:
            self.zoomOut(event.pos().x())
        else:
            logging.debug("Not zooming in or out because wheelEvent is neither positive nor negative.")

        # Setting the event to accepted prevents other components from receiving the event
        event.setAccepted(True)


class ZoomButtons(QFrame):
    """
    Creates a frame with a plus and minus button, and it calls the provided functions when the buttons are clicked
    """
    __zoomInFunction = None
    __zoomOutFunction = None

    def __init__(self, zoom_in_function, zoom_out_function):
        """
        Constructor
        :param zoom_in_function: the function called when the plus button is clicked
        :param zoom_out_function: the function called when the minus button is clicked
        """
        QFrame.__init__(self)
        button_zoom_in = QPushButton()
        button_zoom_in.clicked.connect(zoom_in_function)
        button_zoom_in.setText("+")

        button_zoom_out = QPushButton()
        button_zoom_out.clicked.connect(zoom_out_function)
        button_zoom_out.setText("-")

        box_layout2 = QHBoxLayout()
        box_layout2.addWidget(button_zoom_in)
        box_layout2.addWidget(button_zoom_out)

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setMinimumSize(70, 20)
        self.setMaximumSize(150, 50)
        self.resize(100, 30)
        self.setLayout(box_layout2)


class ScrollButtons(QFrame):
    """
    Creates a frame with start, backward, forward, and end buttons
    It calls the provided functions when the buttons are clicked
    """
    __scrollToStartFunction = None
    __scrollBackwardFunction = None
    __scrollForwardFunction = None
    __scrollToEndFunction = None

    def __init__(self, start_function, backward_function, forward_function, end_function):
        """
        Constructor
        :param start_function: the function called when the "<<" button is clicked
        :param backward_function: the function called when the "<" button is clicked
        :param forward_function: the function called when the ">" button is clicked
        :param end_function: the function called when the ">>" button is clicked
        """
        QFrame.__init__(self)
        button_start = QPushButton()
        button_start.clicked.connect(start_function)
        button_start.setText("<<")

        button_backward = QPushButton()
        button_backward.clicked.connect(backward_function)
        button_backward.setText("<")

        button_forward = QPushButton()
        button_forward.clicked.connect(forward_function)
        button_forward.setText(">")

        button_end = QPushButton()
        button_end.clicked.connect(end_function)
        button_end.setText(">>")

        box_layout2 = QHBoxLayout()
        box_layout2.addWidget(button_start)
        box_layout2.addWidget(button_backward)
        box_layout2.addWidget(button_forward)
        box_layout2.addWidget(button_end)

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setMinimumSize(140, 20)
        self.setMaximumSize(300, 50)
        self.resize(200, 30)
        self.setLayout(box_layout2)


class CompleteComparisonFrame(QFrame):
    """
    Creates a QFrame that shows a alignment based on the information provided to the constructor
    This combines the BarFrameStackerScrollArea, the ZoomButtons, the ScrollButtons, and a title label
    """

    def __init__(self, alignment_info: AlignmentInfo):
        """
        Constructor
        :param alignment_info: The AlignmentInfo to Display
        """
        QFrame.__init__(self)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        title_label = QLabel(alignment_info.getName())
        title_label.setFont(QFont("SansSerif", 16))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setMinimumHeight(20)
        stacker = BarFrameStacker(alignment_info)
        scroll_thing = BarFrameStackerScrollArea(stacker)
        zoom_thing = ZoomButtons(scroll_thing.zoomIn, scroll_thing.zoomOut)
        scroll_button_thing = ScrollButtons(scroll_thing.scroll_start, scroll_thing.scroll_backward,
                                            scroll_thing.scroll_forward, scroll_thing.scroll_end)

        blank_space = QFrame()
        all_the_buttons = QFrame()

        button_layout = QHBoxLayout()
        button_layout.addWidget(zoom_thing, stretch=1)
        button_layout.addWidget(blank_space)
        button_layout.addWidget(scroll_button_thing, stretch=2)
        all_the_buttons.setLayout(button_layout)

        box_layout3 = QVBoxLayout()
        box_layout3.addWidget(title_label)
        box_layout3.addWidget(scroll_thing, stretch=1)
        box_layout3.addWidget(all_the_buttons, stretch=1)

        self.setLayout(box_layout3)

        # The below is a very bad way to appropriately size the bar graph on initialization
        # This zooms in until you can't zoom in anymore
        # TODO - Make a nicer way to do this
        prev_zoom_level = 0
        while scroll_thing.getCurrentZoomLevel() != prev_zoom_level:
            prev_zoom_level = scroll_thing.getCurrentZoomLevel()
            scroll_thing.zoomIn()
        # This zooms out until you can't zoom  out anymore
        # This will not zoom out more than it should
        prev_zoom_level = 0
        while scroll_thing.getCurrentZoomLevel() != prev_zoom_level:
            prev_zoom_level = scroll_thing.getCurrentZoomLevel()
            scroll_thing.zoomOut()


class CompleteComparisonFrameStacker(QFrame):
    """
    Creates a QFrame that holds multiple CompleteComparisonFrames in a vertical box layout
    """

    def __init__(self, alignment_info_list: List[AlignmentInfo]):
        """
        Once complete CompleteComparisonFrame is made per AlignmentInfo
        :param alignment_info_list: A list of AlignmentInfos to display
        """
        QFrame.__init__(self)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        box_layout = QVBoxLayout()
        for alignment_info in alignment_info_list:
            comparison_frame = CompleteComparisonFrame(alignment_info)
            box_layout.addWidget(comparison_frame)

        self.setLayout(box_layout)


class CompleteComparisonFrameStackerScrollArea(QScrollArea):
    """
    Holds a CompleteComparisonFrameStacker in a QScrollArea
    """
    __stacker = None

    def __init__(self, alignment_info_list: List[AlignmentInfo]):
        """
        Constructor
        :param alignment_info_list: A list of AlignmentInfos to display
        """
        QScrollArea.__init__(self)
        self.__stacker = CompleteComparisonFrameStacker(alignment_info_list)
        self.__stacker.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        box_layout = QVBoxLayout()
        box_layout.addWidget(self.__stacker)
        self.horizontalScrollBar().setEnabled(False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setLayout(box_layout)
        self.setWidget(self.__stacker)
        self.setWidgetResizable(True)
        self.resizeEvent = self.onResize

    # TODO - This is not a nice way to handle the resize
    def onResize(self, arg):
        self.__stacker.resize(self.width() - 20, self.__stacker.height())


class GraphTester(QMainWindow):
    """
    Creates a window that displays multiple alignments
    """

    def __init__(self, alignment_info_list: List[AlignmentInfo]):
        """
        Constructor
        :param alignment_info_list: A list of AlignmentInfos to display
        """
        QMainWindow.__init__(self)
        self.setWindowTitle("Fusion Gene Alignments")
        whole_thing = CompleteComparisonFrameStackerScrollArea(alignment_info_list)
        self.setCentralWidget(whole_thing)


