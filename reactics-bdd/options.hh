#ifndef RS_OPTIONS_HH
#define RS_OPTIONS_HH

class Options
{

  public:
    unsigned int verbose;
    bool show_progress;
    bool measure;
    bool part_tr_rel;
    bool reorder_reach;
    bool reorder_trans;
    bool backend_mode;

    double enc_time;
    double enc_mem;
    double ver_time;
    double ver_mem;

    Options(void)
    {
      verbose = 0;
      show_progress = false;
      measure = false;

      part_tr_rel = true;

      reorder_reach = true;
      reorder_trans = true;

      backend_mode = false;

      enc_time = 0;
      enc_mem = 0;
      ver_time = 0;
      ver_mem = 0;
    }
};

#endif
