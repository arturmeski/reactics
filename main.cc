/*
    Copyright (c) 2012-2014
    Artur Meski <meski@ipipan.waw.pl>

    Reuse of the code or its part for any purpose
    without the author's permission is strictly prohibited.
*/

#include "main.hh"

int main(int argc, char **argv)
{
  rsin_driver driver;

  Options *opts = new Options;
  driver.setOptions(opts);

  bool show_reactions = false;
  bool rstl_model_checking = false;
  bool reach_states = false;
  bool reach_states_succ = false;
  bool bmc = true;
  bool benchmarking = false;
  bool usage_error = false;
  bool print_parsed_sys = false;

  static struct option long_options[] = {
    {"trace-parsing",   no_argument,    0, 0   },
    {"trace-scanning",  no_argument,    0, 0   },
    {0,                 0,              0, 0   }
  };

  int c;
  int option_index = 0;

  while ((c = getopt_long(argc, argv, "cbBmpPrsStTvxzh", long_options,
                          &option_index)) != -1) {
    switch (c) {
      case 0:
        printf("option %s", long_options[option_index].name);

        if (optarg) {
          printf(" with arg %s", optarg);
        }

        printf("\n");

        if (strcmp(long_options[option_index].name, "trace-parsing")) {
          driver.trace_parsing = true;
        }
        else if (strcmp(long_options[option_index].name, "trace-scanning")) {
          driver.trace_scanning = true;
        }

        break;

      //case 'b':
      //    printf("-b with %s\n", optarg);
      //    break;
      case 'b':
        bmc = false;
        break;

      case 'p':
        opts->show_progress = true;
        break;

      case 'P':
        print_parsed_sys = true;
        break;

      case 'r':
        show_reactions = true;
        break;

      case 'c':
        rstl_model_checking = true;
        break;

      case 'm':
        opts->measure = true;
        break;

      case 'B':
        benchmarking = true;
        opts->measure = true;
        break;

      case 's':
        reach_states = true;
        break;

      case 't':
        reach_states_succ = true;
        break;

      case 'v':
        opts->verbose++;
        break;

      case 'x':
        opts->part_tr_rel = true;
        break;

      case 'z':
        opts->reorder_reach = true;
        opts->reorder_trans = true;
        break;

      case 'h':
        usage_error = true;
        break;

      default:
        usage_error = true;
        break;
    }
  }

  std::string inputfile;

  if (optind < argc) {
    inputfile = argv[optind];
  }
  else {
    cout << "Missing input file" << endl;
    usage_error = true;
  }

  if (usage_error) {
    print_help(std::string(argv[0]));
    return 100;
  }

  if (!(reach_states || reach_states_succ || rstl_model_checking
        || show_reactions || print_parsed_sys)) {
    FERROR("No task specified: -c, -P, -r, or -s needs to be used");
  }

  if (opts->verbose > 0) {
    cout << "Verbose level: " << opts->verbose << endl;
  }

  VERB("Parsing " << inputfile);

  if (driver.parse(inputfile)) {
    FERROR("Parse error");
  }

  //
  // Here we retrieve the reaction system from the parser
  //
  // We decide which RS will be used at the parser level.
  // This decision depends on whether we use concentrations,
  // context automaton, etc.
  //
  auto rs = *driver.getReactionSystem();

  rs.setOptions(opts); // these need to be passed to the driver

  if (show_reactions) {
    rs.showReactions();
  }

  if (print_parsed_sys) {
    rs.printSystem();
  }

  if (reach_states || reach_states_succ || rstl_model_checking) {
    SymRS srs(&rs, opts);

    ModelChecker mc(&srs, opts);

    if (reach_states) {
      mc.printReach();
    }

    if (reach_states_succ) {
      mc.printReachWithSucc();
    }

    if (rstl_model_checking) {
      if (bmc) {
        cout << "Using BDD-based Bounded Model Checking" << endl;
        mc.checkRSCTL(driver.getFormRSCTL());
      }
      else {
        mc.checkRSCTLfull(driver.getFormRSCTL());
      }
    }
  }

  if (opts->measure) {
    cout << endl << std::setprecision(4)
         << "Encoding time: " << opts->enc_time << " sec" << endl
         << "Verification time: " << opts->ver_time << " sec" << endl
         << "Encoding memory: " << opts->enc_mem << " MB" << endl
         << "Memory (total): " << opts->ver_mem << " MB" << endl
         << "TOTAL time: " << opts->enc_time + opts->ver_time << " sec" << endl;

    if (benchmarking) {
      cout << std::setprecision(4)
           << "STAT; " << opts->enc_time
           << " ; " << opts->ver_time
           << " ; " << opts->enc_mem
           << " ; " << opts->ver_mem
           << " ; " << opts->enc_time + opts->ver_time << endl;

    }
  }

  delete opts;

  return 0;
}

void print_help(std::string path_str)
{
  cout << endl
       << " ------------------------------------" << endl
       << " -- Reaction Systems Model Checker --" << endl
       << " ------------------------------------" << endl
       << endl
       << "   Version:   " << VERSION << endl
       << "   Contact:   " << AUTHOR << endl
       << endl
#ifndef PUBLIC_RELEASE
       << " ###################################" << endl
       << "  THIS IS A PRIVATE VERSION OF RSMC " << endl
       << "     PLEASE, DO NOT DISTRIBUTE      " << endl
       << " ###################################" << endl
       << endl
#endif
       << " Usage: " << path_str << " [options] <inputfile>" << endl << endl
       << " TASKS:" << endl
       << "  -c   -- perform RSCTL model checking" << endl
       //<< " -f K -- generate SMT input for the depth K" << endl
       << "  -P   -- print parsed system" << endl
       << "  -r   -- print reactions" << endl
       << "  -s   -- print the set of all the reachable states" << endl
       << "  -t   -- print the set of all the reachable states with their successors"
       << endl
       << endl << " OTHER:" << endl
       << "  -b   -- disable bounded model checking (BMC) heuristic" << endl
       << "  -x   -- use partitioned transition relation (may use less memory)" <<
       endl
       << "  -z   -- use reordering of the BDD variables" << endl
       << "  -v   -- verbose (can be used more than once to increase verbosity)" <<
       endl
       << "  -p   -- show progress (where possible)" << endl
       << endl
       << " Benchmarking options:" << endl
       << "  -m   -- measure and display time and memory usage" << endl
       << "  -B   -- display an easy to parse summary (enables -m)" << endl
       << endl;
}

/** EOF **/

