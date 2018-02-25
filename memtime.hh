/**************************************************************************
 *                                                                        *
 *  This file is a part of BMC4LTLK,                                      *
 *  a program for Bounded Model Checking of LTLK.                         *
 *                                                                        *
 *  Copyright (C) 2002-2010 Andrzej Zbrzezny <a.zbrzezny@gmail.com>       *
 *                                                                        *
 *  This program is released under the terms of the license contained     *
 *  in the file LICENSE.                                                  *
 *                                                                        *
 **************************************************************************/

/* WARNING: LICENSE VIOLATION. THIS PROGRAM IS USED FOR TEST PURPOSES ONLY
 *          THIS CODE WILL BE REPLACED BEFORE ANY RELEASE!!!!
 */

/* Based on MiniSat 1.14 */

#ifndef __MEMTIME_H__
#define __MEMTIME_H__

#include <sys/time.h>
#include <sys/resource.h>
#include <stdio.h>
#include <unistd.h>
#include "macro.hh"

typedef long long int64;

static inline double cpuTime(void)
{
    struct rusage ru;
    getrusage(RUSAGE_SELF, &ru);
    return (double)ru.ru_utime.tv_sec + (double)ru.ru_utime.tv_usec / 1000000;
}

static inline int memReadStat(void)
{
    char name[256];
    pid_t pid = getpid();
    sprintf(name, "/proc/%d/statm", pid);
    FILE* in = fopen(name, "rb");
    if (in == nullptr)
    {
        return 0;
    }
    int value;
    for (int field = 0; field >= 0; --field)
    {
        if (fscanf(in, "%d", &value) == EOF)
            FERROR("EOF");
    }
    fclose(in);
    return value;
}

static inline int64 memUsedInt64()
{
    return (int64)memReadStat() * (int64)getpagesize();
}

static inline double memUsed()
{
    return memUsedInt64() / 1048576.0;
}

#endif
