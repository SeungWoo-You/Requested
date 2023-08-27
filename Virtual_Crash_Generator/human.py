#from __future__ import annotations
from typing import Literal
from numbers import Number
import re
from dataclasses import dataclass
from dacite import from_dict
import pandas as pd
import logging

from mbdef import real


@dataclass
class IndexConfig:
    name: str
    bFrontAndBackCarContact: int
    color1: tuple[int, int, int]
    color2: tuple[int, int, int]
    mass: float
    autocalc_inertia: int
    inertia_1: tuple[float, float, float]
    inertia_2: tuple[float, float, float]
    inertia_3: tuple[float, float, float]
    stiffness: float
    hysteresis: float
    friction2ground: float
    friction2car: float
    abcn: tuple[float, float, float, float]
    init_pos: tuple[float, float, float]
    init_phi: tuple[float, float, float]
    init_vel: tuple[float, float, float]
    init_omega: tuple[float, float, float]


@dataclass
class NoConfig:
    first_Type: int
    kinematic: int
    spring_damper: int
    body: tuple[str, str]
    friction: float
    joint_pos1: tuple[float, float, float]
    joint_pos2: tuple[float, float, float]
    joint_stiff_X: tuple[float, float, float]
    joint_stiff_Y: tuple[float, float, float]
    joint_stiff_Z: tuple[float, float, float]
    joint_locked: tuple[int, int, int]
    joint_type: str
    joint_lim: tuple[Number, Number]
    joint_vel: int


class Human:
    def __init__(self, num: int) -> None:
        self.num = num
        self.part: IndexConfig
        self.joint: NoConfig

    @property
    def SPACE(self) -> int:
        return 20

    @property
    def FLOAT_DIGIT(self) -> int:
        return 6

    @property
    def LINE(self) -> Literal:
        return "--------------------------------------------------------------------------------\n"

    @property
    def PART_IDX(self) -> dict[str, int]:
        return {
            'Torso': 0,
            'Hip': 1,
            'Femur left': 2,
            'lower leg left': 3,
            'Foot left': 4,
            'Femur right': 5,
            'lower leg right': 6,
            'foot right': 7,
            'right upper arm': 8,
            'right lower arm': 9,
            'left upper arm': 10,
            'left lower arm': 11,
            'neck': 12,
            'head': 13,
            'left knee': 14,
            'right knee': 15,
            'dummy lower leg left': 16,
            'dummy lower leg right': 17,
            'dummy femur left': 18,
            'dummy femur right': 19
        }

    @property
    def NO_IDX(self) -> dict[tuple, int]:
        return {
            (0, 1): 0,
            (0, 12): 1,
            (0, 10): 2,
            (0, 8): 3,
            (1, 2): 4,
            (1, 5): 5,
            (2, 3): 6,
            (3, 4): 7,
            (5, 6): 8,
            (6, 7): 9,
            (8, 9): 10,
            (10, 11): 11,
            (12, 13): 12,
            (2, 14): 13,
            (5, 15): 14,
            (3, 16): 15,
            (6, 17): 16,
            (2, 18): 17,
            (5, 19): 18
        }

    @property
    def JOINT_TYPE(self) -> dict[str, int]:
        return {
            'BALL_SOCKET': 1,
            'FIXED': 2,
            'HINGE_Y': 4
        }

    @property
    def PARTS_NUM(self) -> int:
        return len(self.PART_IDX)

    @property
    def JOINT_NUM(self) -> int:
        return len(self.NO_IDX)

    @property
    def INIT_SYS_NUM(self) -> int:
        return 30000

    def insert_rspace(self, data: Number, each_digit: int, is_float: bool = True) -> str:
        if isinstance(data, list):
            data = tuple(data)
        only_num = re.sub('[(,)]', '', str(data))
        split_by_space = only_num.split()
        spaced = []
        for d in split_by_space:
            if is_float:
                d = str(real(d, self.FLOAT_DIGIT))
            spaced.append(d.rjust(each_digit, ' ').upper())
        ret = ' '.join(spaced)
        return ret

    def mk_part_info(self, inits: pd.DataFrame) -> str:
        part_obj = self.part
        part_name = self.part.name
        part_num = self.PART_IDX[part_name]

        inits = inits.set_axis(
            ['trans', 'phi', 'vel', 'omega'], axis='columns')

        trans, phi, vel, omega = inits['trans'], inits['phi'], inits['vel'], inits['omega']

        idx_to_omega_val: list[Number] = [
            self.PARTS_NUM * self.num + part_num,
            self.INIT_SYS_NUM + self.num,
            None,
            part_obj.bFrontAndBackCarContact,
            part_obj.color1,
            part_obj.color2,
            part_obj.mass,
            part_obj.autocalc_inertia,
            part_obj.inertia_1,
            part_obj.inertia_2,
            part_obj.inertia_3,
            part_obj.stiffness,
            part_obj.hysteresis,
            part_obj.friction2ground,
            part_obj.friction2car,
            part_obj.abcn,
            (part_obj.init_pos + trans).to_list(),
            (part_obj.init_phi + phi).to_list(),
            (part_obj.init_vel + vel).to_list(),
            (part_obj.init_omega + omega).to_list()
        ]
        idx_to_omega_str: list[str] = [
            '(Index)',
            '(System)',
            part_name,
            '(bFrontAndBackCarContact)',
            '(color1 r, g, b)',
            '(color2 r, g, b)',
            '(Mass [kg])',
            '(autocalc inertia)',
            '(Inertia [kgmｽ])',
            '(Inertia [kgmｽ])',
            '(Inertia [kgmｽ])',
            '(Stiffness [N/m])',
            '(Hysteresis)',
            '(Friction to Ground)',
            '(Friction to Cars)',
            '(a, b, c, n)',
            '(Init Pos   x, y, z [m])',
            '(Init Phi   x, y, z [rad])',
            '(Init Vel   x, y, z [m/s])',
            '(Init Omega x, y, z [rad/s])'
        ]
        idx_to_omega = zip(idx_to_omega_val, idx_to_omega_str)
        not_floats = [0, 1, 3, 4, 5, 7]

        info = ""
        for i, (v, s) in enumerate(idx_to_omega):
            if i in not_floats:
                is_float = False
            else:
                is_float = True
            if v == None:
                info += f"{s}\n"
            elif 'color' in s:
                info += f"{self.insert_rspace(v, 3, is_float=is_float)} {s}\n"
            else:
                info += f"{self.insert_rspace(v, self.SPACE, is_float)} {s}\n"
        return info

    def get_joinparts_idx(self, bodies: tuple[str]) -> tuple[Number]:
        if not isinstance(bodies, tuple):
            logging.warning(f"Type should be tuple. Get {type(bodies)}")
            bodies = tuple(bodies)
        body_list = re.sub("[('')]", '', str(bodies)).split(',')
        ret: list[Number] = []
        for body in body_list:
            body = body.strip()
            ret.append(self.PART_IDX[body])
        return tuple(ret)

    def mk_joint_info(self) -> str:
        joint_obj = self.joint
        bodies = self.get_joinparts_idx(joint_obj.body)
        joint_no = self.NO_IDX[bodies]

        type_to_rad_val: list[Number] = [
            joint_obj.first_Type,
            (pd.Series(bodies) + self.PARTS_NUM * self.num).to_list(),
            joint_obj.friction,
            joint_obj.joint_pos1,
            joint_obj.joint_pos2,
            joint_obj.joint_stiff_X,
            joint_obj.joint_stiff_Y,
            joint_obj.joint_stiff_Z,
            joint_obj.joint_locked,
            self.JOINT_TYPE[joint_obj.joint_type],
            joint_obj.joint_lim,
            joint_obj.joint_vel
        ]
        type_to_rad_str: list[str] = [
            f'(Type: {joint_obj.kinematic} kinematic, {joint_obj.spring_damper} spring damper)',
            f'(Body1, Body2) {joint_obj.body}',
            '(Friction)',
            '(JointPos1 x, y, z [m])',
            '(JointPos2 x, y, z [m])',
            '(Jointstiffness X Offset[rad], PhiMin[rad], Stiffness[Nm/rad])',
            '(Jointstiffness Y Offset[rad], PhiMin[rad], Stiffness[Nm/rad])',
            '(Jointstiffness Z Offset[rad], PhiMin[rad], Stiffness[Nm/rad])',
            '(Joint locked X, Y, Z not used!!)',
            f'(Joint type - {joint_obj.joint_type})',
            '(joint limits min/max)',
            '(joint vel m/s, rad/s)'
        ]
        type_to_rad = zip(type_to_rad_val, type_to_rad_str)
        not_floats = [0, 1, 8, 9, 10, 11]

        info = f"No.: {self.insert_rspace(self.JOINT_NUM * self.num + joint_no, 4, is_float=False)}\n\n"
        for i, (v, s) in enumerate(type_to_rad):
            if i in not_floats:
                is_float = False
            else:
                is_float = True
            if 'Joint type' in s:
                info += f"{self.insert_rspace(v, 4, is_float)} {s}\n"
            else:
                info += f"{self.insert_rspace(v, self.SPACE, is_float)} {s}\n"
        return info


