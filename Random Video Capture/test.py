
if 1 in range(10):
    print("hdfdw")

max_fnum = 10
extract_num = int(input(f"Put numbers to extract (0 ~ {max_fnum}): "))
range_1 = range(0, max_fnum + 1, 1)
if extract_num in range_1:
    raise ValueError(
        f"Input not in range. Input is {extract_num}, but range is (0, {max_fnum})")