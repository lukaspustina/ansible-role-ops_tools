#!/usr/bin/python

################################################################################
#
# Collects a performance report of the host
# Author lukas.pustina
#
# Exit codes:
#  = 0 All individual reports have been successfully collected
#  > 0 one or more reports failed
#
################################################################################


import argparse
import sys
from subprocess import check_output, STDOUT, CalledProcessError
import multiprocessing



FACTS_COLLECTORS = [
    { "command": "hostname -f", "desc": "Hostname" },
    { "command": "date", "desc": "Now" },
    { "command": "cat /proc/cpuinfo | grep processor | wc -l", "desc": "Number of CPUs" },
    { "command": "cat /proc/meminfo | awk '/MemTotal/ { print $2 }'", "desc": "Total memory in kB" }
]

PERF_COLLECTORS = [
    { "command": "uptime" },
    { "command": "dmesg -T | tail" },
    { "command": "vmstat 1 5" },
    { "command": "mpstat -P ALL 1 5" },
    { "command": "pidstat -l 1 5" },
    { "command": "free -m" },
    { "command": "iostat -x 1 5" },
    { "command": "sar -n DEV 1 5" },
    { "command": "sar -n TCP,ETCP 1 5" }
]



def main():
    exit_code_sum = 0

    args = parse_args()

    exit_code_sum += print_facts_report()
    exit_code_sum += print_perf_reports( args.repeat, args.serial)
    exit_code_sum += print_footer()

    return exit_code_sum


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--repeat", help="repeat report collection REPEAT times -- must be int", type=int, default=1, required=None)
    parser.add_argument("-s", "--serial", help="run perf reports in a serial fashion", action='store_true')
    args = parser.parse_args()

    return args


def print_facts_report():
    ret_code_sum = 0
    print_output_header( "Host Facts" )

    for fc in FACTS_COLLECTORS:
        (output, command, ret_code) = run_shell_cmd( fc["command"] )
        ret_code_sum += ret_code

        print "* %s: `%s`" % ( fc["desc"], output.strip() )
    print

    return ret_code_sum


def print_output_header( msg="", size=1 ):
    print "".join(['#' for x in range(0, size)]), msg
    print


def run_shell_cmd( command ):
    try:
        output = check_output( command, stderr=STDOUT, shell=True )
        ret_code = 0
    except CalledProcessError as e:
        output = e.output
        ret_code = e.returncode

    return (output, command, ret_code)


def print_perf_reports( repeat, serial=False ):
    ret_code_sum = 0
    print_output_header( "Performance Reports" )

    print "**Content**"
    print
    for pc in PERF_COLLECTORS:
        print "*", pc["command"]
    print

    if not serial: print "**Attention**: Performance reports have been collected in parallel with the number of threads equal to the amount of CPU cores. This may have an implication on the results; especially on CPU related reports. Please keep that in mind."
    if repeat > 1: print "**Attention**: This report contains %d performance reports." % repeat

    for i in range(0, repeat):
        ret_code_sum += print_perf_report( serial )
    print

    return ret_code_sum


def print_perf_report( serial=False ):
    ret_code_sum = 0

    results = []

    if serial:
        pool = multiprocessing.Pool(processes=1)
    else:
        pool = multiprocessing.Pool()
    results = pool.map(run_shell_cmd, [c["command"] for c in PERF_COLLECTORS])

    for r in results:
        (output, command, ret_code) = r
        ret_code_sum += ret_code

        print_output_header( command, 2 )
        if ret_code != 0: print "Exit code:", ret_code

        print "```"
        print output
        print "```"
        print
    print

    return ret_code_sum


def print_footer():
    print "Please see [Linux Performance Analysis in 60,000 Milliseconds](http://techblog.netflix.com/2015_11_01_archive.html) for details about the individual reports."
    print

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

