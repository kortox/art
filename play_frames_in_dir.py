#!env python
import argparse
from dataclasses import dataclass
import datetime
import os
import sqlite3
import sys
from typing import Optional

from inky.auto import auto
from PIL import Image


@dataclass
class Args:
    directory: str


def parse_args():
    arg_parser = argparse.ArgumentParser("Plays a movie on the wHat screen. One frame at a time.")

    arg_parser.add_argument('--directory', '-d', type=str, required=True, help="Directory of images to be displayed")
    parsed_args, the_rest = arg_parser.parse_known_args(sys.argv[1:])
    return Args(
        directory=parsed_args.directory
    )


def display_image(inky_display, img_file: str):
    """
    Based on display_image.py which is based on examples/what/dither-image-what.py
    """
    img = Image.open(img_file)

    # Get the width and height of the image

    w, h = img.size

    # Calculate the new height and width of the image

    h_new = 300
    w_new = int((float(w) / h) * h_new)
    w_cropped = 400

    # Resize the image with high-quality resampling

    img = img.resize((w_new, h_new), resample=Image.LANCZOS)

    # Calculate coordinates to crop image to 400 pixels wide

    x0 = (w_new - w_cropped) / 2
    x1 = x0 + w_cropped
    y0 = 0
    y1 = h_new

    # Crop image

    img = img.crop((x0, y0, x1, y1))

    # Convert the image to use a white / black / red colour palette

    pal_img = Image.new("P", (1, 1))
    pal_img.putpalette((255, 255, 255, 0, 0, 0, 255, 0, 0) + (0, 0, 0) * 252)

    img = img.convert("RGB").quantize(palette=pal_img)

    # Display the final image on Inky wHAT

    inky_display.set_image(img)
    inky_display.show()

@dataclass
class LastFramePlayed:
    directory: str
    frame_file_name: str
    iso_datetime_played: str

    @staticmethod
    def from_row(row):
        return LastFramePlayed(
            directory=row[0],
            frame_file_name=row[1],
            iso_datetime_played=row[2],
        )

    @staticmethod
    def get_for_dir(sqlite_conn, directory: str):
        result_cursor = sqlite_conn.execute('select directory, frame_file_name, iso_datetime_played from last_frame_played where directory = ?', [directory])
        for row in result_cursor:
            return LastFramePlayed.from_row(row)
        else:
            return None

    def save(self, sqlite_conn):
        sqlite_conn.execute(
            """
            insert into last_frame_played (directory, frame_file_name, iso_datetime_played) values (?, ?, ?)
            on conflict(directory) do update set frame_file_name=?, iso_datetime_played=? where directory=?
            """, 
            [self.directory, self.frame_file_name, self.iso_datetime_played, self.frame_file_name, self.iso_datetime_played, self.directory]
        )
        sqlite_conn.commit()

class FramePlayer:

    def __init__(self, sqlite_conn, directory) -> None:
        self.sqlite_conn = sqlite_conn
        self.directory = directory

    def get_file_after(self, last_frame_played: LastFramePlayed):
        all_files_in_dir = os.listdir(self.directory)
        all_files_in_dir.sort()
        index_of_next_file = -1
        for i, file_name in enumerate(all_files_in_dir):
            if file_name == last_frame_played.frame_file_name:
                index_of_next_file = i
        index_of_next_file += 1
        return all_files_in_dir[index_of_next_file]

    def get_first_file_in_dir(self):
        return os.listdir(self.directory)[0]

    def play_next_frame(self):
        last_frame_played = LastFramePlayed.get_for_dir(sqlite_conn=self.sqlite_conn, directory=self.directory)


        if last_frame_played is None:
            print(f"No last from found. Finding first frame in directory: {self.directory}")
            first_file = self.get_first_file_in_dir()
            if not first_file:
                raise Exception(f"No files in directory, nothing to play: ${self.directory}")
            next_frame_to_play = LastFramePlayed(
                directory=self.directory,
                frame_file_name=first_file,
                iso_datetime_played=str(datetime.datetime.now())
            )
        else:
            print(f"Found last frame: {last_frame_played}")
            next_file_name = self.get_file_after(last_frame_played)
            next_frame_to_play = LastFramePlayed(
                directory=self.directory,
                frame_file_name=next_file_name,
                iso_datetime_played=str(datetime.datetime.now())
            )
        
        print(f"Determined this will be the next frame to show: {next_frame_to_play}")

        print(f"Attempting to connect to inky")
        inky_display = auto(ask_user=True, verbose=True)
        inky_display.set_border(inky_display.WHITE)
        print(f"Connected to inky successfully")

        file_name_to_display = os.path.join(next_frame_to_play.directory, next_frame_to_play.frame_file_name)
        print(f"Attempting to render {file_name_to_display}")
        # display_image(
        #     inky_display=inky_display,
        #     img_file=file_name_to_display,
        # )
        # print("Successfully rendered image on inky")

        # only save once everything is successful!
        next_frame_to_play.save(self.sqlite_conn)


def _main() :
    args = parse_args()
    print(f"Got args {args}")
    sqlite_conn = sqlite3.connect("data/frame_player")
    frame_player = FramePlayer(
        sqlite_conn=sqlite_conn,
        directory=args.directory,
    )

    frame_player.play_next_frame()


if __name__ == '__main__':
    _main()
