
/* Based on MiniSat 1.14 */

#ifndef __MEMTIME_H__
#define __MEMTIME_H__

#include <sys/time.h>
#ifdef __WIN32__
#include <windows.h>
#include <psapi.h>
#else
#include <sys/resource.h>
#endif
#if defined(__APPLE__)
#include <malloc/malloc.h>
#endif
#include <stdio.h>
#include <unistd.h>
#include "macro.hh"

using namespace std;

typedef long long int64;

#ifdef __WIN32__

static inline double cpuTime() 
{
    FILETIME createTime, exitTime, kernelTime, userTime;

    if (!GetProcessTimes(GetCurrentProcess(), &createTime, &exitTime, &kernelTime, &userTime)) {
        return 0.0;
    }

    ULARGE_INTEGER u;
    u.LowPart = userTime.dwLowDateTime;
    u.HighPart = userTime.dwHighDateTime;

    return (double)u.QuadPart / 10e6;
}

#else

static inline double cpuTime(void)
{
  struct rusage ru;
  getrusage(RUSAGE_SELF, &ru);
  return (double)ru.ru_utime.tv_sec + (double)ru.ru_utime.tv_usec / 1000000;
}

#endif

static inline int memReadStat(void)
{
  char name[256];
  pid_t pid = getpid();
  sprintf(name, "/proc/%d/statm", pid);
  FILE *in = fopen(name, "rb");

  if (in == nullptr) {
    return 0;
  }

  int value;

  for (int field = 0; field >= 0; --field) {
    if (fscanf(in, "%d", &value) == EOF) {
      FERROR("EOF")
    }
  }

  fclose(in);
  return value;
}


#ifdef __WIN32__

static inline int64 memUsedInt64() 
{
    PROCESS_MEMORY_COUNTERS pmc;
    if (GetProcessMemoryInfo(GetCurrentProcess(), &pmc, sizeof(pmc))) {
        return (int64) pmc.WorkingSetSize;
    }
    
    return 0;
}

#else

static inline int64 memUsedInt64()
{
  return (int64)memReadStat() * (int64)getpagesize();
}

#endif

#if defined(__APPLE__)

static inline double memUsed()
{
  malloc_statistics_t t;
  malloc_zone_statistics(NULL, &t);
  return (double)t.max_size_in_use / (1024 * 1024);
}

#else

static inline double memUsed()
{
  return memUsedInt64() / (1024 * 1024);
}

#endif

#endif

