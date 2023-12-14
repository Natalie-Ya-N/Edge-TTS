"""
SubMaker package for the Edge TTS project.

SubMaker is a package that makes the process of creating subtitles with
information provided by the service easier.
"""

import math
from typing import List, Tuple
from xml.sax.saxutils import escape, unescape


def formatter(
    sub_line_count: int, start_time: float, end_time: float, subdata: str
) -> str:
    """
    formatter returns the timecode and the text of the subtitle.
    """
    return (
        f"{sub_line_count}\n"
        f"{mktimestamp(start_time)} --> {mktimestamp(end_time)}\n"
        f"{escape(subdata)}\n\n"
    )


def mktimestamp(time_unit: float) -> str:
    """
    mktimestamp returns the timecode of the subtitle.

    The timecode is in the format of 00:00:00.000.

    Returns:
        str: The timecode of the subtitle.
    """
    hour = math.floor(time_unit / 10**7 / 3600)
    minute = math.floor((time_unit / 10**7 / 60) % 60)
    seconds = (time_unit / 10**7) % 60
    # return f"{hour:02d}:{minute:02d}:{seconds:06.3f}"
    return f"{hour:02d}:{minute:02d}:{seconds:06.3f}".replace(".", ",")


class SubMaker:
    """
    SubMaker class
    """

    def __init__(self) -> None:
        """
        SubMaker constructor.
        """
        self.offset: List[Tuple[float, float]] = []
        self.subs: List[str] = []

    def create_sub(self, timestamp: Tuple[float, float], text: str) -> None:
        """
        create_sub creates a subtitle with the given timestamp and text
        and adds it to the list of subtitles

        Args:
            timestamp (tuple): The offset and duration of the subtitle.
            text (str): The text of the subtitle.

        Returns:
            None
        """
        self.offset.append((timestamp[0], timestamp[0] + timestamp[1]))
        self.subs.append(text)

    def generate_subs(self, three_dimensional_list, words_in_cue: int = 10) -> str:
        """
        generate_subs generates the complete subtitle file.

        Args:
            words_in_cue (int): defines the number of words in a given cue

        Returns:
            str: The complete subtitle file.

        three_dimensional_list：
            [(sentence, last_word, last_word_num)， (sentence, last_word, last_word_num)]
        """
        if len(self.subs) != len(self.offset):
            raise ValueError("subs and offset are not of the same length")

        if words_in_cue <= 0:
            raise ValueError("words_in_cue must be greater than 0")

        # data = "WEBVTT\r\n\r\n"
        data = ""
        sub_state_count = 0
        sub_state_start = -1.0
        sub_state_subs = ""
        sub_line_count = (
            0  # new variable used to indicate which line of subtitle this is
        )
        for idx, (offset, subs) in enumerate(zip(self.offset, self.subs)):
            start_time, end_time = offset
            subs = unescape(subs)

            # wordboundary is guaranteed not to contain whitespace
            # if len(sub_state_subs) > 0:
            #     sub_state_subs += " "
            sub_state_subs += subs

            if sub_state_start == -1.0:
                sub_state_start = start_time
            sub_state_count += 1

            sentence, last_word, last_word_num = three_dimensional_list[sub_line_count]
            if (
                sub_state_subs.count(last_word) == last_word_num
                or idx == len(self.offset) - 1
            ):
                sub_line_count += 1
                # subs = sub_state_subs
                subs = sentence
                split_subs: List[str] = [
                    subs[i : i + 79] for i in range(0, len(subs), 79)
                ]
                for i in range(len(split_subs) - 1):
                    sub = split_subs[i]
                    split_at_word = True
                    if sub[-1] == " ":
                        split_subs[i] = sub[:-1]
                        split_at_word = False

                    if sub[0] == " ":
                        split_subs[i] = sub[1:]
                        split_at_word = False

                    if split_at_word:
                        split_subs[i] += "-"

                data += formatter(
                    sub_line_count=sub_line_count,
                    start_time=sub_state_start,
                    end_time=end_time,
                    subdata="".join(split_subs),
                )
                sub_state_count = 0
                sub_state_start = -1
                sub_state_subs = ""
        return data
