#!/usr/bin/env python3

import xlrd
import re


def is_test_case_name(cell_content):
    if re.search(r'B[V|I]-\d{2}-C', cell_content):
        return True
    else:
        return False


def get_set_of_test_case_names(path_to_xl_file):
    xlsheet = xlrd.open_workbook(path_to_xl_file).sheet_by_index(0)
    return {x.value for x in xlsheet.col(0, 0, xlsheet.nrows) if is_test_case_name(x.value)}


def get_set_of_test_case_names_supported_by_pts():
    # If you have Bluetooth SIG account, you can get the PTSCoverage.xlsx from:
    # https://www.bluetooth.com/develop-with-bluetooth/qualification-listing/qualification-test-tools/pts-test-coverage/
    xlsheet = xlrd.open_workbook('./PTSCoverage.xlsx').sheet_by_index(0)
    test_case_names = set()
    for row in range(1, xlsheet.nrows):
        layer = xlsheet.cell(row, 0).value
        status = xlsheet.cell(row, 5).value
        pts_version = xlsheet.cell(row, 9).value
        if layer in ['GAP', 'GATT', 'L2CAP', 'SM'] and status == 'Ready':
            tc = xlsheet.cell(row, 1).value
            assert is_test_case_name(tc)
            test_case_names.add(tc)
    return test_case_names


def get_set_of_test_case_names_supported_by_autopts(stack_name):
    test_case_names = set()
    layers = ['GAP', 'GATT', 'L2CAP', 'SM']
    for layer in layers:
        tc_regex = re.compile(r'ZTestCase\("' + layer + r'",\s"(.*?)"')
        with open(f'../ptsprojects/{stack_name}/{layer.lower()}.py', 'r') as f:
            test_case_names.update(tc_regex.findall(f.read()))
    for tc in test_case_names:
        assert is_test_case_name(tc)
    return test_case_names


# Created a draft project in Launch Studio and copied over the ics entries from demant's qualification:
# https://launchstudio.bluetooth.com/ICSDetails/151074
# I then exported the test plan
z22_test_plan = get_set_of_test_case_names('./zephyr_2.2_test_plan.xlsx')

# Created a draft project in Launch Studio and copied over the ics entries from demant's qualification:
# https://launchstudio.bluetooth.com/ICSDetails/151074
# Then, to the best of my understanding, I added the new entries which correspond to the new features, check DRGN-14834
z24_test_plan = get_set_of_test_case_names('./zephyr_2.4_all_new_features_except_periodic_advertising_and_isochronous_channels.xlsx')

new_tests = z24_test_plan - z22_test_plan
print('z24_test_plan - z22_test_plan aka new tests')
print(sorted(list(new_tests)))

tests_supported_by_pts = get_set_of_test_case_names_supported_by_pts()
new_tests_not_supported_by_pts = new_tests - tests_supported_by_pts
print('new_tests_not_supported_by_pts')
print(sorted(list(new_tests_not_supported_by_pts)))

new_tests_supported_by_pts = new_tests.intersection(tests_supported_by_pts)
tests_supported_by_autopts_for_zephyr = get_set_of_test_case_names_supported_by_autopts('zephyr')
new_tests_not_supported_by_autopts_for_zephyr = new_tests_supported_by_pts - tests_supported_by_autopts_for_zephyr
print('new_tests_not_supported_by_autopts_for_zephyr')
print(sorted(list(new_tests_not_supported_by_autopts_for_zephyr)))

new_tests_supported_by_autopts_for_zephyr = new_tests_supported_by_pts.intersection(tests_supported_by_autopts_for_zephyr)
print('new_tests_supported_by_autopts')
print(sorted(list(new_tests_supported_by_autopts_for_zephyr)))

tests_supported_by_autopts_for_mynewt = get_set_of_test_case_names_supported_by_autopts('mynewt')
new_tests_not_supported_by_autopts_for_zephyr_but_supported_for_mynewt = new_tests_not_supported_by_autopts_for_zephyr.intersection(tests_supported_by_autopts_for_mynewt)
print('new_tests_not_supported_by_autopts_for_zephyr_but_supported_for_mynewt')
print(sorted(list(new_tests_not_supported_by_autopts_for_zephyr_but_supported_for_mynewt)))

new_tests_not_supported_by_autopts_for_zephyr_or_mynewt = new_tests_not_supported_by_autopts_for_zephyr - tests_supported_by_autopts_for_mynewt
print('new_tests_not_supported_by_autopts_for_zephyr_or_mynewt')
print(sorted(list(new_tests_not_supported_by_autopts_for_zephyr_or_mynewt)))

# Created a draft project in Launch Studio and copied over the ics entries from demant's qualification:
# https://launchstudio.bluetooth.com/ICSDetails/151074
# Then I simply bumped the spec version to v5.2, without adding any new features
required_tests = get_set_of_test_case_names('./zephyr_2.4_without_new_features.xlsx')
print('z24 test plan without adding new features aka required_tests')
print(sorted(list(required_tests)))

required_tests_not_supported_by_pts = required_tests - tests_supported_by_pts
print('required tests not supported by pts')
print(sorted(list(required_tests_not_supported_by_pts)))

required_tests_supported_by_pts = required_tests.intersection(tests_supported_by_pts)
required_tests_not_supported_by_autopts = required_tests_supported_by_pts - tests_supported_by_autopts_for_zephyr
print('required tests supported by pts but not implemented in autopts')
print(sorted(list(required_tests_not_supported_by_autopts)))

