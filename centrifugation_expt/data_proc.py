#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
data_proc.py
Calculate and plot analyzed data from centrifugation experiment

Handles the primary functions
"""

import sys
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

SUCCESS = 0
INVALID_DATA = 1
IO_ERROR = 2

DEF_CSV_FILE = 'data.csv'
DEF_EXCEL_FILE = 'data.xlsx'


def warning(*objs):
    """Writes a message to stderr."""
    print("WARNING: ", *objs, file=sys.stderr)


def csv_data_analysis(csv_data_file):
    """
    Calculates solvent concentration. Finds aging time and g dried cake/g oil for each row

    Parameters
    ----------
    csv_data_file : excel file containing array of experiment data
        first row: solution information
        second row and below: each row contains data from a run of centrifugation
        (see README.md for more detailed description)

    Returns
    -------
    cent_data : numpy array
        first row: solvent concentration
        second row and below: each row contains columns of aging time (h), aging time (s),
        dried cake concentration (g/g oil)
    """

    data_array = pd.read_csv(csv_data_file, comment='#', header=None)
    # calculate solvent concentration
    solvent_conc = np.divide(np.subtract(data_array.loc[[0], [3]], data_array.loc[[0], [2]]),
                             np.subtract(data_array.loc[[0], [3]], data_array.loc[[0], [1]]))
    # find the start time of the experiment
    start_time = data_array.loc[[0], [0]].values

    # gather centrifugation data into separate arrays
    expt_array = data_array[[1, 2, 3]].iloc[1:]
    cent_time = data_array[[0]].iloc[1:]
    # assign variables to each column of expt_array
    empty_tube = expt_array[1]
    tube_liquid = expt_array[2]
    tube_dried_cake = expt_array[3]

    # calculate mass of tube contents
    mass_liquid = tube_liquid - empty_tube
    mass_dried_cake = tube_dried_cake - empty_tube
    mass_oil = (1-solvent_conc.iloc[0][3])*mass_liquid

    # calculate solution aging time at each centrifugation
    aging_time = [
        pd.to_datetime(cent_time.values[i, 0])-pd.to_datetime(start_time[0, 0])
        for i in range(len(cent_time.values))
    ]
    aging_time_sec = pd.Series(aging_time).dt.total_seconds()
    aging_time_hrs = aging_time_sec/3600

    # calculate dried cake concentration
    conc_dried_cake = mass_dried_cake/mass_oil

    cent_data = pd.concat([aging_time_hrs, aging_time_sec, conc_dried_cake.reset_index(drop=True)], axis=1)

    return cent_data


def excel_data_analysis(excel_data_file):
    """
    Calculates solvent concentration. Finds aging time in hrs and seconds, and g dried cake/g oil for each row.
    Works for excel file with multiple sheets

    Parameters
    ----------
    excel_data_file : excel file containing array of experiment data
        first row: solution information
        second row and below: each row contains data from a run of centrifugation
        (see README.md for more detailed description)
        data from an experiment in each sheet

    Returns
    -------
    cent_data : pandas DataFrame
        first row: solvent concentration
        second row and below: each row contains columns of aging time (h), aging time (s),
        dried cake concentration (g/g oil)
    """
    i = 0
    frame = None
    # Concatenate analyzed data from each sheet in excel file
    while i >= 0:
        try:
            calc_data = calcAndConc(excel_data_file, i)
            frame = pd.concat([frame, calc_data], axis=1)
            i = i + 1
        except:
            break

    cent_data = frame

    return cent_data


def calcAndConc(excel_data_file, i):
    """

    Calculates solvent concentration. Finds aging time in hrs and seconds, and g dried cake/g oil for each row.

    :param excel_data_file: excel file to read data from
    :param i: sheet number of excel file data will be pulled from
    :return: pandas DataFrame of aging time (hrs), aging time (sec), and dried cake conc (g/g oil) from data set
    of sheet i
    """

    all_data = pd.read_excel(excel_data_file, sheet_name=i)
    # Separate solvent addition data
    solvent_add_data = all_data.iloc[[0], [0, 1, 2, 3]]
    # Separate centrifugation data
    data_array = all_data.iloc[:, 4:8].dropna(0)

    # Calculate solvent concentration
    solvent_conc = np.divide(np.subtract(solvent_add_data.values[0, 3], solvent_add_data.values[0, 2]),
                             np.subtract(solvent_add_data.values[0, 3], solvent_add_data.values[0, 1]))
    # find the start time of the experiment
    start_time = solvent_add_data.values[0, 0]

    # gather centrifugation data into separate arrays
    expt_array = data_array.iloc[:, 1:4]
    cent_time = data_array.iloc[:, 0]
    # assign variables to each column of expt_array
    empty_tube = expt_array.values[:, 0]
    tube_liquid = expt_array.values[:, 1]
    tube_dried_cake = expt_array.values[:, 2]

    # calculate mass of tube contents
    mass_liquid = tube_liquid - empty_tube
    mass_dried_cake = tube_dried_cake - empty_tube
    mass_oil = (1-solvent_conc)*mass_liquid

    # calculate solution aging time at each centrifugation
    aging_time = cent_time - start_time
    aging_time_sec = pd.Series(aging_time).dt.total_seconds()
    aging_time_hrs = aging_time_sec/3600

    # calculate dried cake concentration
    conc_dried_cake = pd.Series(mass_dried_cake/mass_oil)

    cent_data = pd.concat([aging_time_hrs, aging_time_sec, conc_dried_cake], axis=1)
    cent_data.columns = [0, 1, 2]

    return cent_data


def parse_cmdline(argv):
    """
    Returns the parsed argument list and return code.
    `argv` is a list of arguments, or `None` for ``sys.argv[1:]``.
    """
    if argv is None:
        argv = sys.argv[1:]

    # initialize the parser object:
    parser = argparse.ArgumentParser()
    # add csv file as argument
    parser.add_argument("-c", "--csv_data_file", help="Location of csv file with data "
                                                      "from a single experiment to be analyzed",
                        default=DEF_CSV_FILE)
    parser.add_argument("-e", "--excel_data_file", help="Location of excel file with data "
                                                        "from multiple experiments to be analyzed",
                        default=DEF_EXCEL_FILE)

    args = parser.parse_args(argv)

    if args.excel_data_file == DEF_EXCEL_FILE:
        try:
            args.csv_data = pd.read_csv(args.csv_data_file)
        except IOError as e:
            warning("Problems reading file:", e)
            parser.print_help()
            return args, IO_ERROR
        except ValueError as e:
            warning("Read invalid data:", e)
            parser.print_help()
            return args, INVALID_DATA
    else:
        try:
            args.excel_data = pd.read_excel(args.excel_data_file)
        except ValueError as e:
            warning("Read invalid data:", e)
            parser.print_help()
            return args, INVALID_DATA

    return args, SUCCESS


def plot_csv(base_f_name, cent_data):

    plt.scatter(cent_data[0], cent_data[2])
    plt.title('Centrifugation Analysis')
    plt.xlabel('Aging Time (hrs)')
    plt.ylabel('Dried Cake Concentration (g/g oil)')
    plt.ylim(bottom=0)
    plt.xlim(left=0)
    out_name = base_f_name + "_csv" + ".png"
    plt.savefig(out_name)
    print("Wrote file: {}".format(out_name))


def plot_excel(base_f_name, cent_data):

    new_columns = np.linspace(0, int(len(cent_data.columns))-1, int(len(cent_data.columns)), dtype=int)
    cent_data.columns = [new_columns]
    data_list = [None]*(int(len(cent_data.columns)/3))

    for i in range(int(len(cent_data.columns)/3)):
        data_list[i] = cent_data.iloc[:, 3*i:3*i+3].dropna()

    for i in range(int(len(cent_data.columns)/3)):
        plt.scatter(data_list[i].iloc[:, 0], data_list[i].iloc[:, 2], label='Data' + str(i+1))

    plt.title('Centrifugation Analysis')
    plt.xlabel('Aging Time (hrs)')
    plt.ylabel('Dried Cake Concentration (g/g oil)')
    plt.ylim(bottom=0)
    plt.xlim(left=0)
    plt.legend(loc="best")
    out_name = base_f_name + "_excel" + ".png"
    plt.savefig(out_name)
    print("Wrote file: {}".format(out_name))


def main(argv=None):
    args, ret = parse_cmdline(argv)
    if ret != SUCCESS:
        return ret

    if args.csv_data_file != DEF_CSV_FILE:
        cent_data_csv = csv_data_analysis(args.csv_data_file)
        # get the name of the input file without the directory it is in, if one was specified
        base_out_fname = os.path.basename(args.csv_data_file)
        # get the first part of the file name (omit extension) and add the suffix
        base_out_fname = os.path.splitext(base_out_fname)[0] + '_analysis'
        # add suffix and extension
        out_fname = base_out_fname + '.csv'
        np.savetxt(out_fname, cent_data_csv, delimiter=',')
        print("Wrote file: {}".format(out_fname))

        # send the base_out_fname and data to a new function that will plot the data
        plot_csv(base_out_fname, cent_data_csv)

    else:
        cent_data_excel = excel_data_analysis(args.excel_data_file)
        # get the name of the input file without the directory it is in, if one was specified
        base_out_fname = os.path.basename(args.excel_data_file)
        # get the first part of the file name (omit extension) and add the suffix
        base_out_fname = os.path.splitext(base_out_fname)[0] + '_analysis'
        # add suffix and extension
        out_fname = base_out_fname + '.xlsx'

        writer = pd.ExcelWriter(out_fname)

        for i in range(int(len(cent_data_excel.columns)/3)):
            written = cent_data_excel.iloc[:, 3*i:3*i+3].dropna()
            written.to_excel(writer, 'Sheet' + str(i+1))

        writer.save()
        print("Wrote file: {}".format(out_fname))

        # send the base_out_fname and data to a new function that will plot the data
        plot_excel(base_out_fname, cent_data_excel)

    return SUCCESS  # success


if __name__ == "__main__":
    status = main()
    sys.exit(status)
