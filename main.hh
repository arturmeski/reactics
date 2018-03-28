/*
    Copyright (c) 2012, 2013
    Artur Meski <meski@ipipan.waw.pl>

    Reuse of the code or its part for any purpose
    without the author's permission is strictly prohibited.
*/

#ifndef RS_MAIN_HH
#define RS_MAIN_HH

#include <iostream>
#include <string>
#include <iomanip>
#include <unistd.h>
#include <getopt.h>
#include <string.h>
#include "rs.hh"
#include "symrs.hh"
#include "mc.hh"
#include "rsin_driver.hh"
#include "options.hh"
#include "memtime.hh"

#define VERSION     "2.0 ALPHA"
#define AUTHOR      "Artur Meski <meski@ipipan.waw.pl>"
using std::cout;
using std::endl;

void print_help(std::string path_str);

#endif
