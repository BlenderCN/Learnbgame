#!/usr/bin/env python

import datetime
import sys
import multiprocessing
import os
import subprocess


def run_sim(arglist):
    """ Run the MCell simulations. """

    mcell_binary, project_dir, base_name, error_file_option, log_file_option, seed = arglist
    mdl_filename = '%s.main.mdl' % (base_name)
    mdl_filepath = os.path.join(project_dir, mdl_filename)
    # Log filename will be log.year-month-day_hour:minute_seed.txt
    # (e.g. log.2013-03-12_11:45_1.txt)
    time_now = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M")
    log_filename = "log.%s_%d.txt" % (time_now, seed)
    error_filename = "error.%s_%d.txt" % (time_now, seed)
    log_filepath = os.path.join(project_dir, log_filename)
    error_filepath = os.path.join(project_dir, error_filename)

    if error_file_option == 'none':
        error_file = subprocess.DEVNULL
    elif error_file_option == 'console':
        error_file = None

    if log_file_option == 'none':
        log_file = subprocess.DEVNULL
    elif log_file_option == 'console':
        log_file = None

    print("Running: " + mcell_binary + " " + mdl_filepath)
    subprocess_cwd = os.path.dirname(mdl_filepath)
    print("  Should run from cwd = " +  subprocess_cwd)

    # Both output and error log file
    if (log_file_option == 'file' and error_file_option == 'file'):
        with open(log_filepath, "w") as log_file:
            with open (error_filepath, "w") as error_file:
                subprocess.call(
                    [mcell_binary, '-seed', '%d' % seed, mdl_filepath],
                    cwd=subprocess_cwd,
                    stdout=log_file, stderr=error_file)
    # Only output log file
    elif log_file_option == 'file':
        with open(log_filepath, "w") as log_file:
            subprocess.call(
                [mcell_binary, '-seed', '%d' % seed, mdl_filepath],
                cwd=subprocess_cwd,
                stdout=log_file, stderr=error_file)
    # Only error log file
    elif error_file_option == 'file':
        with open(error_filepath, "w") as error_file:
            subprocess.call(
                [mcell_binary, '-seed', '%d' % seed, mdl_filepath],
                cwd=subprocess_cwd,
                stdout=log_file, stderr=error_file)
    # Neither error nor output log
    else:
        subprocess.call(
            [mcell_binary, '-seed', '%d' % seed, mdl_filepath],
            cwd=subprocess_cwd, stdout=log_file, stderr=error_file)


if __name__ == "__main__":
    # Get the command line arguments (excluding the script name itself)
    mcell_binary, start_str, end_str, project_dir, base_name, \
        error_file_option, log_file_option, mcell_processes_str = sys.argv[1:]
    start = int(start_str)
    end = int(end_str)
    mcell_processes = int(mcell_processes_str)

    arglist = [[mcell_binary, project_dir, base_name, error_file_option, log_file_option, seed] for seed in range(start, end)]

    # Create a pool of mcell processes.
    pool = multiprocessing.Pool(processes=mcell_processes)
    pool.map(run_sim, arglist)
