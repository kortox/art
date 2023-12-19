#!env python

import argparse
from typing import List
from dataclasses import dataclass
import datetime
import os
import re
import sqlite3
import sys

from play_frames_in_dir import LastFramePlayed, FramePlayer

from inky.auto import auto
from PIL import Image, ImageOps


@dataclass
class Args:
    directory: str
    frame: str


def parse_args():
    arg_parser = argparse.ArgumentParser("Plays a movie on the wHat screen. One frame at a time.")

    arg_parser.add_argument(
        '--directory', '-d', type=str, required=True, help="Directory of images to be displayed"
    )

    arg_parser.add_argument(
        '--frame', '-f', type=str, required=True, 
        help="The frame file name to set. Should be a filename in the directory."
    )


    parsed_args, the_rest = arg_parser.parse_known_args(sys.argv[1:])
    return Args(
        directory=parsed_args.directory,
        frame=parsed_args.frame,
    )


def _main() :
    args = parse_args()
    print(f"Got args {args}")
    sqlite_conn = sqlite3.connect("data/frame_player")
    last_frame_to_set = LastFramePlayed(
        directory=args.directory,
        frame_file_name=args.frame,
        iso_datetime_played=datetime.datetime.utcnow(),
        
    )

    last_frame_to_set.save(sqlite_conn=sqlite_conn)
    print(f"Set last frame played for directory {args.directory} to be {last_frame_to_set}")


if __name__ == '__main__':
    _main()
