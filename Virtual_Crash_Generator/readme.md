# VIRTUAL CRASH File Generator v0.0.1
## File information
It creates people data for VIRTUAL CRASH program. You can set number of humans, generative structure, and file save options.<br>
Consists of 4 files
- <b>`main.py`</b>
    * Main run file
    * <u>Just run this</u> if not want to modify other options
<br><br>
- <b>`human.py`</b>
    * Human data included
    * Can make subclass of `Human`
    * Can modify existing data
<br><br>
- <b>`translate.py`</b>
    * Generate structure included
    * Can make subclass of `Translate`
    * Can modify existing data
<br><br>
- <b>`mbdef.py`</b>
    * Make form-fitting data
    * Control save file
<br><br>
- <b>Notice</b>
    * `.mbdef` is encoded with `shift_jis`, which is based on _japanese_. However, You can read it with any text editor without any special program.
    * You can set options for saving `.txt`.
    * File names are <u>_automatically generated_</u> in sequence. For example, `gen_1.mbdef, gen_2.mbdef, gen_3.mbdef...` You can change generation name, also set arbitrary<b>(not recomanded)</b>.
<br><br>
- <b> Available in this version </b>
    * <u>You can adjust _only translate positon_.</u> Others(angle, velocty, ...) may be added in later versions.
    * Only contains `Square` as `Translate`. This puts humans in regular intervals.
    * Only contains `Korean` as `Human`. Other `Human` data may be added in later versions. Or, you can add in the same form as `Korean`.
    
---
## Install & Run
### Install
-  Enter below command in cmd. You must need `conda`.
    * Note that `virtual_crash` can be replaced any word what you want. <br>
    python version: _3.10.6_<br>
    conda version: _22.9.0_
``` Linux
conda create -n virtual_crash
conda activate virtual_crash
cd (path of this project)
pip install -r requirements.txt
```

### Run
- Enter below command in cmd. You can adjust number, which means <u>__the number of humans__</u>. i.e. below code creates 3 people.
``` Linux
python main.py 3
```
- Or, adjust `launch.json` file. This way can run file only the command `ctrl + f5` in `VS code`.
    * Modify numbers in `"args"`. This means the number of humans.
---
## How to use
### Placement
You can adjust placement. Default is `Square`, which places people in square-like positon in x-y axis. Only modify <b>`main.py`</b>. <br>
#### <u>Interval</u>
Default placement interval is `(1, 1, 0)` as axis `(x, y, z)`. You can set anothor fixed value by using below.
``` python
place_how = tl.Square((0, 0, 0), mans_num, (3, 3, 0))
# The last tuple is interval.
# Above code is set iteval as (3, 3, 0)
# If not put any code, then default value is used.
```
#### <u>Generate direction</u>
`Square` has generate direction. Default direction is `'rt'`, which means <u>_generate right first, top next_</u>. There are total 8 options.
``` python
gen_trans = place_how.trans('rt')
# Other directions are allowed.
# Pick one in (l, r), one in (t, b), and combine in string.
# l: left   r: right    t: top    b: bottom
# Options: 'rt', 'rb', 'lt', 'lb', 'tr', 'tl', 'br', 'bl'
```
### Save
File is saved at directory `results` in this project. File type is `.mbdef` as default, but can choose `.txt` option as mentioned.
``` python
save_path = Path("results")
# Instead of "results", put directory path what you want to save.
# It's okay even if not exist. Automatically created.
```
``` python
mdf.write(text, save_path, is_mbdef=True)
# Default is_mbdef is True. It save mbdef file.
# If you want txt file, then set is_mbdef=False.
# You can also modify file name and encoding. Go to mbdef.py.
```
``` python
def write(text: str, save_path: Path, is_mbdef: bool = True) -> None:
    fname = # Type str what you want in txt
    fpath = save_path / fname
    encoding = # Type str what you want to encode
    file = open(fpath, mode='w', encoding=encoding)
    ...
# Example of fname: 'Example.txt'
# Example of encoding: 'utf-8'
# Note that encoding must be supported by the function open().
```