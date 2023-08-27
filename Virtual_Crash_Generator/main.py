import os
import sys
import pandas as pd
import logging
import colorlog
from pathlib import Path

import human
import translate as tl
import mbdef as mdf


def main():
    mans_num = int(sys.argv[1])

    place_how = tl.Square((0, 0, 0), mans_num)
    logging.info(f"Total people \033[35m{mans_num}")
    logging.info(f"Place mode \033[33m{place_how.__class__.__name__}")
    parag_idx = ""
    parpag_no = ""
    gen_trans = place_how.trans('rt')
    print("")

    for m in range(mans_num):
        person = human.Korean(m)
        logging.info(
            f"Person \033[35m{m} \033[33m{person.__class__.__name__}\033[0m is on")
        trans = gen_trans.__next__()
        logging.info(f"Placed at \033[35m{tuple(trans)}")
        phi = [0, 0, 0]
        vel = [0, 0, 0]
        omega = [0, 0, 0]
        inits = pd.DataFrame({
            'trans': trans,
            'phi': phi,
            'vel': vel,
            'omega': omega
        }, dtype=float)
        parag_idx += mdf.context_idx(person, inits)
        parpag_no += mdf.context_no(person)
        print("")

    total_joints = f"{person.JOINT_NUM * mans_num} Joints\n"

    text = mdf.context_headline(mans_num)
    text += parag_idx + total_joints + parpag_no
    text += person.LINE + mdf.context_ellip_mat()

    save_path = Path("results")
    save_path.mkdir(parents=True, exist_ok=True)
    mdf.write(text, save_path)


if __name__ == "__main__":
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