class Korean(Human):
    def __init__(self, num: int):
        super().__init__(num)

    def set_data_part(self, idx: int | str) -> None:
        if isinstance(idx, str):
            idx = self.PART_IDX[idx]
        data = {
            0: self.data_torso,
            1: self.data_hip,
            2: self.data_femur_left,
            3: self.data_lower_leg_left,
            4: self.data_foot_left,
            5: self.data_femur_right,
            6: self.data_lower_leg_right,
            7: self.data_foot_right,
            8: self.data_right_upper_arm,
            9: self.data_right_lower_arm,
            10: self.data_left_upper_arm,
            11: self.data_left_lower_arm,
            12: self.data_neck,
            13: self.data_head,
            14: self.data_left_knee,
            15: self.data_right_knee,
            16: self.data_dummy_lower_leg_left,
            17: self.data_dummy_lower_leg_right,
            18: self.data_dummy_femur_left,
            19: self.data_dummy_femur_right
        }
        self.part = from_dict(IndexConfig, data[idx])

    def set_data_joint(self, idx: int) -> None:
        data = {
            0: self.data_joint_0,
            1: self.data_joint_1,
            2: self.data_joint_2,
            3: self.data_joint_3,
            4: self.data_joint_4,
            5: self.data_joint_5,
            6: self.data_joint_6,
            7: self.data_joint_7,
            8: self.data_joint_8,
            9: self.data_joint_9,
            10: self.data_joint_10,
            11: self.data_joint_11,
            12: self.data_joint_12,
            13: self.data_joint_13,
            14: self.data_joint_14,
            15: self.data_joint_15,
            16: self.data_joint_16,
            17: self.data_joint_17,
            18: self.data_joint_18
        }
        self.joint = from_dict(NoConfig, data[idx])

    @property
    def data_torso(self) -> dict[str, ]:
        return {
            'name': 'Torso',
            'bFrontAndBackCarContact': 0,
            'color1': (0, 134, 139),
            'color2': (30, 164, 169),
            'mass': 22.000000,
            'autocalc_inertia': 0,
            'inertia_1': (0.395174, 0.000000, 0.000000),
            'inertia_2': (0.000000, 0.296926, 0.000000),
            'inertia_3': (0.000000, 0.000000, 0.255444),
            'stiffness': 215820.000000,
            'hysteresis': 0.100000,
            'friction2ground': 0.600000,
            'friction2car': 0.200000,
            'abcn': (0.120000, 0.180000, 0.200000, 3.000000),
            'init_pos': (0.525438, 0.000000, 1.315000),
            'init_phi': (0.000000, -0.000000, 0.000000),
            'init_vel': (0.000000, 0.000000, 0.000000),
            'init_omega': (0.000000, 0.000000, 0.000000)
        }

    @property
    def data_hip(self) -> dict[str, ]:
        return {
            'name': 'Hip',
            'bFrontAndBackCarContact': 0,
            'color1': (39, 64, 139),
            'color2': (69, 94, 169),
            'mass': 12.000000,
            'autocalc_inertia': 0,
            'inertia_1': (0.120949, 0.000000, 0.000000),
            'inertia_2': (0.000000, 0.072644, 0.000000),
            'inertia_3': (0.000000, 0.000000, 0.134048),
            'stiffness': 117720.000000,
            'hysteresis': 0.100000,
            'friction2ground': 0.600000,
            'friction2car': 0.200000,
            'abcn': (0.120000, 0.175000, 0.100000, 3.000000),
            'init_pos': (0.525438, 0.000000, 1.055000),
            'init_phi': (0.000000, -0.000000, 0.000000),
            'init_vel': (0.000000, 0.000000, 0.000000),
            'init_omega': (0.000000, 0.000000, 0.000000)
        }

    @property
    def data_femur_left(self) -> dict[str, ]:
        return {
            'name': 'Femur left',
            'bFrontAndBackCarContact': 0,
            'color1': (39, 64, 139),
            'color2': (69, 94, 169),
            'mass': 8.000000,
            'autocalc_inertia': 0,
            'inertia_1': (0.119720, 0.000000, 0.000000),
            'inertia_2': (0.000000, 0.119720, 0.000000),
            'inertia_3': (0.000000, 0.000000, 0.023120),
            'stiffness': 120480.000000,
            'hysteresis': 0.100000,
            'friction2ground': 0.600000,
            'friction2car': 0.200000,
            'abcn': (0.085000, 0.085000, 0.260000, 2.000000),
            'init_pos': (0.525438, 0.100000, 0.755000),
            'init_phi': (0.000000, -0.000000, 0.000000),
            'init_vel': (0.000000, 0.000000, 0.000000),
            'init_omega': (0.000000, 0.000000, 0.000000)
        }

    @property
    def data_lower_leg_left(self) -> dict[str, ]:
        return {
            'name': 'lower leg left',
            'bFrontAndBackCarContact': 0,
            'color1': (39, 64, 139),
            'color2': (69, 94, 169),
            'mass': 3.000000,
            'autocalc_inertia': 0,
            'inertia_1': (0.040440, 0.000000, 0.000000),
            'inertia_2': (0.000000, 0.040440, 0.000000),
            'inertia_3': (0.000000, 0.000000, 0.005880),
            'stiffness': 80000.000000,
            'hysteresis': 0.100000,
            'friction2ground': 0.600000,
            'friction2car': 0.200000,
            'abcn': (0.070000, 0.070000, 0.250000, 2.000000),
            'init_pos': (0.525438, 0.100000, 0.285000),
            'init_phi': (0.000000, -0.000000, 0.000000),
            'init_vel': (0.000000, 0.000000, 0.000000),
            'init_omega': (0.000000, 0.000000, 0.000000)
        }

    @property
    def data_foot_left(self) -> dict[str, ]:
        return {
            'name': 'Foot left',
            'bFrontAndBackCarContact': 0,
            'color1': (139, 69, 19),
            'color2': (169, 99, 49),
            'mass': 1.300000,
            'autocalc_inertia': 0,
            'inertia_1': (0.000884, 0.000000, 0.000000),
            'inertia_2': (0.000000, 0.006084, 0.000000),
            'inertia_3': (0.000000, 0.000000, 0.006500),
            'stiffness': 12753.000000,
            'hysteresis': 0.100000,
            'friction2ground': 0.600000,
            'friction2car': 0.200000,
            'abcn': (0.150000, 0.050000, 0.030000, 2.000000),
            'init_pos': (0.625438, 0.100000, 0.030000),
            'init_phi': (0.000000, -0.000000, 0.000000),
            'init_vel': (0.000000, 0.000000, 0.000000),
            'init_omega': (0.000000, 0.000000, 0.000000)
        }

    @property
    def data_femur_right(self) -> dict[str, ]:
        return {
            'name': 'Femur right',
            'bFrontAndBackCarContact': 0,
            'color1': (39, 64, 139),
            'color2': (69, 94, 169),
            'mass': 8.000000,
            'autocalc_inertia': 0,
            'inertia_1': (0.119720, 0.000000, 0.000000),
            'inertia_2': (0.000000, 0.119720, 0.000000),
            'inertia_3': (0.000000, 0.000000, 0.023120),
            'stiffness': 120480.000000,
            'hysteresis': 0.100000,
            'friction2ground': 0.600000,
            'friction2car': 0.200000,
            'abcn': (0.085000, 0.085000, 0.260000, 2.000000),
            'init_pos': (0.525438, -0.100000, 0.755000),
            'init_phi': (0.000000, -0.000000, 0.000000),
            'init_vel': (0.000000, 0.000000, 0.000000),
            'init_omega': (0.000000, 0.000000, 0.000000)
        }

    @property
    def data_lower_leg_right(self) -> dict[str, ]:
        return {
            'name': 'lower leg right',
            'bFrontAndBackCarContact': 0,
            'color1': (39, 64, 139),
            'color2': (69, 94, 169),
            'mass': 3.000000,
            'autocalc_inertia': 0,
            'inertia_1': (0.040440, 0.000000, 0.000000),
            'inertia_2': (0.000000, 0.040440, 0.000000),
            'inertia_3': (0.000000, 0.000000, 0.005880),
            'stiffness': 80000.000000,
            'hysteresis': 0.100000,
            'friction2ground': 0.600000,
            'friction2car': 0.200000,
            'abcn': (0.070000, 0.070000, 0.250000, 2.000000),
            'init_pos': (0.525438, -0.100000, 0.285000),
            'init_phi': (0.000000, -0.000000, 0.000000),
            'init_vel': (0.000000, 0.000000, 0.000000),
            'init_omega': (0.000000, 0.000000, 0.000000)
        }

    @property
    def data_foot_right(self) -> dict[str, ]:
        return {
            'name': 'foot right',
            'bFrontAndBackCarContact': 0,
            'color1': (139, 69, 19),
            'color2': (169, 99, 49),
            'mass': 1.300000,
            'autocalc_inertia': 0,
            'inertia_1': (0.000884, 0.000000, 0.000000),
            'inertia_2': (0.000000, 0.006084, 0.000000),
            'inertia_3': (0.000000, 0.000000, 0.006500),
            'stiffness': 12753.000000,
            'hysteresis': 0.100000,
            'friction2ground': 0.600000,
            'friction2car': 0.200000,
            'abcn': (0.150000, 0.050000, 0.030000, 2.000000),
            'init_pos': (0.625438, -0.100000, 0.030000),
            'init_phi': (0.000000, -0.000000, 0.000000),
            'init_vel': (0.000000, 0.000000, 0.000000),
            'init_omega': (0.000000, 0.000000, 0.000000)
        }

    @property
    def data_right_upper_arm(self) -> dict[str, ]:
        return {
            'name': 'right upper arm',
            'bFrontAndBackCarContact': 0,
            'color1': (0, 134, 139),
            'color2': (30, 164, 169),
            'mass': 2.200000,
            'autocalc_inertia': 0,
            'inertia_1': (0.012364, 0.000000, 0.000000),
            'inertia_2': (0.000000, 0.012364, 0.000000),
            'inertia_3': (0.000000, 0.000000, 0.002200),
            'stiffness': 80582.000000,
            'hysteresis': 0.100000,
            'friction2ground': 0.600000,
            'friction2car': 0.200000,
            'abcn': (0.050000, 0.050000, 0.160000, 2.000000),
            'init_pos': (0.525438, -0.240000, 1.355000),
            'init_phi': (0.000000, -0.000000, 0.000000),
            'init_vel': (0.000000, 0.000000, 0.000000),
            'init_omega': (0.000000, 0.000000, 0.000000)
        }

    @property
    def data_right_lower_arm(self) -> dict[str, ]:
        return {
            'name': 'right lower arm',
            'bFrontAndBackCarContact': 0,
            'color1': (0, 134, 139),
            'color2': (30, 164, 169),
            'mass': 1.500000,
            'autocalc_inertia': 0,
            'inertia_1': (0.008288, 0.000000, 0.000000),
            'inertia_2': (0.000000, 0.008288, 0.000000),
            'inertia_3': (0.000000, 0.000000, 0.001215),
            'stiffness': 70715.000000,
            'hysteresis': 0.100000,
            'friction2ground': 0.600000,
            'friction2car': 0.200000,
            'abcn': (0.045000, 0.045000, 0.160000, 2.000000),
            'init_pos': (0.525438, -0.240000, 1.095000),
            'init_phi': (0.000000, -0.000000, 0.000000),
            'init_vel': (0.000000, 0.000000, 0.000000),
            'init_omega': (0.000000, 0.000000, 0.000000)
        }

    @property
    def data_left_upper_arm(self) -> dict[str, ]:
        return {
            'name': 'left upper arm',
            'bFrontAndBackCarContact': 0,
            'color1': (0, 134, 139),
            'color2': (30, 164, 169),
            'mass': 2.200000,
            'autocalc_inertia': 0,
            'inertia_1': (0.012364, 0.000000, 0.000000),
            'inertia_2': (0.000000, 0.012364, 0.000000),
            'inertia_3': (0.000000, 0.000000, 0.002200),
            'stiffness': 80582.000000,
            'hysteresis': 0.100000,
            'friction2ground': 0.600000,
            'friction2car': 0.200000,
            'abcn': (0.050000, 0.050000, 0.160000, 2.000000),
            'init_pos': (0.525438, 0.240000, 1.355000),
            'init_phi': (0.000000, -0.000000, 0.000000),
            'init_vel': (0.000000, 0.000000, 0.000000),
            'init_omega': (0.000000, 0.000000, 0.000000)
        }

    @property
    def data_left_lower_arm(self) -> dict[str, ]:
        return {
            'name': 'left lower arm',
            'bFrontAndBackCarContact': 0,
            'color1': (0, 134, 139),
            'color2': (30, 164, 169),
            'mass': 1.500000,
            'autocalc_inertia': 0,
            'inertia_1': (0.008288, 0.000000, 0.000000),
            'inertia_2': (0.000000, 0.008288, 0.000000),
            'inertia_3': (0.000000, 0.000000, 0.001215),
            'stiffness': 70715.000000,
            'hysteresis': 0.100000,
            'friction2ground': 0.600000,
            'friction2car': 0.200000,
            'abcn': (0.045000, 0.045000, 0.160000, 2.000000),
            'init_pos': (0.525438, 0.240000, 1.095000),
            'init_phi': (0.000000, -0.000000, 0.000000),
            'init_vel': (0.000000, 0.000000, 0.000000),
            'init_omega': (0.000000, 0.000000, 0.000000)
        }

    @property
    def data_neck(self) -> dict[str, ]:
        return {
            'name': 'neck',
            'bFrontAndBackCarContact': 0,
            'color1': (255, 160, 122),
            'color2': (255, 190, 152),
            'mass': 3.000000,
            'autocalc_inertia': 0,
            'inertia_1': (0.006000, 0.000000, 0.000000),
            'inertia_2': (0.000000, 0.006000, 0.000000),
            'inertia_3': (0.000000, 0.000000, 0.004320),
            'stiffness': 29430.000000,
            'hysteresis': 0.100000,
            'friction2ground': 0.600000,
            'friction2car': 0.200000,
            'abcn': (0.060000, 0.060000, 0.080000, 2.000000),
            'init_pos': (0.525438, 0.000000, 1.555000),
            'init_phi': (0.000000, -0.000000, 0.000000),
            'init_vel': (0.000000, 0.000000, 0.000000),
            'init_omega': (0.000000, 0.000000, 0.000000)
        }

    @property
    def data_head(self) -> dict[str, ]:
        return {
            'name': 'head',
            'bFrontAndBackCarContact': 0,
            'color1': (255, 160, 122),
            'color2': (255, 190, 152),
            'mass': 5.000000,
            'autocalc_inertia': 0,
            'inertia_1': (0.024400, 0.000000, 0.000000),
            'inertia_2': (0.000000, 0.024400, 0.000000),
            'inertia_3': (0.000000, 0.000000, 0.020000),
            'stiffness': 49050.000000,
            'hysteresis': 0.100000,
            'friction2ground': 0.600000,
            'friction2car': 0.200000,
            'abcn': (0.100000, 0.100000, 0.120000, 2.000000),
            'init_pos': (0.525438, 0.000000, 1.715000),
            'init_phi': (0.000000, -0.000000, 0.000000),
            'init_vel': (0.000000, 0.000000, 0.000000),
            'init_omega': (0.000000, 0.000000, 0.000000)
        }

    @property
    def data_left_knee(self) -> dict[str, ]:
        return {
            'name': 'left knee',
            'bFrontAndBackCarContact': 0,
            'color1': (39, 64, 139),
            'color2': (69, 94, 169),
            'mass': 1.000000,
            'autocalc_inertia': 0,
            'inertia_1': (0.001440, 0.000000, 0.000000),
            'inertia_2': (0.000000, 0.001440, 0.000000),
            'inertia_3': (0.000000, 0.000000, 0.001440),
            'stiffness': 490050.000000,
            'hysteresis': 0.100000,
            'friction2ground': 0.600000,
            'friction2car': 0.200000,
            'abcn': (0.060000, 0.060000, 0.060000, 2.000000),
            'init_pos': (0.525438, 0.100000, 0.515000),
            'init_phi': (0.000000, -0.000000, 0.000000),
            'init_vel': (0.000000, 0.000000, 0.000000),
            'init_omega': (0.000000, 0.000000, 0.000000)
        }

    @property
    def data_right_knee(self) -> dict[str, ]:
        return {
            'name': 'right knee',
            'bFrontAndBackCarContact': 0,
            'color1': (39, 64, 139),
            'color2': (69, 94, 169),
            'mass': 1.000000,
            'autocalc_inertia': 0,
            'inertia_1': (0.001440, 0.000000, 0.000000),
            'inertia_2': (0.000000, 0.001440, 0.000000),
            'inertia_3': (0.000000, 0.000000, 0.001440),
            'stiffness': 490050.000000,
            'hysteresis': 0.100000,
            'friction2ground': 0.600000,
            'friction2car': 0.200000,
            'abcn': (0.060000, 0.060000, 0.060000, 2.000000),
            'init_pos': (0.525438, -0.100000, 0.515000),
            'init_phi': (0.000000, -0.000000, 0.000000),
            'init_vel': (0.000000, 0.000000, 0.000000),
            'init_omega': (0.000000, 0.000000, 0.000000)
        }

    @property
    def data_dummy_lower_leg_left(self) -> dict[str, ]:
        return {
            'name': 'dummy lower leg left',
            'bFrontAndBackCarContact': 0,
            'color1': (39, 64, 139),
            'color2': (69, 94, 169),
            'mass': 1.000000,
            'autocalc_inertia': 0,
            'inertia_1': (0.001440, 0.000000, 0.000000),
            'inertia_2': (0.000000, 0.001440, 0.000000),
            'inertia_3': (0.000000, 0.000000, 0.001440),
            'stiffness': 490050.000000,
            'hysteresis': 0.100000,
            'friction2ground': 0.600000,
            'friction2car': 0.200000,
            'abcn': (0.060000, 0.060000, 0.060000, 2.000000),
            'init_pos': (0.525438, 0.100000, 0.285000),
            'init_phi': (0.000000, -0.000000, 0.000000),
            'init_vel': (0.000000, 0.000000, 0.000000),
            'init_omega': (0.000000, 0.000000, 0.000000)
        }

    @property
    def data_dummy_lower_leg_right(self) -> dict[str, ]:
        return {
            'name': 'dummy lower leg right',
            'bFrontAndBackCarContact': 0,
            'color1': (39, 64, 139),
            'color2': (69, 94, 169),
            'mass': 1.000000,
            'autocalc_inertia': 0,
            'inertia_1': (0.001440, 0.000000, 0.000000),
            'inertia_2': (0.000000, 0.001440, 0.000000),
            'inertia_3': (0.000000, 0.000000, 0.001440),
            'stiffness': 490050.000000,
            'hysteresis': 0.100000,
            'friction2ground': 0.600000,
            'friction2car': 0.200000,
            'abcn': (0.060000, 0.060000, 0.060000, 2.000000),
            'init_pos': (0.525438, -0.100000, 0.285000),
            'init_phi': (0.000000, -0.000000, 0.000000),
            'init_vel': (0.000000, 0.000000, 0.000000),
            'init_omega': (0.000000, 0.000000, 0.000000)
        }

    @property
    def data_dummy_femur_left(self) -> dict[str, ]:
        return {
            'name': 'dummy femur left',
            'bFrontAndBackCarContact': 0,
            'color1': (39, 64, 139),
            'color2': (69, 94, 169),
            'mass': 1.000000,
            'autocalc_inertia': 0,
            'inertia_1': (0.002890, 0.000000, 0.000000),
            'inertia_2': (0.000000, 0.002890, 0.000000),
            'inertia_3': (0.000000, 0.000000, 0.002890),
            'stiffness': 490050.000000,
            'hysteresis': 0.100000,
            'friction2ground': 0.600000,
            'friction2car': 0.200000,
            'abcn': (0.085000, 0.085000, 0.085000, 2.000000),
            'init_pos': (0.525438, 0.100000, 0.755000),
            'init_phi': (0.000000, -0.000000, 0.000000),
            'init_vel': (0.000000, 0.000000, 0.000000),
            'init_omega': (0.000000, 0.000000, 0.000000)
        }

    @property
    def data_dummy_femur_right(self) -> dict[str, ]:
        return {
            'name': 'dummy femur right',
            'bFrontAndBackCarContact': 0,
            'color1': (39, 64, 139),
            'color2': (69, 94, 169),
            'mass': 1.000000,
            'autocalc_inertia': 0,
            'inertia_1': (0.002890, 0.000000, 0.000000),
            'inertia_2': (0.000000, 0.002890, 0.000000),
            'inertia_3': (0.000000, 0.000000, 0.002890),
            'stiffness': 490050.000000,
            'hysteresis': 0.100000,
            'friction2ground': 0.600000,
            'friction2car': 0.200000,
            'abcn': (0.085000, 0.085000, 0.085000, 2.000000),
            'init_pos': (0.525438, -0.100000, 0.755000),
            'init_phi': (0.000000, -0.000000, 0.000000),
            'init_vel': (0.000000, 0.000000, 0.000000),
            'init_omega': (0.000000, 0.000000, 0.000000)
        }

    @property
    def data_joint_0(self) -> dict[str, ]:
        return {
            'first_Type': 0,
            'kinematic': 0,
            'spring_damper': 1,
            'body': ('Torso', 'Hip'),
            'friction': 0.500000,
            'joint_pos1': (0.000000, 0.000000, -0.156948),
            'joint_pos2': (0.000000, 0.000000, 0.069755),
            'joint_stiff_X': (0.000000, 0.000000, 0.000000),
            'joint_stiff_Y': (0.000000, 0.000000, 0.000000),
            'joint_stiff_Z': (0.000000, 0.000000, 0.000000),
            'joint_locked': (0, 0, 0),
            'joint_type': 'FIXED',
            'joint_lim': (-1E+030, 1E+030),
            'joint_vel': 0
        }

    @property
    def data_joint_1(self) -> dict[str, ]:
        return {
            'first_Type': 0,
            'kinematic': 0,
            'spring_damper': 1,
            'body': ('Torso', 'neck'),
            'friction': 5.500000,
            'joint_pos1': (0.000000, 0.000000, 0.156948),
            'joint_pos2': (0.000000, 0.000000, -0.052316),
            'joint_stiff_X': (0.000000, 0.000000, 0.000000),
            'joint_stiff_Y': (0.000000, 0.000000, 0.000000),
            'joint_stiff_Z': (0.000000, 0.000000, 0.000000),
            'joint_locked': (0, 0, 0),
            'joint_type': 'BALL_SOCKET',
            'joint_lim': (-1E+030, 1E+030),
            'joint_vel': 0
        }

    @property
    def data_joint_2(self) -> dict[str, ]:
        return {
            'first_Type': 0,
            'kinematic': 0,
            'spring_damper': 1,
            'body': ('Torso', 'left upper arm'),
            'friction': 0.500000,
            'joint_pos1': (0.000000, 0.209264, 0.174387),
            'joint_pos2': (0.000000, 0.000000, 0.139510),
            'joint_stiff_X': (0.000000, 0.000000, 0.000000),
            'joint_stiff_Y': (0.000000, 0.000000, 0.000000),
            'joint_stiff_Z': (0.000000, 0.000000, 0.000000),
            'joint_locked': (0, 0, 0),
            'joint_type': 'BALL_SOCKET',
            'joint_lim': (-1E+030, 1E+030),
            'joint_vel': 0
        }

    @property
    def data_joint_3(self) -> dict[str, ]:
        return {
            'first_Type': 0,
            'kinematic': 0,
            'spring_damper': 1,
            'body': ('Torso', 'right upper arm'),
            'friction': 0.500000,
            'joint_pos1': (0.000000, -0.209264, 0.174387),
            'joint_pos2': (0.000000, 0.000000, 0.139510),
            'joint_stiff_X': (0.000000, 0.000000, 0.000000),
            'joint_stiff_Y': (0.000000, 0.000000, 0.000000),
            'joint_stiff_Z': (0.000000, 0.000000, 0.000000),
            'joint_locked': (0, 0, 0),
            'joint_type': 'BALL_SOCKET',
            'joint_lim': (-1E+030, 1E+030),
            'joint_vel': 0
        }

    @property
    def data_joint_4(self) -> dict[str, ]:
        return {
            'first_Type': 0,
            'kinematic': 0,
            'spring_damper': 1,
            'body': ('Hip', 'Femur left'),
            'friction': 50.000000,
            'joint_pos1': (0.000000, 0.087193, -0.052316),
            'joint_pos2': (0.000000, 0.000000, 0.209264),
            'joint_stiff_X': (0.000000, 0.000000, 0.000000),
            'joint_stiff_Y': (0.000000, 0.000000, 0.000000),
            'joint_stiff_Z': (0.000000, 0.000000, 0.000000),
            'joint_locked': (0, 0, 0),
            'joint_type': 'FIXED',
            'joint_lim': (-1E+030, 1E+030),
            'joint_vel': 0
        }

    @property
    def data_joint_5(self) -> dict[str, ]:
        return {
            'first_Type': 0,
            'kinematic': 0,
            'spring_damper': 1,
            'body': ('Hip', 'Femur right'),
            'friction': 20.000000,
            'joint_pos1': (0.000000, -0.087193, -0.052316),
            'joint_pos2': (0.000000, 0.000000, 0.209264),
            'joint_stiff_X': (0.000000, 0.000000, 0.000000),
            'joint_stiff_Y': (0.000000, 0.000000, 0.000000),
            'joint_stiff_Z': (0.000000, 0.000000, 0.000000),
            'joint_locked': (0, 0, 0),
            'joint_type': 'BALL_SOCKET',
            'joint_lim': (-1E+030, 1E+030),
            'joint_vel': 0
        }

    @property
    def data_joint_6(self) -> dict[str, ]:
        return {
            'first_Type': 0,
            'kinematic': 0,
            'spring_damper': 1,
            'body': ('Femur left', 'lower leg left'),
            'friction': 15.000000,
            'joint_pos1': (0.000000, 0.000000, -0.209264),
            'joint_pos2': (0.000000, 0.000000, 0.200545),
            'joint_stiff_X': (0.000000, 0.000000, 0.000000),
            'joint_stiff_Y': (0.000000, 0.000000, 0.000000),
            'joint_stiff_Z': (0.000000, 0.000000, 0.000000),
            'joint_locked': (0, 0, 0),
            'joint_type': 'HINGE_Y',
            'joint_lim': (-1E+030, 1E+030),
            'joint_vel': 0
        }

    @property
    def data_joint_7(self) -> dict[str, ]:
        return {
            'first_Type': 0,
            'kinematic': 0,
            'spring_damper': 1,
            'body': ('lower leg left', 'Foot left'),
            'friction': 10.000000,
            'joint_pos1': (0.000000, 0.000000, -0.209264),
            'joint_pos2': (-0.087193, 0.000000, 0.013079),
            'joint_stiff_X': (0.000000, 0.000000, 0.000000),
            'joint_stiff_Y': (0.000000, 0.000000, 0.000000),
            'joint_stiff_Z': (0.000000, 0.000000, 0.000000),
            'joint_locked': (0, 0, 0),
            'joint_type': 'BALL_SOCKET',
            'joint_lim': (-1E+030, 1E+030),
            'joint_vel': 0
        }

    @property
    def data_joint_8(self) -> dict[str, ]:
        return {
            'first_Type': 0,
            'kinematic': 0,
            'spring_damper': 1,
            'body': ('Femur right', 'lower leg right'),
            'friction': 15.000000,
            'joint_pos1': (0.000000, 0.000000, -0.209264),
            'joint_pos2': (0.000000, 0.000000, 0.200545),
            'joint_stiff_X': (0.000000, 0.000000, 0.000000),
            'joint_stiff_Y': (0.000000, 0.000000, 0.000000),
            'joint_stiff_Z': (0.000000, 0.000000, 0.000000),
            'joint_locked': (0, 0, 0),
            'joint_type': 'HINGE_Y',
            'joint_lim': (-1E+030, 1E+030),
            'joint_vel': 0
        }

    @property
    def data_joint_9(self) -> dict[str, ]:
        return {
            'first_Type': 0,
            'kinematic': 0,
            'spring_damper': 1,
            'body': ('lower leg right', 'foot right'),
            'friction': 3.000000,
            'joint_pos1': (0.000000, 0.000000, -0.209264),
            'joint_pos2': (-0.087193, 0.000000, 0.013079),
            'joint_stiff_X': (0.000000, 0.000000, 0.000000),
            'joint_stiff_Y': (0.000000, 0.000000, 0.000000),
            'joint_stiff_Z': (0.000000, 0.000000, 0.000000),
            'joint_locked': (0, 0, 0),
            'joint_type': 'BALL_SOCKET',
            'joint_lim': (-1E+030, 1E+030),
            'joint_vel': 0
        }

    @property
    def data_joint_10(self) -> dict[str, ]:
        return {
            'first_Type': 0,
            'kinematic': 0,
            'spring_damper': 1,
            'body': ('right upper arm', 'right lower arm'),
            'friction': 5.500000,
            'joint_pos1': (0.000000, 0.000000, -0.113351),
            'joint_pos2': (0.000000, 0.000000, 0.113351),
            'joint_stiff_X': (0.000000, 0.000000, 0.000000),
            'joint_stiff_Y': (0.000000, 0.000000, 0.000000),
            'joint_stiff_Z': (0.000000, 0.000000, 0.000000),
            'joint_locked': (0, 0, 0),
            'joint_type': 'HINGE_Y',
            'joint_lim': (-1E+030, 1E+030),
            'joint_vel': 0
        }

    @property
    def data_joint_11(self) -> dict[str, ]:
        return {
            'first_Type': 0,
            'kinematic': 0,
            'spring_damper': 1,
            'body': ('left upper arm', 'left lower arm'),
            'friction': 5.500000,
            'joint_pos1': (0.000000, 0.000000, -0.113351),
            'joint_pos2': (0.000000, 0.000000, 0.113351),
            'joint_stiff_X': (0.000000, 0.000000, 0.000000),
            'joint_stiff_Y': (0.000000, 0.000000, 0.000000),
            'joint_stiff_Z': (0.000000, 0.000000, 0.000000),
            'joint_locked': (0, 0, 0),
            'joint_type': 'HINGE_Y',
            'joint_lim': (-1E+030, 1E+030),
            'joint_vel': 0
        }

    @property
    def data_joint_12(self) -> dict[str, ]:
        return {
            'first_Type': 0,
            'kinematic': 0,
            'spring_damper': 1,
            'body': ('neck', 'head'),
            'friction': 5.500000,
            'joint_pos1': (0.000000, 0.000000, 0.052316),
            'joint_pos2': (0.000000, 0.000000, -0.087193),
            'joint_stiff_X': (0.000000, 0.000000, 0.000000),
            'joint_stiff_Y': (0.000000, 0.000000, 0.000000),
            'joint_stiff_Z': (0.000000, 0.000000, 0.000000),
            'joint_locked': (0, 0, 0),
            'joint_type': 'BALL_SOCKET',
            'joint_lim': (-1E+030, 1E+030),
            'joint_vel': 0
        }

    @property
    def data_joint_13(self) -> dict[str, ]:
        return {
            'first_Type': 0,
            'kinematic': 0,
            'spring_damper': 1,
            'body': ('Femur left', 'left knee'),
            'friction': 5.500000,
            'joint_pos1': (0.000000, 0.000000, -0.209264),
            'joint_pos2': (0.000000, 0.000000, 0.000000),
            'joint_stiff_X': (0.000000, 0.000000, 0.000000),
            'joint_stiff_Y': (0.000000, 0.000000, 0.000000),
            'joint_stiff_Z': (0.000000, 0.000000, 0.000000),
            'joint_locked': (0, 0, 0),
            'joint_type': 'FIXED',
            'joint_lim': (-1E+030, 1E+030),
            'joint_vel': 0
        }

    @property
    def data_joint_14(self) -> dict[str, ]:
        return {
            'first_Type': 0,
            'kinematic': 0,
            'spring_damper': 1,
            'body': ('Femur right', 'right knee'),
            'friction': 5.500000,
            'joint_pos1': (0.000000, 0.000000, -0.209264),
            'joint_pos2': (0.000000, 0.000000, 0.000000),
            'joint_stiff_X': (0.000000, 0.000000, 0.000000),
            'joint_stiff_Y': (0.000000, 0.000000, 0.000000),
            'joint_stiff_Z': (0.000000, 0.000000, 0.000000),
            'joint_locked': (0, 0, 0),
            'joint_type': 'FIXED',
            'joint_lim': (-1E+030, 1E+030),
            'joint_vel': 0
        }

    @property
    def data_joint_15(self) -> dict[str, ]:
        return {
            'first_Type': 0,
            'kinematic': 0,
            'spring_damper': 1,
            'body': ('lower leg left', 'dummy lower leg left'),
            'friction': 5.500000,
            'joint_pos1': (0.000000, 0.000000, 0.000000),
            'joint_pos2': (0.000000, 0.000000, 0.000000),
            'joint_stiff_X': (0.000000, 0.000000, 0.000000),
            'joint_stiff_Y': (0.000000, 0.000000, 0.000000),
            'joint_stiff_Z': (0.000000, 0.000000, 0.000000),
            'joint_locked': (0, 0, 0),
            'joint_type': 'FIXED',
            'joint_lim': (-1E+030, 1E+030),
            'joint_vel': 0
        }

    @property
    def data_joint_16(self) -> dict[str, ]:
        return {
            'first_Type': 0,
            'kinematic': 0,
            'spring_damper': 1,
            'body': ('lower leg right', 'dummy lower leg right'),
            'friction': 5.500000,
            'joint_pos1': (0.000000, 0.000000, 0.000000),
            'joint_pos2': (0.000000, 0.000000, 0.000000),
            'joint_stiff_X': (0.000000, 0.000000, 0.000000),
            'joint_stiff_Y': (0.000000, 0.000000, 0.000000),
            'joint_stiff_Z': (0.000000, 0.000000, 0.000000),
            'joint_locked': (0, 0, 0),
            'joint_type': 'FIXED',
            'joint_lim': (-1E+030, 1E+030),
            'joint_vel': 0
        }

    @property
    def data_joint_17(self) -> dict[str, ]:
        return {
            'first_Type': 0,
            'kinematic': 0,
            'spring_damper': 1,
            'body': ('Femur left', 'dummy femur left'),
            'friction': 5.500000,
            'joint_pos1': (0.000000, 0.000000, 0.000000),
            'joint_pos2': (0.000000, 0.000000, 0.000000),
            'joint_stiff_X': (0.000000, 0.000000, 0.000000),
            'joint_stiff_Y': (0.000000, 0.000000, 0.000000),
            'joint_stiff_Z': (0.000000, 0.000000, 0.000000),
            'joint_locked': (0, 0, 0),
            'joint_type': 'FIXED',
            'joint_lim': (-1E+030, 1E+030),
            'joint_vel': 0
        }

    @property
    def data_joint_18(self) -> dict[str, ]:
        return {
            'first_Type': 0,
            'kinematic': 0,
            'spring_damper': 1,
            'body': ('Femur right', 'dummy femur right'),
            'friction': 5.500000,
            'joint_pos1': (0.000000, 0.000000, 0.000000),
            'joint_pos2': (0.000000, 0.000000, 0.000000),
            'joint_stiff_X': (0.000000, 0.000000, 0.000000),
            'joint_stiff_Y': (0.000000, 0.000000, 0.000000),
            'joint_stiff_Z': (0.000000, 0.000000, 0.000000),
            'joint_locked': (0, 0, 0),
            'joint_type': 'FIXED',
            'joint_lim': (-1E+030, 1E+030),
            'joint_vel': 0
        }
