import cv2
import os
import sys
import logging
import colorlog
import random
from datetime import datetime
from pathlib import Path


def mkdir(video_path: Path, auto: bool = True) -> None:
    logging.info(f"Input path: {video_path.absolute()}")
    if not video_path.exists():
        logging.warning("Path not exist")
        if not auto:
            ans = input("Path not exist. Create new one? (y / n): ")
            if not (ans.upper() == 'Y' or ans.upper() == 'YES'):
                raise OSError("Do not create a new directory.")
        video_path.mkdir(parents=True, exist_ok=True)
        logging.info(f"Path created: {video_path.absolute()}")


def main():
    video_path = Path(sys.argv[1])
    mkdir(video_path)

    files = list(video_path.glob('*.mp4'))
    max_fnum = len(files)
    extract_num = int(input(f"Put numbers to extract (0 ~ {max_fnum}): "))
    if extract_num not in range(max_fnum + 1):
        raise ValueError(
            f"Input not in range. Input is {extract_num}, but range is (0, {max_fnum})")
    samples: list[Path] = random.sample(files, extract_num)

    save_path = Path('images_' + datetime.now().strftime('%y%m%d%H%M%S'))
    save_path.mkdir(parents=True, exist_ok=True)

    for file in samples:
        vidcap: cv2.VideoCapture = cv2.VideoCapture(str(file))
        video_length = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1
        target_frame = int(random.randint(0, video_length))
        logging.info(f"Selected frame: {target_frame} in {file.name}")
        for t in range(target_frame):
            success, image = vidcap.read()
        save_img = save_path / Path(f'{file.stem}_{target_frame}.png')
        if not save_img.exists():
            cv2.imwrite(str(save_img), image)
            logging.info(f"{save_img} is saved.")
        else:
            logging.warning(f"File exist! Overwrited {save_img.name}")


if __name__ == '__main__':
    os.system("cls")
    format = (
        "%(thin_purple)s%(asctime)s "
        "%(reset)s%(thin_blue)s%(bg_black)s%(funcName)s %(lineno)d "
        "%(reset)s%(log_color)s%(levelname)s: "
        "%(reset)s%(message)s"
    )
    colorlog.basicConfig(
        level=logging.INFO, format=format,
        datefmt="%m/%d/%Y %H:%M:%S"
    )
    main()
