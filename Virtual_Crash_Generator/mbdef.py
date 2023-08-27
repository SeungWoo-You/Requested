from decimal import Decimal
from typing import Type, TYPE_CHECKING
import pandas as pd
from pathlib import Path
import logging

if TYPE_CHECKING:
    from human import Human


def context_headline(humans: int) -> str:
    headline = (
        "MULTIBODY_DEFINITION_FILE\n"
        "124\n"
        "            0.000500 (TimeStep [s])\n"
        "0    (Occupant)\n"
        f"{humans * 20} Bodies\n"
    )
    return headline


def context_idx(man: Type['Human'], inits: pd.DataFrame) -> str:
    info = ""
    for part in man.PART_IDX.values():
        info += man.LINE
        man.set_data_part(part)
        info += man.mk_part_info(inits)
    return info


def context_no(man: Type['Human']) -> str:
    info = ""
    for joi in man.NO_IDX.values():
        info += man.LINE
        man.set_data_joint(joi)
        info += man.mk_joint_info()
    return info


def context_ellip_mat() -> str:
    text = "Ellipsoid Contact matrix (Body 1, Body 2, Contact)"
    return text


def real(k: float | str, digit: int) -> Decimal:
    d = '1'.zfill(digit)
    return Decimal(k).quantize(Decimal(f'.{d}'))


def write(text: str, save_path: Path, is_mbdef: bool = True) -> None:
    fname = f"gen_{len(list(save_path.glob('*')))}.txt"
    fpath = save_path / fname
    encoding = 'shift_jis'
    file = open(fpath, mode='w', encoding=encoding)
    logging.info(f"File \033[36m{fname}\033[0m is created")
    logging.warning(f"Encoding with \033[31m{encoding}")

    file.write(text)
    file.close()
    if not is_mbdef:
        logging.info(f"File \033[36m{fname}\033[0m is saved")
        return

    mbfile = fpath.rename(fpath.with_suffix('.mbdef'))
    logging.info(f"File \033[36m{mbfile.name}\033[0m is saved")
    return
