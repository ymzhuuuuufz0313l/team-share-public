#set SNPS_DIR "/eda/synopsys/syn_vH_2013"
set SNPS_DIR "/eda/synopsys/syn1506"
set SNPS_LIB_DIR [format "%s%s" $SNPS_DIR "/libraries/syn"]

if {$synopsys_program_name != "pt_shell"} {
  if {[regexp {_40_} $LINK_LIB]} {
    set PVT  "ss0p99v125c"
    set PVTM "ss0p99v125c"
    set MEM_PVT  "ss0p99v125c"
    set MEM_PVTM "ss0p99v125c"
    set PVT_IO "ss0p99v125c"
#    set MEM_PVT  "ss1p08v125c"
#    set MEM_PVTM "ss1p08v125c"

  } elseif { [regexp {_28_} $LINK_LIB]} {
    set PVT  "ss_cworst_max_0p81v_125c"
    set PVTM "ssg_0p81v_0p81v_125c"
    set PVT40 "ss0p99v125c"
    set PVT_IO "ss_cworst_max_0p81v_125c"
    set CORNER "wc_cworst"
  } elseif { [regexp {_28p_arm_} $LINK_LIB]} {
    set PVT  "ssg_cworstt_max_0p81v_m40c"
    set PVTM "ssg_cworstt_0p81v_0p81v_m40c"
    set MEM_PVT "ssg_cworstt_0p81v_0p81v_m40c"
    set MEM_PVTM "ssg_cworstt_0p81v_0p81v_m40c"
    set PVT40 ""
    set PVT_IO "ssg_cworstt_max_0p81v_m40c"
    set PVT_ANA "ssg_0p81v_m40c"
    set CORNER "wc_cworst"
  } elseif { [regexp {_28p_snps_} $LINK_LIB]} {
    set PVT  "ssgwc0p81vn40c"
    set PVTM "ssgwc0p81vn40c"
    set MEM_PVT "ssgwc0p81vn40c"
    set MEM_PVTM "ssgwc0p81vn40c"
    set PVT40 "ss0p99v125c"
    set PVT_IO "ssg_cworstt_max_0p81v_m40c"
    set PVT_ANA "ssg_0p81v_m40c"
    set CORNER "wcl_cworst"
  } elseif { [regexp {_55_} $LINK_LIB]} {
    set PVT  "ss1p08v125c"
    set PVTM "ss1p08v125c"
    set PVT_IO "ss2p97v125c"
    set MEM_PVT  "ss1p08v125c"
    set MEM_PVTM "ss1p08v125c"
    set CORNER "wc_cworst"
  } elseif { [regexp {tsmc_22ulp_} $LINK_LIB]} {
    set PVT  "ssg0p81vn40c"
    set PVTM "ssg0p81vm40c"
    set MEM_PVT "ssgwct0p81vn40c"
    set MEM_PVTM "ssgwct0p81vm40c"
    set PVT40 "ss0p99v125c"
    set PVT_IO "ssg0p81v1p62vm40c"
    set PVT_ANA "ssg0p81vm40c"
    set PVT_DDR "ss0p81vn40c_Cworst_pg"
    set PVT_DDR_UTILS "ss0p81vn40c_pg"
    set CORNER "wcl_cworst"
    set PVT_MACRO "wcl_cmax_m40_setup"
  } else {
    set PVT  ""
    set PVTM ""
    set MEM_PVT  ""
    set MEM_PVTM ""
    set CORNER "wc_cworst"
  }
} else {
  if {[regexp {_40_} $LINK_LIB]} {

    if {$CORNER == "wc_cworst"      }  { set PVT_IO "ss0p99v125c"  }
    if {$CORNER == "wc_rcworst_max" }  { set PVT_IO "ss0p99v125c"  }
    if {$CORNER == "wc_rcworst_min" }  { set PVT_IO "ss0p99v125c"  }
    if {$CORNER == "wcl_cworst"     }  { set PVT_IO "ss0p99vn40c"  }
    if {$CORNER == "lt_cbest"       }  { set PVT_IO "ff1p21vn40c"  }
    if {$CORNER == "ml_cbest"       }  { set PVT_IO "ff1p21v125c"  }
    if {$CORNER == "lt_cbest_26"    }  { set PVT_IO "ff1p26vn40c"  }
    if {$CORNER == "ml_cbest_26"    }  { set PVT_IO "ff1p26v125c"  }


    if {$CORNER == "wc_cworst"      }  { set PVT  "ss0p99v125c"    }
    if {$CORNER == "wc_rcworst_max" }  { set PVT  "ss0p99v125c"    }
    if {$CORNER == "wc_rcworst_min" }  { set PVT  "ss0p99v125c"    }
    if {$CORNER == "wcl_cworst"     }  { set PVT  "ss0p99vn40c"    }
    if {$CORNER == "lt_cbest"       }  { set PVT  "ff1p21vn40c"    }
    if {$CORNER == "ml_cbest"       }  { set PVT  "ff1p21v125c"    }
    if {$CORNER == "lt_cbest_26"    }  { set PVT  "ff1p26vn40c"    }    
    if {$CORNER == "ml_cbest_26"    }  { set PVT  "ff1p26v125c"    }    
    if {$CORNER == "wc_cworst"      }  { set PVTM "ss0p99v125c"    }
    if {$CORNER == "wc_rcworst_max" }  { set PVTM "ss0p99v125c"    }
    if {$CORNER == "wc_rcworst_min" }  { set PVTM "ss0p99v125c"    }
    if {$CORNER == "wcl_cworst"     }  { set PVTM "ss0p99vm40c"    }
    if {$CORNER == "lt_cbest"       }  { set PVTM "ff1p21vm40c"    }
    if {$CORNER == "ml_cbest"       }  { set PVTM "ff1p21v125c"    }
    if {$CORNER == "lt_cbest_26"    }  { set PVTM "ff1p26vm40c"    }   
    if {$CORNER == "ml_cbest_26"    }  { set PVTM "ff1p26v125c"    }


    if {$CORNER == "wc_cworst"      }  { set MEM_PVT  "ss0p99v125c"    }
    if {$CORNER == "wc_rcworst_max" }  { set MEM_PVT  "ss0p99v125c"    }
    if {$CORNER == "wc_rcworst_min" }  { set MEM_PVT  "ss0p99v125c"    }
    if {$CORNER == "wcl_cworst"     }  { set MEM_PVT  "ss0p99vn40c"    }
    if {$CORNER == "lt_cbest"       }  { set MEM_PVT  "ff1p21vn40c"    }
    if {$CORNER == "ml_cbest"       }  { set MEM_PVT  "ff1p21v125c"    }
    if {$CORNER == "lt_cbest_26"    }  { set MEM_PVT  "ff1p21vm40c"    }    
    if {$CORNER == "ml_cbest_26"    }  { set MEM_PVT  "ff1p21v125c"    }    
    if {$CORNER == "wc_cworst"      }  { set MEM_PVTM "ss0p99v125c"    }
    if {$CORNER == "wc_rcworst_max" }  { set MEM_PVTM "ss0p99v125c"    }
    if {$CORNER == "wc_rcworst_min" }  { set MEM_PVTM "ss0p99v125c"    }
    if {$CORNER == "wcl_cworst"     }  { set MEM_PVTM "ss0p99vm40c"    }
    if {$CORNER == "lt_cbest"       }  { set MEM_PVTM "ff1p21vm40c"    }
    if {$CORNER == "ml_cbest"       }  { set MEM_PVTM "ff1p21v125c"    }
    if {$CORNER == "lt_cbest_26"    }  { set MEM_PVTM "ff1p21vm40c"    }   
    if {$CORNER == "ml_cbest_26"    }  { set MEM_PVTM "ff1p21v125c"    }

    if {$CORNER == "wc_cworst"      }  { set RC_FILE "cworst_125"  }
    if {$CORNER == "wc_rcworst_max" }  { set RC_FILE "rcworst_125" }
    if {$CORNER == "wc_rcworst_min" }  { set RC_FILE "rcworst_125" }
    if {$CORNER == "wcl_cworst"     }  { set RC_FILE "cworst_m40"  }
    if {$CORNER == "lt_cbest"       }  { set RC_FILE "cbest_m40"   }
    if {$CORNER == "ml_cbest"       }  { set RC_FILE "cbest_125"   }
    if {$CORNER == "lt_cbest_26"    }  { set RC_FILE "cbest_m40"   }
    if {$CORNER == "ml_cbest_26"    }  { set RC_FILE "cbest_125"   }
  } elseif { [regexp {_55_} $LINK_LIB]} {

    if {$CORNER == "wc_cworst"      }  { set PVT_IO "ss2p97v125c"    }
    if {$CORNER == "wc_rcworst_max" }  { set PVT_IO "ss2p97v125c"    }
    if {$CORNER == "wc_rcworst_min" }  { set PVT_IO "ss2p97v125c"    }
    if {$CORNER == "wcl_cworst"     }  { set PVT_IO "ss1p08vn40c"    }
    if {$CORNER == "lt_cbest"       }  { set PVT_IO "ff3p63vn40c"    }
    if {$CORNER == "ml_cbest"       }  { set PVT_IO "ff3p63v125c"    }

    if {$CORNER == "wc_cworst"      }  { set PVT  "ss1p08v125c"    }
    if {$CORNER == "wc_rcworst_max" }  { set PVT  "ss1p08v125c"    }
    if {$CORNER == "wc_rcworst_min" }  { set PVT  "ss1p08v125c"    }
    if {$CORNER == "wcl_cworst"     }  { set PVT  "ss1p08vm40c"    }
    if {$CORNER == "lt_cbest"       }  { set PVT  "ff1p32vm40c"    }
    if {$CORNER == "ml_cbest"       }  { set PVT  "ff1p32v125c"    }
    if {$CORNER == "wc_cworst"      }  { set PVTM "ss1p08v125c"    }
    if {$CORNER == "wc_rcworst_max" }  { set PVTM "ss1p08v125c"    }
    if {$CORNER == "wc_rcworst_min" }  { set PVTM "ss1p08v125c"    }
    if {$CORNER == "wcl_cworst"     }  { set PVTM "ss1p08vm40c"    }
    if {$CORNER == "lt_cbest"       }  { set PVTM "ss1p08vm40c"    }
    if {$CORNER == "ml_cbest"       }  { set PVTM "ff1p32v125c"    }

    if {$CORNER == "wc_cworst"      }  { set MEM_PVT  "ss1p08v125c"    }
    if {$CORNER == "wc_rcworst_max" }  { set MEM_PVT  "ss1p08v125c"    }
    if {$CORNER == "wc_rcworst_min" }  { set MEM_PVT  "ss1p08v125c"    }
    if {$CORNER == "wcl_cworst"     }  { set MEM_PVT  "ss1p08vn40c"    }
    if {$CORNER == "lt_cbest"       }  { set MEM_PVT  "ff1p32vn40c"    }
    if {$CORNER == "ml_cbest"       }  { set MEM_PVT  "ff1p32v125c"    }
    if {$CORNER == "wc_cworst"      }  { set MEM_PVTM "ss1p08v125c"    }
    if {$CORNER == "wc_rcworst_max" }  { set MEM_PVTM "ss1p08v125c"    }
    if {$CORNER == "wc_rcworst_min" }  { set MEM_PVTM "ss1p08v125c"    }
    if {$CORNER == "wcl_cworst"     }  { set MEM_PVTM "ss1p08vn40c"    }
    if {$CORNER == "lt_cbest"       }  { set MEM_PVTM "ss1p08vn40c"    }
    if {$CORNER == "ml_cbest"       }  { set MEM_PVTM "ff1p32v125c"    }

    if {$CORNER == "wc_cworst"      }  { set RC_FILE "cworst_125"  }
    if {$CORNER == "wc_rcworst_max" }  { set RC_FILE "rcworst_125" }
    if {$CORNER == "wc_rcworst_min" }  { set RC_FILE "rcworst_125" }
    if {$CORNER == "wcl_cworst"     }  { set RC_FILE "cworst_m40"  }
    if {$CORNER == "lt_cbest"       }  { set RC_FILE "cbest_m40"   }
    if {$CORNER == "ml_cbest"       }  { set RC_FILE "cbest_125"   }
  } elseif { [regexp {_28_} $LINK_LIB]} {

    if {$CORNER == "wc_cworst"      }  { set PVT_IO "ss_cworst_max_0p81v_125c"    }
    if {$CORNER == "wc_rcworst_max" }  { set PVT_IO "ss_cworst_max_0p81v_125c"    }
    if {$CORNER == "wc_rcworst_min" }  { set PVT_IO "ss_cworst_max_0p81v_125c"    }
    if {$CORNER == "wcl_cworst"     }  { set PVT_IO "ss_cworst_max_0p81v_m40c"    }
    if {$CORNER == "lt_cbest"       }  { set PVT_IO "ff_cbest_min_0p99v_m40c"    }
    if {$CORNER == "ml_cbest"       }  { set PVT_IO "ff_cbest_min_0p99v_125c"    }


    if {$CORNER == "wc_cworst"      }  { set PVT  "ss_cworst_max_0p81v_125c"    }
    if {$CORNER == "wc_rcworst_max" }  { set PVT  "ss_cworst_max_0p81v_125c"    }
    if {$CORNER == "wc_rcworst_min" }  { set PVT  "ss_cworst_max_0p81v_125c"    }
    if {$CORNER == "wcl_cworst"     }  { set PVT  "ss_cworst_max_0p81v_m40c"    }
    if {$CORNER == "lt_cbest"       }  { set PVT  "ff_cbest_min_0p99v_m40c"    }
    if {$CORNER == "ml_cbest"       }  { set PVT  "ff_cbest_min_0p99v_125c"    }
    if {$CORNER == "wc_cworst"      }  { set PVTM "ssg_0p81v_0p81v_125c"    }
    if {$CORNER == "wc_rcworst_max" }  { set PVTM "ssg_0p81v_0p81v_125c"    }
    if {$CORNER == "wc_rcworst_min" }  { set PVTM "ssg_0p81v_0p81v_125c"    }
    if {$CORNER == "wcl_cworst"     }  { set PVTM "ssg_0p81v_0p81v_m40c"    }
    if {$CORNER == "lt_cbest"       }  { set PVTM "ff_0p99v_0p99v_m40c"    }
    if {$CORNER == "ml_cbest"       }  { set PVTM "ff_0p99v_0p99v_125c"    }
    if {$CORNER == "wc_cworst"      }  { set RC_FILE "cworst_125"  }
    if {$CORNER == "wc_rcworst_max" }  { set RC_FILE "rcworst_125" }
    if {$CORNER == "wc_rcworst_min" }  { set RC_FILE "rcworst_125" }
    if {$CORNER == "wcl_cworst"     }  { set RC_FILE "cworst_m40"  }
    if {$CORNER == "lt_cbest"       }  { set RC_FILE "cbest_m40"   }
    if {$CORNER == "ml_cbest"       }  { set RC_FILE "cbest_125"   }
  } elseif { [regexp {_28p_arm_} $LINK_LIB]} {

    if {$CORNER == "wc_cmax_125_setup"  }  { set PVT_IO "ssg_cworstt_max_0p81v_125c"    }
    if {$CORNER == "wc_rcmax_125_setup" }  { set PVT_IO "ssg_cworstt_max_0p81v_125c"    }
    if {$CORNER == "wcl_cmax_m40_setup" }  { set PVT_IO "ssg_cworstt_max_0p81v_m40c"    }
    if {$CORNER == "wcl_rcmax_m40_setup"}  { set PVT_IO "ssg_cworstt_max_0p81v_m40c"    }
    if {$CORNER == "wc_cmax_125_hold"   }  { set PVT_IO "ssg_cworstt_max_0p81v_125c"    }
    if {$CORNER == "wc_rcmax_125_hold"  }  { set PVT_IO "ssg_cworstt_max_0p81v_125c"    }
    if {$CORNER == "wcl_cmax_m40_hold"  }  { set PVT_IO "ssg_cworstt_max_0p81v_m40c"    }
    if {$CORNER == "wcl_rcmax_m40_hold" }  { set PVT_IO "ssg_cworstt_max_0p81v_m40c"    }
    if {$CORNER == "wc_cmin_125_hold"   }  { set PVT_IO "ssg_cworstt_max_0p81v_125c"    }
    if {$CORNER == "wc_rcmin_125_hold"  }  { set PVT_IO "ssg_cworstt_max_0p81v_125c"    }
    if {$CORNER == "wcl_cmin_m40_hold"  }  { set PVT_IO "ssg_cworstt_max_0p81v_m40c"    }
    if {$CORNER == "wcl_rcmin_m40_hold" }  { set PVT_IO "ssg_cworstt_max_0p81v_m40c"    }
    if {$CORNER == "lt_cmax_m40_hold"   }  { set PVT_IO "ffg_cbestt_min_0p99v_m40c"     }
    if {$CORNER == "lt_rcmax_m40_hold"  }  { set PVT_IO "ffg_cbestt_min_0p99v_m40c"     }
    if {$CORNER == "ml_cmax_125_hold"   }  { set PVT_IO "ffg_cbestt_min_0p99v_125c"     }
    if {$CORNER == "ml_rcmax_125_hold"  }  { set PVT_IO "ffg_cbestt_min_0p99v_125c"     }
    if {$CORNER == "lt_cmin_m40_hold"   }  { set PVT_IO "ffg_cbestt_min_0p99v_m40c"     }
    if {$CORNER == "lt_rcmin_m40_hold"  }  { set PVT_IO "ffg_cbestt_min_0p99v_m40c"     }
    if {$CORNER == "ml_cmin_125_hold"   }  { set PVT_IO "ffg_cbestt_min_0p99v_125c"     }
    if {$CORNER == "ml_rcmin_125_hold"  }  { set PVT_IO "ffg_cbestt_min_0p99v_125c"     }

    if {$CORNER == "wc_cmax_125_setup"  }  { set PVT_ANA "ssg_0p81v_125c"    }
    if {$CORNER == "wc_rcmax_125_setup" }  { set PVT_ANA "ssg_0p81v_125c"    }
    if {$CORNER == "wcl_cmax_m40_setup" }  { set PVT_ANA "ssg_0p81v_m40c"    }
    if {$CORNER == "wcl_rcmax_m40_setup"}  { set PVT_ANA "ssg_0p81v_m40c"    }
    if {$CORNER == "wc_cmax_125_hold"   }  { set PVT_ANA "ssg_0p81v_125c"    }
    if {$CORNER == "wc_rcmax_125_hold"  }  { set PVT_ANA "ssg_0p81v_125c"    }
    if {$CORNER == "wcl_cmax_m40_hold"  }  { set PVT_ANA "ssg_0p81v_m40c"    }
    if {$CORNER == "wcl_rcmax_m40_hold" }  { set PVT_ANA "ssg_0p81v_m40c"    }
    if {$CORNER == "wc_cmin_125_hold"   }  { set PVT_ANA "ssg_0p81v_125c"    }
    if {$CORNER == "wc_rcmin_125_hold"  }  { set PVT_ANA "ssg_0p81v_125c"    }
    if {$CORNER == "wcl_cmin_m40_hold"  }  { set PVT_ANA "ssg_0p81v_m40c"    }
    if {$CORNER == "wcl_rcmin_m40_hold" }  { set PVT_ANA "ssg_0p81v_m40c"    }
    if {$CORNER == "lt_cmax_m40_hold"   }  { set PVT_ANA "ffg_0p99v_m40c"    }
    if {$CORNER == "lt_rcmax_m40_hold"  }  { set PVT_ANA "ffg_0p99v_m40c"    }
    if {$CORNER == "ml_cmax_125_hold"   }  { set PVT_ANA "ffg_0p99v_125c"    }
    if {$CORNER == "ml_rcmax_125_hold"  }  { set PVT_ANA "ffg_0p99v_125c"    }
    if {$CORNER == "lt_cmin_m40_hold"   }  { set PVT_ANA "ffg_0p99v_m40c"    }
    if {$CORNER == "lt_rcmin_m40_hold"  }  { set PVT_ANA "ffg_0p99v_m40c"    }
    if {$CORNER == "ml_cmin_125_hold"   }  { set PVT_ANA "ffg_0p99v_125c"    }
    if {$CORNER == "ml_rcmin_125_hold"  }  { set PVT_ANA "ffg_0p99v_125c"    }

    if {$CORNER == "wc_cmax_125_setup"  }  { set PVT    "ssg_cworstt_max_0p81v_125c"    }
    if {$CORNER == "wc_rcmax_125_setup" }  { set PVT    "ssg_cworstt_max_0p81v_125c"    }
    if {$CORNER == "wcl_cmax_m40_setup" }  { set PVT    "ssg_cworstt_max_0p81v_m40c"    }
    if {$CORNER == "wcl_rcmax_m40_setup"}  { set PVT    "ssg_cworstt_max_0p81v_m40c"    }
    if {$CORNER == "wc_cmax_125_hold"   }  { set PVT    "ssg_cworstt_max_0p81v_125c"    }
    if {$CORNER == "wc_rcmax_125_hold"  }  { set PVT    "ssg_cworstt_max_0p81v_125c"    }
    if {$CORNER == "wcl_cmax_m40_hold"  }  { set PVT    "ssg_cworstt_max_0p81v_m40c"    }
    if {$CORNER == "wcl_rcmax_m40_hold" }  { set PVT    "ssg_cworstt_max_0p81v_m40c"    }
    if {$CORNER == "wc_cmin_125_hold"   }  { set PVT    "ssg_cworstt_max_0p81v_125c"    }
    if {$CORNER == "wc_rcmin_125_hold"  }  { set PVT    "ssg_cworstt_max_0p81v_125c"    }
    if {$CORNER == "wcl_cmin_m40_hold"  }  { set PVT    "ssg_cworstt_max_0p81v_m40c"    }
    if {$CORNER == "wcl_rcmin_m40_hold" }  { set PVT    "ssg_cworstt_max_0p81v_m40c"    }
    if {$CORNER == "lt_cmax_m40_hold"   }  { set PVT    "ffg_cbestt_min_0p99v_m40c"     }
    if {$CORNER == "lt_rcmax_m40_hold"  }  { set PVT    "ffg_cbestt_min_0p99v_m40c"     }
    if {$CORNER == "ml_cmax_125_hold"   }  { set PVT    "ffg_cbestt_min_0p99v_125c"     }
    if {$CORNER == "ml_rcmax_125_hold"  }  { set PVT    "ffg_cbestt_min_0p99v_125c"     }
    if {$CORNER == "lt_cmin_m40_hold"   }  { set PVT    "ffg_cbestt_min_0p99v_m40c"     }
    if {$CORNER == "lt_rcmin_m40_hold"  }  { set PVT    "ffg_cbestt_min_0p99v_m40c"     }
    if {$CORNER == "ml_cmin_125_hold"   }  { set PVT    "ffg_cbestt_min_0p99v_125c"     }  
    if {$CORNER == "ml_rcmin_125_hold"  }  { set PVT    "ffg_cbestt_min_0p99v_125c"     }  

    if {$CORNER == "wc_cmax_125_setup"  }  { set MEM_PVT "ssg_cworstt_0p81v_0p81v_125c"    }
    if {$CORNER == "wc_rcmax_125_setup" }  { set MEM_PVT "ssg_cworstt_0p81v_0p81v_125c"    }
    if {$CORNER == "wcl_cmax_m40_setup" }  { set MEM_PVT "ssg_cworstt_0p81v_0p81v_m40c"    }
    if {$CORNER == "wcl_rcmax_m40_setup"}  { set MEM_PVT "ssg_cworstt_0p81v_0p81v_m40c"    }
    if {$CORNER == "wc_cmax_125_hold"   }  { set MEM_PVT "ssg_cworstt_0p81v_0p81v_125c"    }
    if {$CORNER == "wc_rcmax_125_hold"  }  { set MEM_PVT "ssg_cworstt_0p81v_0p81v_125c"    }
    if {$CORNER == "wcl_cmax_m40_hold"  }  { set MEM_PVT "ssg_cworstt_0p81v_0p81v_m40c"    }
    if {$CORNER == "wcl_rcmax_m40_hold" }  { set MEM_PVT "ssg_cworstt_0p81v_0p81v_m40c"    }
    if {$CORNER == "wc_cmin_125_hold"   }  { set MEM_PVT "ssg_cworstt_0p81v_0p81v_125c"    }
    if {$CORNER == "wc_rcmin_125_hold"  }  { set MEM_PVT "ssg_cworstt_0p81v_0p81v_125c"    }
    if {$CORNER == "wcl_cmin_m40_hold"  }  { set MEM_PVT "ssg_cworstt_0p81v_0p81v_m40c"    }
    if {$CORNER == "wcl_rcmin_m40_hold" }  { set MEM_PVT "ssg_cworstt_0p81v_0p81v_m40c"    }
    if {$CORNER == "lt_cmax_m40_hold"   }  { set MEM_PVT "ffg_cbestt_0p99v_0p99v_m40c"     }
    if {$CORNER == "lt_rcmax_m40_hold"  }  { set MEM_PVT "ffg_cbestt_0p99v_0p99v_m40c"     }
    if {$CORNER == "ml_cmax_125_hold"   }  { set MEM_PVT "ffg_cbestt_0p99v_0p99v_125c"     }
    if {$CORNER == "ml_rcmax_125_hold"  }  { set MEM_PVT "ffg_cbestt_0p99v_0p99v_125c"     }
    if {$CORNER == "lt_cmin_m40_hold"   }  { set MEM_PVT "ffg_cbestt_0p99v_0p99v_m40c"     }
    if {$CORNER == "lt_rcmin_m40_hold"  }  { set MEM_PVT "ffg_cbestt_0p99v_0p99v_m40c"     }
    if {$CORNER == "ml_cmin_125_hold"   }  { set MEM_PVT "ffg_cbestt_0p99v_0p99v_125c"     }
    if {$CORNER == "ml_rcmin_125_hold"  }  { set MEM_PVT "ffg_cbestt_0p99v_0p99v_125c"     }

    if {$CORNER == "wc_cmax_125_setup"  }  { set MEM_PVTM "ssg_cworstt_0p81v_0p81v_125c"    }
    if {$CORNER == "wc_rcmax_125_setup" }  { set MEM_PVTM "ssg_cworstt_0p81v_0p81v_125c"    }
    if {$CORNER == "wcl_cmax_m40_setup" }  { set MEM_PVTM "ssg_cworstt_0p81v_0p81v_m40c"    }
    if {$CORNER == "wcl_rcmax_m40_setup"}  { set MEM_PVTM "ssg_cworstt_0p81v_0p81v_m40c"    }
    if {$CORNER == "wc_cmax_125_hold"   }  { set MEM_PVTM "ssg_cworstt_0p81v_0p81v_125c"    }
    if {$CORNER == "wc_rcmax_125_hold"  }  { set MEM_PVTM "ssg_cworstt_0p81v_0p81v_125c"    }
    if {$CORNER == "wcl_cmax_m40_hold"  }  { set MEM_PVTM "ssg_cworstt_0p81v_0p81v_m40c"    }
    if {$CORNER == "wcl_rcmax_m40_hold" }  { set MEM_PVTM "ssg_cworstt_0p81v_0p81v_m40c"    }
    if {$CORNER == "wc_cmin_125_hold"   }  { set MEM_PVTM "ssg_cworstt_0p81v_0p81v_125c"    }
    if {$CORNER == "wc_rcmin_125_hold"  }  { set MEM_PVTM "ssg_cworstt_0p81v_0p81v_125c"    }
    if {$CORNER == "wcl_cmin_m40_hold"  }  { set MEM_PVTM "ssg_cworstt_0p81v_0p81v_m40c"    }
    if {$CORNER == "wcl_rcmin_m40_hold" }  { set MEM_PVTM "ssg_cworstt_0p81v_0p81v_m40c"    }
    if {$CORNER == "lt_cmax_m40_hold"   }  { set MEM_PVTM "ffg_cbestt_0p99v_0p99v_m40c"     }
    if {$CORNER == "lt_rcmax_m40_hold"  }  { set MEM_PVTM "ffg_cbestt_0p99v_0p99v_m40c"     }
    if {$CORNER == "ml_cmax_125_hold"   }  { set MEM_PVTM "ffg_cbestt_0p99v_0p99v_125c"     }
    if {$CORNER == "ml_rcmax_125_hold"  }  { set MEM_PVTM "ffg_cbestt_0p99v_0p99v_125c"     }
    if {$CORNER == "lt_cmin_m40_hold"   }  { set MEM_PVTM "ffg_cbestt_0p99v_0p99v_m40c"     }
    if {$CORNER == "lt_rcmin_m40_hold"  }  { set MEM_PVTM "ffg_cbestt_0p99v_0p99v_m40c"     }
    if {$CORNER == "ml_cmin_125_hold"   }  { set MEM_PVTM "ffg_cbestt_0p99v_0p99v_125c"     }
    if {$CORNER == "ml_rcmin_125_hold"  }  { set MEM_PVTM "ffg_cbestt_0p99v_0p99v_125c"     }

    if {$CORNER == "wc_cmax_125_setup"  }  { set PVTM "ssg_cworstt_0p81v_0p81v_125c"    }
    if {$CORNER == "wc_rcmax_125_setup" }  { set PVTM "ssg_cworstt_0p81v_0p81v_125c"    }
    if {$CORNER == "wcl_cmax_m40_setup" }  { set PVTM "ssg_cworstt_0p81v_0p81v_m40c"    }
    if {$CORNER == "wcl_rcmax_m40_setup"}  { set PVTM "ssg_cworstt_0p81v_0p81v_m40c"    }
    if {$CORNER == "wc_cmax_125_hold"   }  { set PVTM "ssg_cworstt_0p81v_0p81v_125c"    }
    if {$CORNER == "wc_rcmax_125_hold"  }  { set PVTM "ssg_cworstt_0p81v_0p81v_125c"    }
    if {$CORNER == "wcl_cmax_m40_hold"  }  { set PVTM "ssg_cworstt_0p81v_0p81v_m40c"    }
    if {$CORNER == "wcl_rcmax_m40_hold" }  { set PVTM "ssg_cworstt_0p81v_0p81v_m40c"    }
    if {$CORNER == "wc_cmin_125_hold"   }  { set PVTM "ssg_cworstt_0p81v_0p81v_125c"    }
    if {$CORNER == "wc_rcmin_125_hold"  }  { set PVTM "ssg_cworstt_0p81v_0p81v_125c"    }
    if {$CORNER == "wcl_cmin_m40_hold"  }  { set PVTM "ssg_cworstt_0p81v_0p81v_m40c"    }
    if {$CORNER == "wcl_rcmin_m40_hold" }  { set PVTM "ssg_cworstt_0p81v_0p81v_m40c"    }
    if {$CORNER == "lt_cmax_m40_hold"   }  { set PVTM "ffg_cbestt_0p99v_0p99v_m40c"     }
    if {$CORNER == "lt_rcmax_m40_hold"  }  { set PVTM "ffg_cbestt_0p99v_0p99v_m40c"     }
    if {$CORNER == "ml_cmax_125_hold"   }  { set PVTM "ffg_cbestt_0p99v_0p99v_125c"     }
    if {$CORNER == "ml_rcmax_125_hold"  }  { set PVTM "ffg_cbestt_0p99v_0p99v_125c"     }
    if {$CORNER == "lt_cmin_m40_hold"   }  { set PVTM "ffg_cbestt_0p99v_0p99v_m40c"     }
    if {$CORNER == "lt_rcmin_m40_hold"  }  { set PVTM "ffg_cbestt_0p99v_0p99v_m40c"     }
    if {$CORNER == "ml_cmin_125_hold"   }  { set PVTM "ffg_cbestt_0p99v_0p99v_125c"     }
    if {$CORNER == "ml_rcmin_125_hold"  }  { set PVTM "ffg_cbestt_0p99v_0p99v_125c"     }

    if {$CORNER == "wc_cmax_125_setup"  }  { set PCT "0pct"   }
    if {$CORNER == "wc_rcmax_125_setup" }  { set PCT "0pct"   }
    if {$CORNER == "wcl_cmax_m40_setup" }  { set PCT "0pct"   }
    if {$CORNER == "wcl_rcmax_m40_setup"}  { set PCT "0pct"   }
    if {$CORNER == "wc_cmax_125_hold"   }  { set PCT "0pct"   }
    if {$CORNER == "wc_rcmax_125_hold"  }  { set PCT "0pct"   }
    if {$CORNER == "wcl_cmax_m40_hold"  }  { set PCT "0pct"   }
    if {$CORNER == "wcl_rcmax_m40_hold" }  { set PCT "0pct"   }
    if {$CORNER == "wc_cmin_125_hold"   }  { set PCT "0pct"   }
    if {$CORNER == "wc_rcmin_125_hold"  }  { set PCT "0pct"   }
    if {$CORNER == "wcl_cmin_m40_hold"  }  { set PCT "0pct"   }
    if {$CORNER == "wcl_rcmin_m40_hold" }  { set PCT "0pct"   }
    if {$CORNER == "lt_cmax_m40_hold"   }  { set PCT "0pct"   }
    if {$CORNER == "lt_rcmax_m40_hold"  }  { set PCT "0pct"   }
    if {$CORNER == "ml_cmax_125_hold"   }  { set PCT "0pct"   }
    if {$CORNER == "ml_rcmax_125_hold"  }  { set PCT "0pct"   }
    if {$CORNER == "lt_cmin_m40_hold"   }  { set PCT "0pct"   }
    if {$CORNER == "lt_rcmin_m40_hold"  }  { set PCT "0pct"   }
    if {$CORNER == "ml_cmin_125_hold"   }  { set PCT "0pct"   }
    if {$CORNER == "ml_rcmin_125_hold"  }  { set PCT "0pct"   }

    if {$CORNER == "wc_cmax_125_setup"  }  { set RC_FILE "cworst_125"   }
    if {$CORNER == "wc_rcmax_125_setup" }  { set RC_FILE "rcworst_125"  }
    if {$CORNER == "wcl_cmax_m40_setup" }  { set RC_FILE "cworst_m40"   }
    if {$CORNER == "wcl_rcmax_m40_setup"}  { set RC_FILE "rcworst_m40"  }
    if {$CORNER == "wc_cmax_125_hold"   }  { set RC_FILE "cworst_125"   }
    if {$CORNER == "wc_rcmax_125_hold"  }  { set RC_FILE "rcworst_125"  }
    if {$CORNER == "wcl_cmax_m40_hold"  }  { set RC_FILE "cworst_m40"   }
    if {$CORNER == "wcl_rcmax_m40_hold" }  { set RC_FILE "rcworst_m40"  }
    if {$CORNER == "wc_cmin_125_hold"   }  { set RC_FILE "cbest_125"    }
    if {$CORNER == "wc_rcmin_125_hold"  }  { set RC_FILE "rcbest_125"   }
    if {$CORNER == "wcl_cmin_m40_hold"  }  { set RC_FILE "cbest_m40"    }
    if {$CORNER == "wcl_rcmin_m40_hold" }  { set RC_FILE "rcbest_m40"   }
    if {$CORNER == "lt_cmax_m40_hold"   }  { set RC_FILE "cworst_m40"   }
    if {$CORNER == "lt_rcmax_m40_hold"  }  { set RC_FILE "rcworst_m40"  }
    if {$CORNER == "ml_cmax_125_hold"   }  { set RC_FILE "cworst_125"   }
    if {$CORNER == "ml_rcmax_125_hold"  }  { set RC_FILE "rcworst_125"  }
    if {$CORNER == "lt_cmin_m40_hold"   }  { set RC_FILE "cbest_m40"    }
    if {$CORNER == "lt_rcmin_m40_hold"  }  { set RC_FILE "rcbest_m40"   }
    if {$CORNER == "ml_cmin_125_hold"   }  { set RC_FILE "cbest_125"    }
    if {$CORNER == "ml_rcmin_125_hold"  }  { set RC_FILE "rcbest_125"   }

  } elseif { [regexp {_28p_snps_} $LINK_LIB]} {

    if {$CORNER == "wc_cmax_125_setup"  }  { set PVT_IO "ssg_cworstt_max_0p81v_125c"    }
    if {$CORNER == "wc_rcmax_125_setup" }  { set PVT_IO "ssg_cworstt_max_0p81v_125c"    }
    if {$CORNER == "wcl_cmax_m40_setup" }  { set PVT_IO "ssg_cworstt_max_0p81v_m40c"    }
    if {$CORNER == "wcl_rcmax_m40_setup"}  { set PVT_IO "ssg_cworstt_max_0p81v_m40c"    }
    if {$CORNER == "wc_cmax_125_hold"   }  { set PVT_IO "ssg_cworstt_max_0p81v_125c"    }
    if {$CORNER == "wc_rcmax_125_hold"  }  { set PVT_IO "ssg_cworstt_max_0p81v_125c"    }
    if {$CORNER == "wcl_cmax_m40_hold"  }  { set PVT_IO "ssg_cworstt_max_0p81v_m40c"    }
    if {$CORNER == "wcl_rcmax_m40_hold" }  { set PVT_IO "ssg_cworstt_max_0p81v_m40c"    }
    if {$CORNER == "wc_cmin_125_hold"   }  { set PVT_IO "ssg_cworstt_max_0p81v_125c"    }
    if {$CORNER == "wc_rcmin_125_hold"  }  { set PVT_IO "ssg_cworstt_max_0p81v_125c"    }
    if {$CORNER == "wcl_cmin_m40_hold"  }  { set PVT_IO "ssg_cworstt_max_0p81v_m40c"    }
    if {$CORNER == "wcl_rcmin_m40_hold" }  { set PVT_IO "ssg_cworstt_max_0p81v_m40c"    }
    if {$CORNER == "lt_cmax_m40_hold"   }  { set PVT_IO "ffg_cbestt_min_0p99v_m40c"     }
    if {$CORNER == "lt_rcmax_m40_hold"  }  { set PVT_IO "ffg_cbestt_min_0p99v_m40c"     }
    if {$CORNER == "ml_cmax_125_hold"   }  { set PVT_IO "ffg_cbestt_min_0p99v_125c"     }
    if {$CORNER == "ml_rcmax_125_hold"  }  { set PVT_IO "ffg_cbestt_min_0p99v_125c"     }
    if {$CORNER == "lt_cmin_m40_hold"   }  { set PVT_IO "ffg_cbestt_min_0p99v_m40c"     }
    if {$CORNER == "lt_rcmin_m40_hold"  }  { set PVT_IO "ffg_cbestt_min_0p99v_m40c"     }
    if {$CORNER == "ml_cmin_125_hold"   }  { set PVT_IO "ffg_cbestt_min_0p99v_125c"     }
    if {$CORNER == "ml_rcmin_125_hold"  }  { set PVT_IO "ffg_cbestt_min_0p99v_125c"     }

    if {$CORNER == "wc_cmax_125_setup"  }  { set PVT_ANA "ssg_0p81v_125c"    }
    if {$CORNER == "wc_rcmax_125_setup" }  { set PVT_ANA "ssg_0p81v_125c"    }
    if {$CORNER == "wcl_cmax_m40_setup" }  { set PVT_ANA "ssg_0p81v_m40c"    }
    if {$CORNER == "wcl_rcmax_m40_setup"}  { set PVT_ANA "ssg_0p81v_m40c"    }
    if {$CORNER == "wc_cmax_125_hold"   }  { set PVT_ANA "ssg_0p81v_125c"    }
    if {$CORNER == "wc_rcmax_125_hold"  }  { set PVT_ANA "ssg_0p81v_125c"    }
    if {$CORNER == "wcl_cmax_m40_hold"  }  { set PVT_ANA "ssg_0p81v_m40c"    }
    if {$CORNER == "wcl_rcmax_m40_hold" }  { set PVT_ANA "ssg_0p81v_m40c"    }
    if {$CORNER == "wc_cmin_125_hold"   }  { set PVT_ANA "ssg_0p81v_125c"    }
    if {$CORNER == "wc_rcmin_125_hold"  }  { set PVT_ANA "ssg_0p81v_125c"    }
    if {$CORNER == "wcl_cmin_m40_hold"  }  { set PVT_ANA "ssg_0p81v_m40c"    }
    if {$CORNER == "wcl_rcmin_m40_hold" }  { set PVT_ANA "ssg_0p81v_m40c"    }
    if {$CORNER == "lt_cmax_m40_hold"   }  { set PVT_ANA "ffg_0p99v_m40c"    }
    if {$CORNER == "lt_rcmax_m40_hold"  }  { set PVT_ANA "ffg_0p99v_m40c"    }
    if {$CORNER == "ml_cmax_125_hold"   }  { set PVT_ANA "ffg_0p99v_125c"    }
    if {$CORNER == "ml_rcmax_125_hold"  }  { set PVT_ANA "ffg_0p99v_125c"    }
    if {$CORNER == "lt_cmin_m40_hold"   }  { set PVT_ANA "ffg_0p99v_m40c"    }
    if {$CORNER == "lt_rcmin_m40_hold"  }  { set PVT_ANA "ffg_0p99v_m40c"    }
    if {$CORNER == "ml_cmin_125_hold"   }  { set PVT_ANA "ffg_0p99v_125c"    }
    if {$CORNER == "ml_rcmin_125_hold"  }  { set PVT_ANA "ffg_0p99v_125c"    }

    if {$CORNER == "wc_cmax_125_setup"  }  { set PVT40 "ss0p99v125c"    }
    if {$CORNER == "wc_rcmax_125_setup" }  { set PVT40 "ss0p99v125c"    }
    if {$CORNER == "wcl_cmax_m40_setup" }  { set PVT40 "ss0p99vn40c"    }
    if {$CORNER == "wcl_rcmax_m40_setup"}  { set PVT40 "ss0p99vn40c"    }
    if {$CORNER == "wc_cmax_125_hold"   }  { set PVT40 "ss0p99v125c"    }
    if {$CORNER == "wc_rcmax_125_hold"  }  { set PVT40 "ss0p99v125c"    }
    if {$CORNER == "wcl_cmax_m40_hold"  }  { set PVT40 "ss0p99vn40c"    }
    if {$CORNER == "wcl_rcmax_m40_hold" }  { set PVT40 "ss0p99vn40c"    }
    if {$CORNER == "wc_cmin_125_hold"   }  { set PVT40 "ss0p99v125c"    }
    if {$CORNER == "wc_rcmin_125_hold"  }  { set PVT40 "ss0p99v125c"    }
    if {$CORNER == "wcl_cmin_m40_hold"  }  { set PVT40 "ss0p99vn40c"    }
    if {$CORNER == "wcl_rcmin_m40_hold" }  { set PVT40 "ss0p99vn40c"    }
    if {$CORNER == "lt_cmax_m40_hold"   }  { set PVT40 "ff1p21vn40c"    }
    if {$CORNER == "lt_rcmax_m40_hold"  }  { set PVT40 "ff1p21vn40c"    }
    if {$CORNER == "ml_cmax_125_hold"   }  { set PVT40 "ff1p21v125c"    }
    if {$CORNER == "ml_rcmax_125_hold"  }  { set PVT40 "ff1p21v125c"    }
    if {$CORNER == "lt_cmin_m40_hold"   }  { set PVT40 "ff1p21vn40c"    }
    if {$CORNER == "lt_rcmin_m40_hold"  }  { set PVT40 "ff1p21vn40c"    }
    if {$CORNER == "ml_cmin_125_hold"   }  { set PVT40 "ff1p21v125c"    }
    if {$CORNER == "ml_rcmin_125_hold"  }  { set PVT40 "ff1p21v125c"    }

    if {$CORNER == "wc_cmax_125_setup"  }  { set PVT    "ssgwc0p81v125c"    }
    if {$CORNER == "wc_rcmax_125_setup" }  { set PVT    "ssgwc0p81v125c"    }
    if {$CORNER == "wcl_cmax_m40_setup" }  { set PVT    "ssgwc0p81vn40c"    }
    if {$CORNER == "wcl_rcmax_m40_setup"}  { set PVT    "ssgwc0p81vn40c"    }
    if {$CORNER == "wc_cmax_125_hold"   }  { set PVT    "ssgwc0p81v125c"    }
    if {$CORNER == "wc_rcmax_125_hold"  }  { set PVT    "ssgwc0p81v125c"    }
    if {$CORNER == "wcl_cmax_m40_hold"  }  { set PVT    "ssgwc0p81vn40c"    }
    if {$CORNER == "wcl_rcmax_m40_hold" }  { set PVT    "ssgwc0p81vn40c"    }
    if {$CORNER == "wc_cmin_125_hold"   }  { set PVT    "ssgwc0p81v125c"    }
    if {$CORNER == "wc_rcmin_125_hold"  }  { set PVT    "ssgwc0p81v125c"    }
    if {$CORNER == "wcl_cmin_m40_hold"  }  { set PVT    "ssgwc0p81vn40c"    }
    if {$CORNER == "wcl_rcmin_m40_hold" }  { set PVT    "ssgwc0p81vn40c"    }
    if {$CORNER == "lt_cmax_m40_hold"   }  { set PVT    "ffgbc0p99vn40c"     }
    if {$CORNER == "lt_rcmax_m40_hold"  }  { set PVT    "ffgbc0p99vn40c"     }
    if {$CORNER == "ml_cmax_125_hold"   }  { set PVT    "ffgbc0p99v125c"     }
    if {$CORNER == "ml_rcmax_125_hold"  }  { set PVT    "ffgbc0p99v125c"     }
    if {$CORNER == "lt_cmin_m40_hold"   }  { set PVT    "ffgbc0p99vn40c"     }
    if {$CORNER == "lt_rcmin_m40_hold"  }  { set PVT    "ffgbc0p99vn40c"     }
    if {$CORNER == "ml_cmin_125_hold"   }  { set PVT    "ffgbc0p99v125c"     }  
    if {$CORNER == "ml_rcmin_125_hold"  }  { set PVT    "ffgbc0p99v125c"     }  

    if {$CORNER == "wc_cmax_125_setup"  }  { set MEM_PVT "ssgwc0p81v125c"    }
    if {$CORNER == "wc_rcmax_125_setup" }  { set MEM_PVT "ssgwc0p81v125c"    }
    if {$CORNER == "wcl_cmax_m40_setup" }  { set MEM_PVT "ssgwc0p81vn40c"    }
    if {$CORNER == "wcl_rcmax_m40_setup"}  { set MEM_PVT "ssgwc0p81vn40c"    }
    if {$CORNER == "wc_cmax_125_hold"   }  { set MEM_PVT "ssgwc0p81v125c"    }
    if {$CORNER == "wc_rcmax_125_hold"  }  { set MEM_PVT "ssgwc0p81v125c"    }
    if {$CORNER == "wcl_cmax_m40_hold"  }  { set MEM_PVT "ssgwc0p81vn40c"    }
    if {$CORNER == "wcl_rcmax_m40_hold" }  { set MEM_PVT "ssgwc0p81vn40c"    }
    if {$CORNER == "wc_cmin_125_hold"   }  { set MEM_PVT "ssgwc0p81v125c"    }
    if {$CORNER == "wc_rcmin_125_hold"  }  { set MEM_PVT "ssgwc0p81v125c"    }
    if {$CORNER == "wcl_cmin_m40_hold"  }  { set MEM_PVT "ssgwc0p81vn40c"    }
    if {$CORNER == "wcl_rcmin_m40_hold" }  { set MEM_PVT "ssgwc0p81vn40c"    }
    if {$CORNER == "lt_cmax_m40_hold"   }  { set MEM_PVT "ffgbc0p99vn40c"     }
    if {$CORNER == "lt_rcmax_m40_hold"  }  { set MEM_PVT "ffgbc0p99vn40c"     }
    if {$CORNER == "ml_cmax_125_hold"   }  { set MEM_PVT "ffgbc0p99v125c"     }
    if {$CORNER == "ml_rcmax_125_hold"  }  { set MEM_PVT "ffgbc0p99v125c"     }
    if {$CORNER == "lt_cmin_m40_hold"   }  { set MEM_PVT "ffgbc0p99vn40c"     }
    if {$CORNER == "lt_rcmin_m40_hold"  }  { set MEM_PVT "ffgbc0p99vn40c"     }
    if {$CORNER == "ml_cmin_125_hold"   }  { set MEM_PVT "ffgbc0p99v125c"     }
    if {$CORNER == "ml_rcmin_125_hold"  }  { set MEM_PVT "ffgbc0p99v125c"     }

    if {$CORNER == "wc_cmax_125_setup"  }  { set MEM_PVTM "ssgwc0p81v125c"    }
    if {$CORNER == "wc_rcmax_125_setup" }  { set MEM_PVTM "ssgwc0p81v125c"    }
    if {$CORNER == "wcl_cmax_m40_setup" }  { set MEM_PVTM "ssgwc0p81vn40c"    }
    if {$CORNER == "wcl_rcmax_m40_setup"}  { set MEM_PVTM "ssgwc0p81vn40c"    }
    if {$CORNER == "wc_cmax_125_hold"   }  { set MEM_PVTM "ssgwc0p81v125c"    }
    if {$CORNER == "wc_rcmax_125_hold"  }  { set MEM_PVTM "ssgwc0p81v125c"    }
    if {$CORNER == "wcl_cmax_m40_hold"  }  { set MEM_PVTM "ssgwc0p81vn40c"    }
    if {$CORNER == "wcl_rcmax_m40_hold" }  { set MEM_PVTM "ssgwc0p81vn40c"    }
    if {$CORNER == "wc_cmin_125_hold"   }  { set MEM_PVTM "ssgwc0p81v125c"    }
    if {$CORNER == "wc_rcmin_125_hold"  }  { set MEM_PVTM "ssgwc0p81v125c"    }
    if {$CORNER == "wcl_cmin_m40_hold"  }  { set MEM_PVTM "ssgwc0p81vn40c"    }
    if {$CORNER == "wcl_rcmin_m40_hold" }  { set MEM_PVTM "ssgwc0p81vn40c"    }
    if {$CORNER == "lt_cmax_m40_hold"   }  { set MEM_PVTM "ffgbc0p99vn40c"     }
    if {$CORNER == "lt_rcmax_m40_hold"  }  { set MEM_PVTM "ffgbc0p99vn40c"     }
    if {$CORNER == "ml_cmax_125_hold"   }  { set MEM_PVTM "ffgbc0p99v125c"     }
    if {$CORNER == "ml_rcmax_125_hold"  }  { set MEM_PVTM "ffgbc0p99v125c"     }
    if {$CORNER == "lt_cmin_m40_hold"   }  { set MEM_PVTM "ffgbc0p99vn40c"     }
    if {$CORNER == "lt_rcmin_m40_hold"  }  { set MEM_PVTM "ffgbc0p99vn40c"     }
    if {$CORNER == "ml_cmin_125_hold"   }  { set MEM_PVTM "ffgbc0p99v125c"     }
    if {$CORNER == "ml_rcmin_125_hold"  }  { set MEM_PVTM "ffgbc0p99v125c"     }

    if {$CORNER == "wc_cmax_125_setup"  }  { set PVTM "ssgwc0p81v125c"    }
    if {$CORNER == "wc_rcmax_125_setup" }  { set PVTM "ssgwc0p81v125c"    }
    if {$CORNER == "wcl_cmax_m40_setup" }  { set PVTM "ssgwc0p81vn40c"    }
    if {$CORNER == "wcl_rcmax_m40_setup"}  { set PVTM "ssgwc0p81vn40c"    }
    if {$CORNER == "wc_cmax_125_hold"   }  { set PVTM "ssgwc0p81v125c"    }
    if {$CORNER == "wc_rcmax_125_hold"  }  { set PVTM "ssgwc0p81v125c"    }
    if {$CORNER == "wcl_cmax_m40_hold"  }  { set PVTM "ssgwc0p81vn40c"    }
    if {$CORNER == "wcl_rcmax_m40_hold" }  { set PVTM "ssgwc0p81vn40c"    }
    if {$CORNER == "wc_cmin_125_hold"   }  { set PVTM "ssgwc0p81v125c"    }
    if {$CORNER == "wc_rcmin_125_hold"  }  { set PVTM "ssgwc0p81v125c"    }
    if {$CORNER == "wcl_cmin_m40_hold"  }  { set PVTM "ssgwc0p81vn40c"    }
    if {$CORNER == "wcl_rcmin_m40_hold" }  { set PVTM "ssgwc0p81vn40c"    }
    if {$CORNER == "lt_cmax_m40_hold"   }  { set PVTM "ffgbc0p99vn40c"     }
    if {$CORNER == "lt_rcmax_m40_hold"  }  { set PVTM "ffgbc0p99vn40c"     }
    if {$CORNER == "ml_cmax_125_hold"   }  { set PVTM "ffgbc0p99v125c"     }
    if {$CORNER == "ml_rcmax_125_hold"  }  { set PVTM "ffgbc0p99v125c"     }
    if {$CORNER == "lt_cmin_m40_hold"   }  { set PVTM "ffgbc0p99vn40c"     }
    if {$CORNER == "lt_rcmin_m40_hold"  }  { set PVTM "ffgbc0p99vn40c"     }
    if {$CORNER == "ml_cmin_125_hold"   }  { set PVTM "ffgbc0p99v125c"     }
    if {$CORNER == "ml_rcmin_125_hold"  }  { set PVTM "ffgbc0p99v125c"     }
#?
    if {$CORNER == "wc_cmax_125_setup"  }  { set PCT "0pct"   }
    if {$CORNER == "wc_rcmax_125_setup" }  { set PCT "0pct"   }
    if {$CORNER == "wcl_cmax_m40_setup" }  { set PCT "0pct"   }
    if {$CORNER == "wcl_rcmax_m40_setup"}  { set PCT "0pct"   }
    if {$CORNER == "wc_cmax_125_hold"   }  { set PCT "0pct"   }
    if {$CORNER == "wc_rcmax_125_hold"  }  { set PCT "0pct"   }
    if {$CORNER == "wcl_cmax_m40_hold"  }  { set PCT "0pct"   }
    if {$CORNER == "wcl_rcmax_m40_hold" }  { set PCT "0pct"   }
    if {$CORNER == "wc_cmin_125_hold"   }  { set PCT "0pct"   }
    if {$CORNER == "wc_rcmin_125_hold"  }  { set PCT "0pct"   }
    if {$CORNER == "wcl_cmin_m40_hold"  }  { set PCT "0pct"   }
    if {$CORNER == "wcl_rcmin_m40_hold" }  { set PCT "0pct"   }
    if {$CORNER == "lt_cmax_m40_hold"   }  { set PCT "0pct"   }
    if {$CORNER == "lt_rcmax_m40_hold"  }  { set PCT "0pct"   }
    if {$CORNER == "ml_cmax_125_hold"   }  { set PCT "0pct"   }
    if {$CORNER == "ml_rcmax_125_hold"  }  { set PCT "0pct"   }
    if {$CORNER == "lt_cmin_m40_hold"   }  { set PCT "0pct"   }
    if {$CORNER == "lt_rcmin_m40_hold"  }  { set PCT "0pct"   }
    if {$CORNER == "ml_cmin_125_hold"   }  { set PCT "0pct"   }
    if {$CORNER == "ml_rcmin_125_hold"  }  { set PCT "0pct"   }

    if {$CORNER == "wc_cmax_125_setup"  }  { set RC_FILE "cworst_125"   }
    if {$CORNER == "wc_rcmax_125_setup" }  { set RC_FILE "rcworst_125"  }
    if {$CORNER == "wcl_cmax_m40_setup" }  { set RC_FILE "cworst_m40"   }
    if {$CORNER == "wcl_rcmax_m40_setup"}  { set RC_FILE "rcworst_m40"  }
    if {$CORNER == "wc_cmax_125_hold"   }  { set RC_FILE "cworst_125"   }
    if {$CORNER == "wc_rcmax_125_hold"  }  { set RC_FILE "rcworst_125"  }
    if {$CORNER == "wcl_cmax_m40_hold"  }  { set RC_FILE "cworst_m40"   }
    if {$CORNER == "wcl_rcmax_m40_hold" }  { set RC_FILE "rcworst_m40"  }
    if {$CORNER == "wc_cmin_125_hold"   }  { set RC_FILE "cbest_125"    }
    if {$CORNER == "wc_rcmin_125_hold"  }  { set RC_FILE "rcbest_125"   }
    if {$CORNER == "wcl_cmin_m40_hold"  }  { set RC_FILE "cbest_m40"    }
    if {$CORNER == "wcl_rcmin_m40_hold" }  { set RC_FILE "rcbest_m40"   }
    if {$CORNER == "lt_cmax_m40_hold"   }  { set RC_FILE "cworst_m40"   }
    if {$CORNER == "lt_rcmax_m40_hold"  }  { set RC_FILE "rcworst_m40"  }
    if {$CORNER == "ml_cmax_125_hold"   }  { set RC_FILE "cworst_125"   }
    if {$CORNER == "ml_rcmax_125_hold"  }  { set RC_FILE "rcworst_125"  }
    if {$CORNER == "lt_cmin_m40_hold"   }  { set RC_FILE "cbest_m40"    }
    if {$CORNER == "lt_rcmin_m40_hold"  }  { set RC_FILE "rcbest_m40"   }
    if {$CORNER == "ml_cmin_125_hold"   }  { set RC_FILE "cbest_125"    }
    if {$CORNER == "ml_rcmin_125_hold"  }  { set RC_FILE "rcbest_125"   }

  } elseif { [regexp {tsmc_22ulp_} $LINK_LIB]} {

    if {$CORNER == "wc_cmax_125_setup"  }  { set PVT_IO "ssg0p81v1p62v125c"  }
    if {$CORNER == "wc_rcmax_125_setup" }  { set PVT_IO "ssg0p81v1p62v125c"  }
    if {$CORNER == "wcz_cmax_0_setup"   }  { set PVT_IO "ssg0p81v1p62v0c"    }
    if {$CORNER == "wcz_rcmax_0_setup"  }  { set PVT_IO "ssg0p81v1p62v0c"    }
    if {$CORNER == "wcl_cmax_m40_setup" }  { set PVT_IO "ssg0p81v1p62vm40c"  }
    if {$CORNER == "wcl_rcmax_m40_setup"}  { set PVT_IO "ssg0p81v1p62vm40c"  }
    if {$CORNER == "wc_cmax_125_hold"   }  { set PVT_IO "ssg0p81v1p62v125c"  }
    if {$CORNER == "wc_rcmax_125_hold"  }  { set PVT_IO "ssg0p81v1p62v125c"  }
    if {$CORNER == "wcz_cmax_0_hold"    }  { set PVT_IO "ssg0p81v1p62v0c"    }
    if {$CORNER == "wcz_rcmax_0_hold"   }  { set PVT_IO "ssg0p81v1p62v0c"    }
    if {$CORNER == "wcl_cmax_m40_hold"  }  { set PVT_IO "ssg0p81v1p62vm40c"  }
    if {$CORNER == "wcl_rcmax_m40_hold" }  { set PVT_IO "ssg0p81v1p62vm40c"  }
    if {$CORNER == "lt_cmax_m40_hold"   }  { set PVT_IO "ffg0p99v1p98vm40c"  }
    if {$CORNER == "lt_rcmax_m40_hold"  }  { set PVT_IO "ffg0p99v1p98vm40c"  }
    if {$CORNER == "bc_cmax_0_hold"     }  { set PVT_IO "ffg0p99v1p98v0c"    }
    if {$CORNER == "bc_rcmax_0_hold"    }  { set PVT_IO "ffg0p99v1p98v0c"    }
    if {$CORNER == "ml_cmax_125_hold"   }  { set PVT_IO "ffg0p99v1p98v125c"  }
    if {$CORNER == "ml_rcmax_125_hold"  }  { set PVT_IO "ffg0p99v1p98v125c"  }
    if {$CORNER == "lt_cmin_m40_hold"   }  { set PVT_IO "ffg0p99v1p98vm40c"  }
    if {$CORNER == "lt_rcmin_m40_hold"  }  { set PVT_IO "ffg0p99v1p98vm40c"  }
    if {$CORNER == "bc_cmin_0_hold"     }  { set PVT_IO "ffg0p99v1p98v0c"    }
    if {$CORNER == "bc_rcmin_0_hold"    }  { set PVT_IO "ffg0p99v1p98v0c"    }
    if {$CORNER == "ml_cmin_125_hold"   }  { set PVT_IO "ffg0p99v1p98v125c"  }
    if {$CORNER == "ml_rcmin_125_hold"  }  { set PVT_IO "ffg0p99v1p98v125c"  }
    if {$CORNER == "typical_85c"        }  { set PVT_IO "tt0p9v85c"  }

    if {$CORNER == "wc_cmax_125_setup"  }  { set PVT_ANA "ssg0p81v125c"  }
    if {$CORNER == "wc_rcmax_125_setup" }  { set PVT_ANA "ssg0p81v125c"  }
    if {$CORNER == "wcz_cmax_0_setup"   }  { set PVT_ANA "ssg0p81v0c"    }
    if {$CORNER == "wcz_rcmax_0_setup"  }  { set PVT_ANA "ssg0p81v0c"    }
    if {$CORNER == "wcl_cmax_m40_setup" }  { set PVT_ANA "ssg0p81vm40c"  }
    if {$CORNER == "wcl_rcmax_m40_setup"}  { set PVT_ANA "ssg0p81vm40c"  }
    if {$CORNER == "wc_cmax_125_hold"   }  { set PVT_ANA "ssg0p81v125c"  }
    if {$CORNER == "wc_rcmax_125_hold"  }  { set PVT_ANA "ssg0p81v125c"  }
    if {$CORNER == "wcz_cmax_0_hold"    }  { set PVT_ANA "ssg0p81v0c"    }
    if {$CORNER == "wcz_rcmax_0_hold"   }  { set PVT_ANA "ssg0p81v0c"    }
    if {$CORNER == "wcl_cmax_m40_hold"  }  { set PVT_ANA "ssg0p81vm40c"  }
    if {$CORNER == "wcl_rcmax_m40_hold" }  { set PVT_ANA "ssg0p81vm40c"  }
    if {$CORNER == "lt_cmax_m40_hold"   }  { set PVT_ANA "ffg0p99vm40c"  }
    if {$CORNER == "lt_rcmax_m40_hold"  }  { set PVT_ANA "ffg0p99vm40c"  }
    if {$CORNER == "bc_cmax_0_hold"     }  { set PVT_ANA "ffg0p99v0c"    }
    if {$CORNER == "bc_rcmax_0_hold"    }  { set PVT_ANA "ffg0p99v0c"    }
    if {$CORNER == "ml_cmax_125_hold"   }  { set PVT_ANA "ffg0p99v125c"  }
    if {$CORNER == "ml_rcmax_125_hold"  }  { set PVT_ANA "ffg0p99v125c"  }
    if {$CORNER == "lt_cmin_m40_hold"   }  { set PVT_ANA "ffg0p99vm40c"  }
    if {$CORNER == "lt_rcmin_m40_hold"  }  { set PVT_ANA "ffg0p99vm40c"  }
    if {$CORNER == "bc_cmin_0_hold"     }  { set PVT_ANA "ffg0p99v0c"    }
    if {$CORNER == "bc_rcmin_0_hold"    }  { set PVT_ANA "ffg0p99v0c"    }
    if {$CORNER == "ml_cmin_125_hold"   }  { set PVT_ANA "ffg0p99v125c"  }
    if {$CORNER == "ml_rcmin_125_hold"  }  { set PVT_ANA "ffg0p99v125c"  }
    if {$CORNER == "typical_85c"        }  { set PVT_ANA "tt0p9v85c"  }
 # add by XQJ : ddr lib CLKSWITCH
    if {$CORNER == "wc_cmax_125_setup"  }  { set PVT_DDR_UTILS "ss0p81v125c_pg"  }
    if {$CORNER == "wc_rcmax_125_setup" }  { set PVT_DDR_UTILS "ss0p81v125c_pg"  }
    if {$CORNER == "wcz_cmax_0_setup"   }  { set PVT_DDR_UTILS "ss0p81v0c_pg"    }
    if {$CORNER == "wcz_rcmax_0_setup"  }  { set PVT_DDR_UTILS "ss0p81v0c_pg"    }
    if {$CORNER == "wcl_cmax_m40_setup" }  { set PVT_DDR_UTILS "ss0p81vn40c_pg"  }
    if {$CORNER == "wcl_rcmax_m40_setup"}  { set PVT_DDR_UTILS "ss0p81vn40c_pg"  }
    if {$CORNER == "wc_cmax_125_hold"   }  { set PVT_DDR_UTILS "ss0p81v125c_pg"  }
    if {$CORNER == "wc_rcmax_125_hold"  }  { set PVT_DDR_UTILS "ss0p81v125c_pg"  }
    if {$CORNER == "wcz_cmax_0_hold"    }  { set PVT_DDR_UTILS "ss0p81v0c_pg"    }
    if {$CORNER == "wcz_rcmax_0_hold"   }  { set PVT_DDR_UTILS "ss0p81v0c_pg"    }
    if {$CORNER == "wcl_cmax_m40_hold"  }  { set PVT_DDR_UTILS "ss0p81vn40c_pg"  }
    if {$CORNER == "wcl_rcmax_m40_hold" }  { set PVT_DDR_UTILS "ss0p81vn40c_pg"  }
    if {$CORNER == "lt_cmax_m40_hold"   }  { set PVT_DDR_UTILS "ff0p99vn40c_pg"  }
    if {$CORNER == "lt_rcmax_m40_hold"  }  { set PVT_DDR_UTILS "ff0p99vn40c_pg"  }
    if {$CORNER == "bc_cmax_0_hold"     }  { set PVT_DDR_UTILS "ff0p99v0c_pg"    }
    if {$CORNER == "bc_rcmax_0_hold"    }  { set PVT_DDR_UTILS "ff0p99v0c_pg"    }
    if {$CORNER == "ml_cmax_125_hold"   }  { set PVT_DDR_UTILS "ff0p99v125c_pg"  }
    if {$CORNER == "ml_rcmax_125_hold"  }  { set PVT_DDR_UTILS "ff0p99v125c_pg"  }
    if {$CORNER == "lt_cmin_m40_hold"   }  { set PVT_DDR_UTILS "ff0p99vn40c_pg"  }
    if {$CORNER == "lt_rcmin_m40_hold"  }  { set PVT_DDR_UTILS "ff0p99vn40c_pg"  }
    if {$CORNER == "bc_cmin_0_hold"     }  { set PVT_DDR_UTILS "ff0p99v0c_pg"    }
    if {$CORNER == "bc_rcmin_0_hold"    }  { set PVT_DDR_UTILS "ff0p99v0c_pg"    }
    if {$CORNER == "ml_cmin_125_hold"   }  { set PVT_DDR_UTILS "ff0p99v125c_pg"  }
    if {$CORNER == "ml_rcmin_125_hold"  }  { set PVT_DDR_UTILS "ff0p99v125c_pg"  }
    if {$CORNER == "typical_85c"        }  { set PVT_DDR_UTILS "tt0p9v25c_pg"    }

    if {$CORNER == "wc_cmax_125_setup"  }  { set PVT_DDR "ss0p81v125c_Cworst_pg"  }
    if {$CORNER == "wc_rcmax_125_setup" }  { set PVT_DDR "ss0p81v125c_RCworst_pg" }
    if {$CORNER == "wcz_cmax_0_setup"   }  { set PVT_DDR "ss0p81v0c_Cworst_pg"    }
    if {$CORNER == "wcz_rcmax_0_setup"  }  { set PVT_DDR "ss0p81v0c_RCworst_pg"   }
    if {$CORNER == "wcl_cmax_m40_setup" }  { set PVT_DDR "ss0p81vn40c_Cworst_pg"  }
    if {$CORNER == "wcl_rcmax_m40_setup"}  { set PVT_DDR "ss0p81vn40c_RCworst_pg" }
    if {$CORNER == "wc_cmax_125_hold"   }  { set PVT_DDR "ss0p81v125c_Cworst_pg"  }
    if {$CORNER == "wc_rcmax_125_hold"  }  { set PVT_DDR "ss0p81v125c_RCworst_pg" }
    if {$CORNER == "wcz_cmax_0_hold"    }  { set PVT_DDR "ss0p81v0c_Cworst_pg"    }
    if {$CORNER == "wcz_rcmax_0_hold"   }  { set PVT_DDR "ss0p81v0c_RCworst_pg"   }
    if {$CORNER == "wcl_cmax_m40_hold"  }  { set PVT_DDR "ss0p81vn40c_Cworst_pg"  }
    if {$CORNER == "wcl_rcmax_m40_hold" }  { set PVT_DDR "ss0p81vn40c_RCworst_pg" }
    if {$CORNER == "lt_cmax_m40_hold"   }  { set PVT_DDR "ff0p99vn40c_Cworst_pg"  }
    if {$CORNER == "lt_rcmax_m40_hold"  }  { set PVT_DDR "ff0p99vn40c_RCworst_pg" }
    if {$CORNER == "bc_cmax_0_hold"     }  { set PVT_DDR "ff0p99v0c_Cworst_pg"    }
    if {$CORNER == "bc_rcmax_0_hold"    }  { set PVT_DDR "ff0p99v0c_RCworst_pg"   }
    if {$CORNER == "ml_cmax_125_hold"   }  { set PVT_DDR "ff0p99v125c_Cworst_pg"  }
    if {$CORNER == "ml_rcmax_125_hold"  }  { set PVT_DDR "ff0p99v125c_RCworst_pg" }
    if {$CORNER == "lt_cmin_m40_hold"   }  { set PVT_DDR "ff0p99vn40c_Cbest_pg"   }
    if {$CORNER == "lt_rcmin_m40_hold"  }  { set PVT_DDR "ff0p99vn40c_RCbest_pg"  }
    if {$CORNER == "bc_cmin_0_hold"     }  { set PVT_DDR "ff0p99v0c_Cbest_pg"     }
    if {$CORNER == "bc_rcmin_0_hold"    }  { set PVT_DDR "ff0p99v0c_RCbest_pg"    }
    if {$CORNER == "ml_cmin_125_hold"   }  { set PVT_DDR "ff0p99v125c_Cbest_pg"   }
    if {$CORNER == "ml_rcmin_125_hold"  }  { set PVT_DDR "ff0p99v125c_RCbest_pg"  }
    if {$CORNER == "typical_85c"        }  { set PVT_DDR "tt0p9v25c_RCTypical_pg"  }

    if {$CORNER == "wc_cmax_125_setup"  }  { set PVT40 "ss0p99v125c"  }
    if {$CORNER == "wc_rcmax_125_setup" }  { set PVT40 "ss0p99v125c"  }
    if {$CORNER == "wcz_cmax_0_setup"   }  { set PVT40 "ss0p99v0c"    }
    if {$CORNER == "wcz_rcmax_0_setup"  }  { set PVT40 "ss0p99v0c"    }
    if {$CORNER == "wcl_cmax_m40_setup" }  { set PVT40 "ss0p99vn40c"  }
    if {$CORNER == "wcl_rcmax_m40_setup"}  { set PVT40 "ss0p99vn40c"  }
    if {$CORNER == "wc_cmax_125_hold"   }  { set PVT40 "ss0p99v125c"  }
    if {$CORNER == "wc_rcmax_125_hold"  }  { set PVT40 "ss0p99v125c"  }
    if {$CORNER == "wcz_cmax_0_hold"    }  { set PVT40 "ss0p99v0c"    }
    if {$CORNER == "wcz_rcmax_0_hold"   }  { set PVT40 "ss0p99v0c"    }
    if {$CORNER == "wcl_cmax_m40_hold"  }  { set PVT40 "ss0p99vn40c"  }
    if {$CORNER == "wcl_rcmax_m40_hold" }  { set PVT40 "ss0p99vn40c"  }
    if {$CORNER == "lt_cmax_m40_hold"   }  { set PVT40 "ff1p21vn40c"  }
    if {$CORNER == "lt_rcmax_m40_hold"  }  { set PVT40 "ff1p21vn40c"  }
    if {$CORNER == "bc_cmax_0_hold"     }  { set PVT40 "ff1p21v0c"    }
    if {$CORNER == "bc_rcmax_0_hold"    }  { set PVT40 "ff1p21v0c"    }
    if {$CORNER == "ml_cmax_125_hold"   }  { set PVT40 "ff1p21v125c"  }
    if {$CORNER == "ml_rcmax_125_hold"  }  { set PVT40 "ff1p21v125c"  }
    if {$CORNER == "lt_cmin_m40_hold"   }  { set PVT40 "ff1p21vn40c"  }
    if {$CORNER == "lt_rcmin_m40_hold"  }  { set PVT40 "ff1p21vn40c"  }
    if {$CORNER == "bc_cmin_0_hold"     }  { set PVT40 "ff1p21v0c"    }
    if {$CORNER == "bc_rcmin_0_hold"    }  { set PVT40 "ff1p21v0c"    }
    if {$CORNER == "ml_cmin_125_hold"   }  { set PVT40 "ff1p21v125c"  }
    if {$CORNER == "ml_rcmin_125_hold"  }  { set PVT40 "ff1p21v125c"  }
    if {$CORNER == "typical_85c"        }  { set PVT_DDR "tt0p9v25c_RCTypical_pg"  }
# CLKSWITCH
    if {$CORNER == "wc_cmax_125_setup"  }  { set PVT_MACRO "wc_cmax_125_setup"  }
    if {$CORNER == "wc_rcmax_125_setup" }  { set PVT_MACRO "wc_rcmax_125_setup" }
    if {$CORNER == "wcz_cmax_0_setup"   }  { set PVT_MACRO "wcz_cmax_0_setup"   }
    if {$CORNER == "wcz_rcmax_0_setup"  }  { set PVT_MACRO "wcz_rcmax_0_setup"  }
    if {$CORNER == "wcl_cmax_m40_setup" }  { set PVT_MACRO "wcl_cmax_m40_setup" }
    if {$CORNER == "wcl_rcmax_m40_setup"}  { set PVT_MACRO "wcl_rcmax_m40_setup"}
    if {$CORNER == "wc_cmax_125_hold"   }  { set PVT_MACRO "wc_cmax_125_hold"   }
    if {$CORNER == "wc_rcmax_125_hold"  }  { set PVT_MACRO "wc_rcmax_125_hold"  }
    if {$CORNER == "wcz_cmax_0_hold"    }  { set PVT_MACRO "wcz_cmax_0_hold"    }
    if {$CORNER == "wcz_rcmax_0_hold"   }  { set PVT_MACRO "wcz_rcmax_0_hold"   }
    if {$CORNER == "wcl_cmax_m40_hold"  }  { set PVT_MACRO "wcl_cmax_m40_hold"  }
    if {$CORNER == "wcl_rcmax_m40_hold" }  { set PVT_MACRO "wcl_rcmax_m40_hold" }
    if {$CORNER == "lt_cmax_m40_hold"   }  { set PVT_MACRO "lt_cmax_m40_hold"   }
    if {$CORNER == "lt_rcmax_m40_hold"  }  { set PVT_MACRO "lt_rcmax_m40_hold"  }
    if {$CORNER == "bc_cmax_0_hold"     }  { set PVT_MACRO "bc_cmax_0_hold"     }
    if {$CORNER == "bc_rcmax_0_hold"    }  { set PVT_MACRO "bc_rcmax_0_hold"    }
    if {$CORNER == "ml_cmax_125_hold"   }  { set PVT_MACRO "ml_cmax_125_hold"   }
    if {$CORNER == "ml_rcmax_125_hold"  }  { set PVT_MACRO "ml_rcmax_125_hold"  }
    if {$CORNER == "lt_cmin_m40_hold"   }  { set PVT_MACRO "lt_cmin_m40_hold"   }
    if {$CORNER == "lt_rcmin_m40_hold"  }  { set PVT_MACRO "lt_rcmin_m40_hold"  }
    if {$CORNER == "bc_cmin_0_hold"     }  { set PVT_MACRO "bc_cmin_0_hold"     }
    if {$CORNER == "bc_rcmin_0_hold"    }  { set PVT_MACRO "bc_rcmin_0_hold"    }
    if {$CORNER == "ml_cmin_125_hold"   }  { set PVT_MACRO "ml_cmin_125_hold"   }
    if {$CORNER == "ml_rcmin_125_hold"  }  { set PVT_MACRO "ml_rcmin_125_hold"  }
    if {$CORNER == "typical_85c"        }  { set PVT_MACRO "wcz_rcmax_0_hold"       }
#
    if {$CORNER == "wc_cmax_125_setup"  }  { set PVT    "ssg0p81v125c"  }
    if {$CORNER == "wc_rcmax_125_setup" }  { set PVT    "ssg0p81v125c"  }
    if {$CORNER == "wcz_cmax_0_setup"   }  { set PVT    "ssg0p81v0c"    }
    if {$CORNER == "wcz_rcmax_0_setup"  }  { set PVT    "ssg0p81v0c"    }
    if {$CORNER == "wcl_cmax_m40_setup" }  { set PVT    "ssg0p81vn40c"  }
    if {$CORNER == "wcl_rcmax_m40_setup"}  { set PVT    "ssg0p81vn40c"  }
    if {$CORNER == "wc_cmax_125_hold"   }  { set PVT    "ssg0p81v125c"  }
    if {$CORNER == "wc_rcmax_125_hold"  }  { set PVT    "ssg0p81v125c"  }
    if {$CORNER == "wcz_cmax_0_hold"    }  { set PVT    "ssg0p81v0c"    }
    if {$CORNER == "wcz_rcmax_0_hold"   }  { set PVT    "ssg0p81v0c"    }
    if {$CORNER == "wcl_cmax_m40_hold"  }  { set PVT    "ssg0p81vn40c"  }
    if {$CORNER == "wcl_rcmax_m40_hold" }  { set PVT    "ssg0p81vn40c"  }
    if {$CORNER == "lt_cmax_m40_hold"   }  { set PVT    "ffg0p99vn40c"  }
    if {$CORNER == "lt_rcmax_m40_hold"  }  { set PVT    "ffg0p99vn40c"  }
    if {$CORNER == "bc_cmax_0_hold"     }  { set PVT    "ffg0p99v0c"    }
    if {$CORNER == "bc_rcmax_0_hold"    }  { set PVT    "ffg0p99v0c"    }
    if {$CORNER == "ml_cmax_125_hold"   }  { set PVT    "ffg0p99v125c"  }
    if {$CORNER == "ml_rcmax_125_hold"  }  { set PVT    "ffg0p99v125c"  }
    if {$CORNER == "lt_cmin_m40_hold"   }  { set PVT    "ffg0p99vn40c"  }
    if {$CORNER == "lt_rcmin_m40_hold"  }  { set PVT    "ffg0p99vn40c"  }
    if {$CORNER == "bc_cmin_0_hold"     }  { set PVT    "ffg0p99v0c"    }
    if {$CORNER == "bc_rcmin_0_hold"    }  { set PVT    "ffg0p99v0c"    }
    if {$CORNER == "ml_cmin_125_hold"   }  { set PVT    "ffg0p99v125c"  }  
    if {$CORNER == "typical_85c"        }  { set PVT    "tt0p9v85c"  }  

    if {$CORNER == "wc_cmax_125_setup"  }  { set MEM_PVT "ssgwct0p81v125c"  }
    if {$CORNER == "wc_rcmax_125_setup" }  { set MEM_PVT "ssgwct0p81v125c"  }
    if {$CORNER == "wcz_cmax_0_setup"   }  { set MEM_PVT "ssgwct0p81v0c"    }
    if {$CORNER == "wcz_rcmax_0_setup"  }  { set MEM_PVT "ssgwct0p81v0c"    }
    if {$CORNER == "wcl_cmax_m40_setup" }  { set MEM_PVT "ssgwct0p81vn40c"  }
    if {$CORNER == "wcl_rcmax_m40_setup"}  { set MEM_PVT "ssgwct0p81vn40c"  }
    if {$CORNER == "wc_cmax_125_hold"   }  { set MEM_PVT "ssgwct0p81v125c"  }
    if {$CORNER == "wc_rcmax_125_hold"  }  { set MEM_PVT "ssgwct0p81v125c"  }
    if {$CORNER == "wcz_cmax_0_hold"    }  { set MEM_PVT "ssgwct0p81v0c"    }
    if {$CORNER == "wcz_rcmax_0_hold"   }  { set MEM_PVT "ssgwct0p81v0c"    }
    if {$CORNER == "wcl_cmax_m40_hold"  }  { set MEM_PVT "ssgwct0p81vn40c"  }
    if {$CORNER == "wcl_rcmax_m40_hold" }  { set MEM_PVT "ssgwct0p81vn40c"  }
    if {$CORNER == "lt_cmax_m40_hold"   }  { set MEM_PVT "ffgbct0p99vn40c"  }
    if {$CORNER == "lt_rcmax_m40_hold"  }  { set MEM_PVT "ffgbct0p99vn40c"  }
    if {$CORNER == "bc_cmax_0_hold"     }  { set MEM_PVT "ffgbct0p99v0c"    }
    if {$CORNER == "bc_rcmax_0_hold"    }  { set MEM_PVT "ffgbct0p99v0c"    }
    if {$CORNER == "ml_cmax_125_hold"   }  { set MEM_PVT "ffgbct0p99v125c"  }
    if {$CORNER == "ml_rcmax_125_hold"  }  { set MEM_PVT "ffgbct0p99v125c"  }
    if {$CORNER == "lt_cmin_m40_hold"   }  { set MEM_PVT "ffgbct0p99vn40c"  }
    if {$CORNER == "lt_rcmin_m40_hold"  }  { set MEM_PVT "ffgbct0p99vn40c"  }
    if {$CORNER == "bc_cmin_0_hold"     }  { set MEM_PVT "ffgbct0p99v0c"    }
    if {$CORNER == "bc_rcmin_0_hold"    }  { set MEM_PVT "ffgbct0p99v0c"    }
    if {$CORNER == "ml_cmin_125_hold"   }  { set MEM_PVT "ffgbct0p99v125c"  }
    if {$CORNER == "ml_rcmin_125_hold"  }  { set MEM_PVT "ffgbct0p99v125c"  }
    if {$CORNER == "typical_85c"        }  { set MEM_PVT "tt0p9v85c"  }  

    if {$CORNER == "wc_cmax_125_setup"  }  { set MEM_PVTM "ssgwcT0p81v125c"  }
    if {$CORNER == "wc_rcmax_125_setup" }  { set MEM_PVTM "ssgwcT0p81v125c"  }
    if {$CORNER == "wcz_cmax_0_setup"   }  { set MEM_PVTM "ssgwcT0p81v0c"    }
    if {$CORNER == "wcz_rcmax_0_setup"  }  { set MEM_PVTM "ssgwcT0p81v0c"    }
    if {$CORNER == "wcl_cmax_m40_setup" }  { set MEM_PVTM "ssgwcT0p81vm40c"  }
    if {$CORNER == "wcl_rcmax_m40_setup"}  { set MEM_PVTM "ssgwcT0p81vm40c"  }
    if {$CORNER == "wc_cmax_125_hold"   }  { set MEM_PVTM "ssgwcT0p81v125c"  }
    if {$CORNER == "wc_rcmax_125_hold"  }  { set MEM_PVTM "ssgwcT0p81v125c"  }
    if {$CORNER == "wcz_cmax_0_hold"    }  { set MEM_PVTM "ssgwcT0p81v0c"    }
    if {$CORNER == "wcz_rcmax_0_hold"   }  { set MEM_PVTM "ssgwcT0p81v0c"    }
    if {$CORNER == "wcl_cmax_m40_hold"  }  { set MEM_PVTM "ssgwcT0p81vm40c"  }
    if {$CORNER == "wcl_rcmax_m40_hold" }  { set MEM_PVTM "ssgwcT0p81vm40c"  }
    if {$CORNER == "lt_cmax_m40_hold"   }  { set MEM_PVTM "ffgbcT0p99vm40c"  }
    if {$CORNER == "lt_rcmax_m40_hold"  }  { set MEM_PVTM "ffgbcT0p99vm40c"  }
    if {$CORNER == "bc_cmax_0_hold"     }  { set MEM_PVTM "ffgbcT0p99v0c"    }
    if {$CORNER == "bc_rcmax_0_hold"    }  { set MEM_PVTM "ffgbcT0p99v0c"    }
    if {$CORNER == "ml_cmax_125_hold"   }  { set MEM_PVTM "ffgbcT0p99v125c"  }
    if {$CORNER == "ml_rcmax_125_hold"  }  { set MEM_PVTM "ffgbcT0p99v125c"  }
    if {$CORNER == "lt_cmin_m40_hold"   }  { set MEM_PVTM "ffgbcT0p99vm40c"  }
    if {$CORNER == "lt_rcmin_m40_hold"  }  { set MEM_PVTM "ffgbcT0p99vm40c"  }
    if {$CORNER == "bc_cmin_0_hold"     }  { set MEM_PVTM "ffgbcT0p99v0c"    }
    if {$CORNER == "bc_rcmin_0_hold"    }  { set MEM_PVTM "ffgbcT0p99v0c"    }
    if {$CORNER == "ml_cmin_125_hold"   }  { set MEM_PVTM "ffgbcT0p99v125c"  }
    if {$CORNER == "ml_rcmin_125_hold"  }  { set MEM_PVTM "ffgbcT0p99v125c"  }
    if {$CORNER == "typical_85c"        }  { set MEM_PVTM "tt0p9v85c"  }  

    if {$CORNER == "wc_cmax_125_setup"  }  { set PVTM "ssg0p81v125c"  }
    if {$CORNER == "wc_rcmax_125_setup" }  { set PVTM "ssg0p81v125c"  }
    if {$CORNER == "wcz_cmax_0_setup"   }  { set PVTM "ssg0p81v0c"    }
    if {$CORNER == "wcz_rcmax_0_setup"  }  { set PVTM "ssg0p81v0c"    }
    if {$CORNER == "wcl_cmax_m40_setup" }  { set PVTM "ssg0p81vm40c"  }
    if {$CORNER == "wcl_rcmax_m40_setup"}  { set PVTM "ssg0p81vm40c"  }
    if {$CORNER == "wc_cmax_125_hold"   }  { set PVTM "ssg0p81v125c"  }
    if {$CORNER == "wc_rcmax_125_hold"  }  { set PVTM "ssg0p81v125c"  }
    if {$CORNER == "wcz_cmax_0_hold"    }  { set PVTM "ssg0p81v0c"    }
    if {$CORNER == "wcz_rcmax_0_hold"   }  { set PVTM "ssg0p81v0c"    }
    if {$CORNER == "wcl_cmax_m40_hold"  }  { set PVTM "ssg0p81vm40c"  }
    if {$CORNER == "wcl_rcmax_m40_hold" }  { set PVTM "ssg0p81vm40c"  }
    if {$CORNER == "lt_cmax_m40_hold"   }  { set PVTM "ffg0p99vm40c"  }
    if {$CORNER == "lt_rcmax_m40_hold"  }  { set PVTM "ffg0p99vm40c"  }
    if {$CORNER == "bc_cmax_0_hold"     }  { set PVTM "ffg0p99v0c"    }
    if {$CORNER == "bc_rcmax_0_hold"    }  { set PVTM "ffg0p99v0c"    }
    if {$CORNER == "ml_cmax_125_hold"   }  { set PVTM "ffg0p99v125c"  }
    if {$CORNER == "ml_rcmax_125_hold"  }  { set PVTM "ffg0p99v125c"  }
    if {$CORNER == "lt_cmin_m40_hold"   }  { set PVTM "ffg0p99vm40c"  }
    if {$CORNER == "lt_rcmin_m40_hold"  }  { set PVTM "ffg0p99vm40c"  }
    if {$CORNER == "bc_cmin_0_hold"     }  { set PVTM "ffg0p99v0c"    }
    if {$CORNER == "bc_rcmin_0_hold"    }  { set PVTM "ffg0p99v0c"    }
    if {$CORNER == "ml_cmin_125_hold"   }  { set PVTM "ffg0p99v125c"  }
    if {$CORNER == "ml_rcmin_125_hold"  }  { set PVTM "ffg0p99v125c"  }
    if {$CORNER == "ml_rcmin_125_hold"  }  { set PVTM "ffg0p99v125c"  }
    if {$CORNER == "typical_85c"        }  { set PVTM "tt0p9v85c"  }  

    if {$CORNER == "wc_cmax_125_setup"  }  { set RC_FILE "cworst_T_125"   }
    if {$CORNER == "wc_rcmax_125_setup" }  { set RC_FILE "rcworst_T_125"}
    if {$CORNER == "wcz_cmax_0_setup"   }  { set RC_FILE "cworst_T_0"   }
    if {$CORNER == "wcz_rcmax_0_setup"  }  { set RC_FILE "rcworst_T_0"  }
    if {$CORNER == "wcl_cmax_m40_setup" }  { set RC_FILE "cworst_T_m40"   }
    if {$CORNER == "wcl_rcmax_m40_setup"}  { set RC_FILE "rcworst_T_m40"  }
    if {$CORNER == "wc_cmax_125_hold"   }  { set RC_FILE "cworst_125"   }
    if {$CORNER == "wc_rcmax_125_hold"  }  { set RC_FILE "rcworst_125"  }
    if {$CORNER == "wcz_cmax_0_hold"    }  { set RC_FILE "cworst_0"   }
    if {$CORNER == "wcz_rcmax_0_hold"   }  { set RC_FILE "rcworst_0"  }
    if {$CORNER == "wcl_cmax_m40_hold"  }  { set RC_FILE "cworst_m40"   }
    if {$CORNER == "wcl_rcmax_m40_hold" }  { set RC_FILE "rcworst_m40"  }
    if {$CORNER == "lt_cmax_m40_hold"   }  { set RC_FILE "cworst_m40"   }
    if {$CORNER == "lt_rcmax_m40_hold"  }  { set RC_FILE "rcworst_m40"  }
    if {$CORNER == "bc_cmax_0_hold"     }  { set RC_FILE "cworst_0"   }
    if {$CORNER == "bc_rcmax_0_hold"    }  { set RC_FILE "rcworst_0"  }
    if {$CORNER == "ml_cmax_125_hold"   }  { set RC_FILE "cworst_125"   }
    if {$CORNER == "ml_rcmax_125_hold"  }  { set RC_FILE "rcworst_125"  }
    if {$CORNER == "lt_cmin_m40_hold"   }  { set RC_FILE "cbest_m40"    }
    if {$CORNER == "lt_rcmin_m40_hold"  }  { set RC_FILE "rcbest_m40"   }
    if {$CORNER == "bc_cmin_0_hold"     }  { set RC_FILE "cbest_0"    }
    if {$CORNER == "bc_rcmin_0_hold"    }  { set RC_FILE "rcbest_0"   }
    if {$CORNER == "ml_cmin_125_hold"   }  { set RC_FILE "cbest_125"    }
    if {$CORNER == "ml_rcmin_125_hold"  }  { set RC_FILE "rcbest_125"   }
    if {$CORNER == "typical_85c"        }  { set RC_FILE "typical_85" }

  } else {
      set PVT_IO ""
      set PVT  "ss1p08v125c"
      set PVTM "ss1p08v125c"
      set RC_FILE ""
  }
}


set MEM_DIR_SNPS              "/project/HV8107/DataBase/Digital/memory_library/snps/lib/${MEM_PVT}"
set MEM_DIR_FARA              "/project/HV8107/DataBase/Digital/memory_library/fara/lib/${MEM_PVTM}"
set MEM_DIR_ARM               "/project/HV8107/DataBase/Digital/memory_library/arm/lib/${MEM_PVTM}"

if {[regexp {_40_} $LINK_LIB]} {
#set IO_DIR_0                  "/eda/process/40/UMC_LP/IP/IO/UMK40GIOLP25MVSRFS_C02_TAPEOUTKIT/synopsys"
#set IO_DIR_1                  "/eda/process/40/UMC_LP/IP/IO/UMK40GIOLP25MVIRFS_C02_TAPEOUTKIT/synopsys"
#set IO_DIR_2                  "/eda/process/40/UMC_LP/IP/IO_KIWI/umc40lp_kiwi_io_stagger/db"
set IO_DIR_1                  "/eda/process/40/UMC_LP/IP/IO_KIWI/umc40lp_kiwi_io_inline/db"
set IO_DIR_2                  "/eda/process/40/UMC_LP/IP/IO_KIWI/umc40lp_kiwi_io_stagger_v2/db"
set TIECELL_DIR               "/eda/process/40/UMC_LP/IP/u40lp_mrom_tie/V1/db"
} elseif { [regexp {_55_} $LINK_LIB]} {

#set IO_DIR_0                  "/project/KT6806/cad/IO/UM055GIOLP25MVSRFS/synopsys"
set IO_DIR_1                  "/project/KT6806/cad/IO/UM055GIOLP25MVIRFS/synopsys"
set IO_DIR_2                  ""
set TIECELL_DIR               ""
} elseif { [regexp {_28p_} $LINK_LIB]} {
#set IO_DIR_i                  "/eda/process/40/UMC_LP/IP/IO_KIWI/umc40lp_kiwi_io_inline/db"
set IO_DIR_0                  "/eda/process/28/UMC_HPC_PLUS/IP/IO_KIWI/umc28hpcp_kiwi_io_stagger/V1/db"
set TIECELL_DIR               "/eda/process/40/UMC_LP/IP/u40lp_mrom_tie/V1/db"
} else {
set IO_DIR_0               ""
set IO_DIR_1               ""
set IO_DIR_2               ""
set TIECELL_DIR            ""
}

set mem_search_path [list \
    $MEM_DIR_SNPS \
    $MEM_DIR_FARA \
    $MEM_DIR_ARM  ]

set ana_search_path [list \
    $SNPS_LIB_DIR \
    $IO_DIR_0 \
    $TIECELL_DIR \
    [format "%s%s" $SNPS_DIR "/dw/sim_ver"] ] 


set LIB_MEM_SNPS                                "mem_snps_${MEM_PVT}_lib.db"
set LIB_MEM_SNPS_NAME                           "mem_snps_${MEM_PVT}_lib"
set LIB_MEM_FARA                                "mem_fara_${MEM_PVTM}_lib.db"
set LIB_MEM_FARA_NAME                           "mem_fara_${MEM_PVTM}_lib"
set LIB_MEM_ARM                                 "mem_arm_${MEM_PVTM}_lib.db"
set LIB_MEM_ARM_NAME                            "mem_arm_${MEM_PVTM}_lib"

set SNPS_LIB_0  "standard.sldb" 
set SNPS_LIB_1  "dw_foundation.sldb"

if {[regexp {_40_} $LINK_LIB]} {
  if {$PVT == "ss0p99v125c"      }  { set LIB_IO [list  "umc40lp_kiwi_io_inline_297c125_wc.db" "umc40lp_kiwi_io_stagger_297c125_wc.db"]}
  if {$PVT == "ss0p99vn40c"      }  { set LIB_IO [list  "umc40lp_kiwi_io_inline_297c125_wc.db" "umc40lp_kiwi_io_stagger_297c125_wc.db"]}
  if {$PVT == "ff1p21vn40c"      }  { set LIB_IO [list  "umc40lp_kiwi_io_inline_363c-40_bc.db" "umc40lp_kiwi_io_stagger_363c-40_bc.db"]}
  if {$PVT == "ff1p21v125c"      }  { set LIB_IO [list  "umc40lp_kiwi_io_inline_363c-40_bc.db" "umc40lp_kiwi_io_stagger_363c-40_bc.db"]}
  if {$PVT == "ff1p26vn40c"      }  { set LIB_IO [list  "umc40lp_kiwi_io_inline_363c-40_bc.db" "umc40lp_kiwi_io_stagger_363c-40_bc.db"]}
  if {$PVT == "ff1p26v125c"      }  { set LIB_IO [list  "umc40lp_kiwi_io_inline_363c-40_bc.db" "umc40lp_kiwi_io_stagger_363c-40_bc.db"]}
} elseif {[regexp {_28_} $LINK_LIB]} {
  if {$PVT40 == "ss0p99v125c"    }  { set LIB_IO [list "uk40giolp25mvsrfs_297c125_wc.db" "uk40giolp25mvirfs_33_wc.db" "umc40lp_kiwi_io_stagger_297c125_wc.db"]     }
  if {$PVT == "ss0p99vn40c"      }  { set LIB_IO [list ]     }
  if {$PVT == "ff1p21vn40c"      }  { set LIB_IO [list ]     }
  if {$PVT == "ff1p21v125c"      }  { set LIB_IO [list ]     } 
} elseif {[regexp {_28p_snps_} $LINK_LIB]} {
  if {$PVT == "ssgwc0p81v0c"        }  { set LIB_IO [list  "umc28hpcp_kiwi_io_stagger_ssg_0p81v_m40c.db"]  }
  if {$PVT == "ssgwc0p81v125c"      }  { set LIB_IO [list  "umc28hpcp_kiwi_io_stagger_ssg_0p81v_125c.db"]  }
  if {$PVT == "ssgwc0p81vn40c"      }  { set LIB_IO [list  "umc28hpcp_kiwi_io_stagger_ssg_0p81v_m40c.db"]  }
  if {$PVT == "ffgbc0p99v125c"      }  { set LIB_IO [list  "umc28hpcp_kiwi_io_stagger_ffg_0p99v_125c.db"]  }
  if {$PVT == "ffgbc0p99vn40c"      }  { set LIB_IO [list  "umc28hpcp_kiwi_io_stagger_ffg_0p99v_m40c.db"]  }
} elseif {[regexp {_55_} $LINK_LIB]} {
  #if {$PVT == "ss0p99vn40c"      }  { set LIB_IO [list ]     }
  set LIB_IO [list "u055giolp25mvsrfs_225c125_wc.db" "u055giolp25mvirfs_225c125_wc.db"]

} else {
  set LIB_IO   [list ] 
}

if {[regexp {_40_} $LINK_LIB]} {
  if {$PVT == "ss0p99v125c"      }  { set LIB_TIECELL [list  "u40lp_mrom_tie_ss0p99v125c.db"]}
  if {$PVT == "ss0p99vn40c"      }  { set LIB_TIECELL [list  "u40lp_mrom_tie_ss0p99vn40c.db"]}
  if {$PVT == "ff1p21vn40c"      }  { set LIB_TIECELL [list  "u40lp_mrom_tie_ff1p21vn40c.db"]}
  if {$PVT == "ff1p21v125c"      }  { set LIB_TIECELL [list  "u40lp_mrom_tie_ff1p21v125c.db"]}
} elseif {[regexp {_28p_snps_} $LINK_LIB]} { 
#temp
  if {$PVT == "ssgwc0p81v0c"     }  { set LIB_TIECELL [list  "u40lp_mrom_tie_ss0p99v125c.db"]}
  if {$PVT == "ssgwc0p81v125c"   }  { set LIB_TIECELL [list  "u40lp_mrom_tie_ss0p99vn40c.db"]}
  if {$PVT == "ssgwc0p81vn40c"   }  { set LIB_TIECELL [list  "u40lp_mrom_tie_ss0p99vn40c.db"]}
  if {$PVT == "ffgbc0p99v125c"   }  { set LIB_TIECELL [list  "u40lp_mrom_tie_ff1p21vn40c.db"]}
  if {$PVT == "ffgbc0p99vn40c"   }  { set LIB_TIECELL [list  "u40lp_mrom_tie_ff1p21v125c.db"]}
} else {
  set LIB_TIECELL   [list ]
}

set mem_link_library   [list ]
if { $MEM_FARA_EN==1 } {
  set mem_link_library [concat $mem_link_library $LIB_MEM_FARA]
}
if { $MEM_SNPS_EN==1 } {
  set mem_link_library [concat $mem_link_library $LIB_MEM_SNPS]
}
if { $MEM_ARM_EN==1 } {
  set mem_link_library [concat $mem_link_library $LIB_MEM_ARM]
}


set ana_link_library [list \
    $SNPS_LIB_0 \
    $SNPS_LIB_1]


if { $ANA_EN==1 } {
source $TCL_DIR/common_db_ana.tcl -verbose -echo
#source $TCL_DIR/common_db_dig_macro.tcl -verbose -echo
set ana_search_path [concat $ana_search_path $ana_search_path_uni]
set ana_link_library [concat $LIB_IO $LIB_TIECELL $ana_link_library $ana_link_library_uni ]
#set ana_link_library [concat $ana_link_library $ana_link_library_uni]
}

set search_path_hlmc_55_snps_7t [list \
  "/eda/process/55/HLMC/standcell/synopsys/standcell_202a/v-logic_hu55npkhlogcasdut000f/DesignWare_logic_libs/huali55nlp/uhd/base/hvt/latest/liberty/ccs" \
  "/eda/process/55/HLMC/standcell/synopsys/standcell_202a/v-logic_hu55npkslogcasdut000f/DesignWare_logic_libs/huali55nlp/uhd/base/svt/latest/liberty/ccs" \
  "/eda/process/55/HLMC/standcell/synopsys/standcell_202a/v-logic_hu55npkllogcasdut000f/DesignWare_logic_libs/huali55nlp/uhd/base/lvt/latest/liberty/ccs" \
  "/eda/process/55/HLMC/standcell/synopsys/standcell_202a/v-logic_hu55npkhlogcasdeu000f/DesignWare_logic_libs/huali55nlp/uhd/eco/hvt/latest/liberty/ccs" \
  "/eda/process/55/HLMC/standcell/synopsys/standcell_202a/v-logic_hu55npkslogcasdeu000f/DesignWare_logic_libs/huali55nlp/uhd/eco/svt/latest/liberty/ccs" \
  "/eda/process/55/HLMC/standcell/synopsys/standcell_202a/v-logic_hu55npkllogcasdeu000f/DesignWare_logic_libs/huali55nlp/uhd/eco/lvt/latest/liberty/ccs"]
set search_path_hlmc_55_snps_9t [list \
  "/eda/process/55/HLMC/standcell/synopsys/standcell_202a/v-logic_hu55npkhlogcasdst000f/DesignWare_logic_libs/huali55nlp/hd/base/hvt/latest/liberty/ccs" \
  "/eda/process/55/HLMC/standcell/synopsys/standcell_202a/v-logic_hu55npkslogcasdst000f/DesignWare_logic_libs/huali55nlp/hd/base/svt/latest/liberty/ccs" \
  "/eda/process/55/HLMC/standcell/synopsys/standcell_202a/v-logic_hu55npkllogcasdst000f/DesignWare_logic_libs/huali55nlp/hd/base/lvt/latest/liberty/ccs" \
  "/eda/process/55/HLMC/standcell/synopsys/standcell_202a/v-logic_hu55npkhlogcasdet000f/DesignWare_logic_libs/huali55nlp/hd/eco/hvt/latest/liberty/ccs" \
  "/eda/process/55/HLMC/standcell/synopsys/standcell_202a/v-logic_hu55npkslogcasdet000f/DesignWare_logic_libs/huali55nlp/hd/eco/svt/latest/liberty/ccs" \
  "/eda/process/55/HLMC/standcell/synopsys/standcell_202a/v-logic_hu55npkllogcasdet000f/DesignWare_logic_libs/huali55nlp/hd/eco/lvt/latest/liberty/ccs"]
set search_path_umc_55_fara_7t [list \
  "/eda/process/55/UMC_LP/standcell/Faraday/7t/2017Q1v2.0/fsf0l_ehs/2017Q1v2.0/GENERIC_CORE/FrontEnd/synopsys/synthesis" \
  "/eda/process/55/UMC_LP/standcell/Faraday/7t/2017Q1v2.0/fsf0l_ers/2017Q1v2.0/GENERIC_CORE/FrontEnd/synopsys/synthesis" \
  "/eda/process/55/UMC_LP/standcell/Faraday/7t/2017Q1v2.0/fsf0l_els/2017Q1v2.0/GENERIC_CORE/FrontEnd/synopsys/synthesis"]


#set search_path_umc_55_fara_7t [list \
#  "/eda/process/55/UMC_LP/standcell/Faraday/7t/2017Q1v1.0/fsf0l_ers/2013Q1v1.0/GENERIC_CORE/FrontEnd/synopsys/synthesis" \
#  "/eda/process/55/UMC_LP/standcell/Faraday/7t/2017Q1v1.0/fsf0l_els/2013Q1v1.0/GENERIC_CORE/FrontEnd/synopsys/synthesis"]
set search_path_umc_55_fara_8t [list \
  "/eda/process/55/UMC_LP/standcell/Faraday/8t/2013Q1v1.0/fsf0l_drs/2013Q1v1.0/GENERIC_CORE/FrontEnd/synopsys/synthesis" \
  "/eda/process/55/UMC_LP/standcell/Faraday/8t/2013Q1v1.0/fsf0l_dls/2013Q1v1.0/GENERIC_CORE/FrontEnd/synopsys/synthesis" ]
set search_path_umc_55_snps_7t [list \
  "/eda/process/55/UMC_LP/standcell/UMC/G-9LT-LOGIC_MIXED_MODE55N-LP_LOW_K_UM055LSCLPMVBDH-LIBRARY_TAPE_OUT_KIT-Ver.B01_P.B/synopsys/ccs" \
  "/eda/process/55/UMC_LP/standcell/UMC/G-9LT-LOGIC_MIXED_MODE55N-LP_LOW_K_UM055LSCLPMVBDH-LIBRARY_TAPE_OUT_KIT-Ver.B01_P.B/synopsys/ccs"]
set search_path_umc_55_snps_8t [list ]

set search_path_umc_40_fara_7t [list \
  "/eda/process/40/UMC_LP/standcell/Faraday/7t/2018Q2v2.2/fsh0l_ehs/2018Q2v2.2/GENERIC_CORE/FrontEnd/synopsys/synthesis" \
  "/eda/process/40/UMC_LP/standcell/Faraday/7t/2018Q2v2.2/fsh0l_ers/2018Q2v2.2/GENERIC_CORE/FrontEnd/synopsys/synthesis" \
  "/eda/process/40/UMC_LP/standcell/Faraday/7t/2018Q2v2.2/fsh0l_els/2018Q2v2.2/GENERIC_CORE/FrontEnd/synopsys/synthesis"]
set search_path_umc_40_fara_9t [list \
  "/eda/process/40/UMC_LP/standcell/Faraday/9t/2017Q3v1.1/fsh0l_bhs/2017Q3v1.1/GENERIC_CORE/FrontEnd/synopsys/synthesis" \
  "/eda/process/40/UMC_LP/standcell/Faraday/9t/2017Q3v1.1/fsh0l_brs/2017Q3v1.1/GENERIC_CORE/FrontEnd/synopsys/synthesis" \
  "/eda/process/40/UMC_LP/standcell/Faraday/9t/2017Q3v1.1/fsh0l_bls/2017Q4v1.1/GENERIC_CORE/FrontEnd/synopsys/synthesis"]
set search_path_umc_40_snps_9t [list \
  "/eda/process/40/UMC_LP/standcell/synopsys/V5.00A/v-logic_um40npkhlogcasdst000f/DesignWare_logic_libs/umc40nlp/hd/base/hvt/latest/liberty/ccs" \
  "/eda/process/40/UMC_LP/standcell/synopsys/V5.00A/v-logic_um40npkslogcasdst000f/DesignWare_logic_libs/umc40nlp/hd/base/svt/latest/liberty/ccs" \
  "/eda/process/40/UMC_LP/standcell/synopsys/V5.00A/v-logic_um40npkllogcasdst000f/DesignWare_logic_libs/umc40nlp/hd/base/lvt/latest/liberty/ccs"]

set search_path_umc_28_arm_9t_hpc [list \
  "/eda/process/28/UMC_HPC/standcell/UMC_L28HPC_SC9MCZ_FB/arm/umc/l28hpc/sc9mcpp140z_base_hvt_c30/r1p0/db" \
  "/eda/process/28/UMC_HPC/standcell/UMC_L28HPC_SC9MCZ_FB/arm/umc/l28hpc/sc9mcpp140z_base_rvt_c30/r1p0/db" \
  "/eda/process/28/UMC_HPC/standcell/UMC_L28HPC_SC9MCZ_FB/arm/umc/l28hpc/sc9mcpp140z_base_lvt_c30/r1p0/db"]

set search_path_umc_28p_arm_7t_hpc [list \
  "/eda/process/28/UMC_HPC_PLUS/standcell/Arm/7t/arm/umc/l28hpcp/sc7mcpp140z_base_hvt_c40/r0p1/db-ccs-tn-scm" \
  "/eda/process/28/UMC_HPC_PLUS/standcell/Arm/7t/arm/umc/l28hpcp/sc7mcpp140z_base_hvt_c35/r0p1/db-ccs-tn-scm" \
  "/eda/process/28/UMC_HPC_PLUS/standcell/Arm/7t/arm/umc/l28hpcp/sc7mcpp140z_base_hvt_c30/r0p1/db-ccs-tn-scm" \
  "/eda/process/28/UMC_HPC_PLUS/standcell/Arm/7t/arm/umc/l28hpcp/sc7mcpp140z_base_svt_c40/r0p1/db-ccs-tn-scm" \
  "/eda/process/28/UMC_HPC_PLUS/standcell/Arm/7t/arm/umc/l28hpcp/sc7mcpp140z_base_svt_c35/r0p1/db-ccs-tn-scm" \
  "/eda/process/28/UMC_HPC_PLUS/standcell/Arm/7t/arm/umc/l28hpcp/sc7mcpp140z_base_svt_c30/r0p1/db-ccs-tn-scm" \
  "/eda/process/28/UMC_HPC_PLUS/standcell/Arm/7t/arm/umc/l28hpcp/sc7mcpp140z_base_lvt_c40/r0p1/db-ccs-tn-scm" \
  "/eda/process/28/UMC_HPC_PLUS/standcell/Arm/7t/arm/umc/l28hpcp/sc7mcpp140z_base_lvt_c35/r0p1/db-ccs-tn-scm" \
  "/eda/process/28/UMC_HPC_PLUS/standcell/Arm/7t/arm/umc/l28hpcp/sc7mcpp140z_base_lvt_c30/r0p1/db-ccs-tn-scm" ]

set search_path_umc_28p_arm_9t_hpc [list \
  "/eda/process/28/UMC_HPC_PLUS/standcell/Arm/9t/arm/umc/l28hpcp/sc9mcpp140z_base_hvt_c40/r0p1/db-ccs-tn-scm" \
  "/eda/process/28/UMC_HPC_PLUS/standcell/Arm/9t/arm/umc/l28hpcp/sc9mcpp140z_base_hvt_c35/r0p1/db-ccs-tn-scm" \
  "/eda/process/28/UMC_HPC_PLUS/standcell/Arm/9t/arm/umc/l28hpcp/sc9mcpp140z_base_hvt_c30/r0p1/db-ccs-tn-scm" \
  "/eda/process/28/UMC_HPC_PLUS/standcell/Arm/9t/arm/umc/l28hpcp/sc9mcpp140z_base_svt_c40/r0p1/db-ccs-tn-scm" \
  "/eda/process/28/UMC_HPC_PLUS/standcell/Arm/9t/arm/umc/l28hpcp/sc9mcpp140z_base_svt_c35/r0p1/db-ccs-tn-scm" \
  "/eda/process/28/UMC_HPC_PLUS/standcell/Arm/9t/arm/umc/l28hpcp/sc9mcpp140z_base_svt_c30/r0p1/db-ccs-tn-scm" \
  "/eda/process/28/UMC_HPC_PLUS/standcell/Arm/9t/arm/umc/l28hpcp/sc9mcpp140z_base_lvt_c40/r0p1/db-ccs-tn-scm" \
  "/eda/process/28/UMC_HPC_PLUS/standcell/Arm/9t/arm/umc/l28hpcp/sc9mcpp140z_base_lvt_c35/r0p1/db-ccs-tn-scm" \
  "/eda/process/28/UMC_HPC_PLUS/standcell/Arm/9t/arm/umc/l28hpcp/sc9mcpp140z_base_lvt_c30/r0p1/db-ccs-tn-scm" ]

set search_path_umc_28p_arm_12t_hpc [list \
  "/eda/process/28/UMC_HPC_PLUS/standcell/Arm/12t/arm/umc/l28hpcp/sc12mcpp140z_base_hvt_c40/r0p1/db-ccs-tn-scm" \
  "/eda/process/28/UMC_HPC_PLUS/standcell/Arm/12t/arm/umc/l28hpcp/sc12mcpp140z_base_hvt_c35/r0p1/db-ccs-tn-scm" \
  "/eda/process/28/UMC_HPC_PLUS/standcell/Arm/12t/arm/umc/l28hpcp/sc12mcpp140z_base_hvt_c30/r0p1/db-ccs-tn-scm" \
  "/eda/process/28/UMC_HPC_PLUS/standcell/Arm/12t/arm/umc/l28hpcp/sc12mcpp140z_base_svt_c40/r0p1/db-ccs-tn-scm" \
  "/eda/process/28/UMC_HPC_PLUS/standcell/Arm/12t/arm/umc/l28hpcp/sc12mcpp140z_base_svt_c35/r0p1/db-ccs-tn-scm" \
  "/eda/process/28/UMC_HPC_PLUS/standcell/Arm/12t/arm/umc/l28hpcp/sc12mcpp140z_base_svt_c30/r0p1/db-ccs-tn-scm" \
  "/eda/process/28/UMC_HPC_PLUS/standcell/Arm/12t/arm/umc/l28hpcp/sc12mcpp140z_base_lvt_c40/r0p1/db-ccs-tn-scm" \
  "/eda/process/28/UMC_HPC_PLUS/standcell/Arm/12t/arm/umc/l28hpcp/sc12mcpp140z_base_lvt_c35/r0p1/db-ccs-tn-scm" \
  "/eda/process/28/UMC_HPC_PLUS/standcell/Arm/12t/arm/umc/l28hpcp/sc12mcpp140z_base_lvt_c30/r0p1/db-ccs-tn-scm" ]

set search_path_umc_28p_snps_ud [list \
  "/eda/process/28/UMC_HPC_PLUS/standcell/synopsys/hvt/v-logic_um28nphhlogl30udh140f/DesignWare_logic_libs/umc28nlph/30uhd/udh/hvt/latest/liberty/ccs" \
  "/eda/process/28/UMC_HPC_PLUS/standcell/synopsys/hvt/v-logic_um28nphhlogl30udl140f/DesignWare_logic_libs/umc28nlph/30uhd/udl/hvt/latest/liberty/ccs" \
  "/eda/process/28/UMC_HPC_PLUS/standcell/synopsys/hvt/v-logic_um28nphhlogl30udp140f/DesignWare_logic_libs/umc28nlph/30uhd/udp/hvt/latest/liberty/ccs" \
  "/eda/process/28/UMC_HPC_PLUS/standcell/synopsys/hvt/v-logic_um28nphhlogl35udh140f/DesignWare_logic_libs/umc28nlph/35uhd/udh/hvt/latest/liberty/ccs" \
  "/eda/process/28/UMC_HPC_PLUS/standcell/synopsys/hvt/v-logic_um28nphhlogl35udl140f/DesignWare_logic_libs/umc28nlph/35uhd/udl/hvt/latest/liberty/ccs" \
  "/eda/process/28/UMC_HPC_PLUS/standcell/synopsys/hvt/v-logic_um28nphhlogl35udp140f/DesignWare_logic_libs/umc28nlph/35uhd/udp/hvt/latest/liberty/ccs" \
  "/eda/process/28/UMC_HPC_PLUS/standcell/synopsys/hvt/v-logic_um28nphhlogl40udh140f/DesignWare_logic_libs/umc28nlph/40uhd/udh/hvt/latest/liberty/ccs" \
  "/eda/process/28/UMC_HPC_PLUS/standcell/synopsys/hvt/v-logic_um28nphhlogl40udl140f/DesignWare_logic_libs/umc28nlph/40uhd/udl/hvt/latest/liberty/ccs" \
  "/eda/process/28/UMC_HPC_PLUS/standcell/synopsys/hvt/v-logic_um28nphhlogl40udp140f/DesignWare_logic_libs/umc28nlph/40uhd/udp/hvt/latest/liberty/ccs" \
  "/eda/process/28/UMC_HPC_PLUS/standcell/synopsys/svt/v-logic_um28nphslogl30udl140f/DesignWare_logic_libs/umc28nlph/30uhd/udl/svt/latest/liberty/ccs" \
  "/eda/process/28/UMC_HPC_PLUS/standcell/synopsys/svt/v-logic_um28nphslogl30udh140f/DesignWare_logic_libs/umc28nlph/30uhd/udh/svt/latest/liberty/ccs" \
  "/eda/process/28/UMC_HPC_PLUS/standcell/synopsys/svt/v-logic_um28nphslogl30udp140f/DesignWare_logic_libs/umc28nlph/30uhd/udp/svt/latest/liberty/ccs" \
  "/eda/process/28/UMC_HPC_PLUS/standcell/synopsys/svt/v-logic_um28nphslogl35udh140f/DesignWare_logic_libs/umc28nlph/35uhd/udh/svt/latest/liberty/ccs" \
  "/eda/process/28/UMC_HPC_PLUS/standcell/synopsys/svt/v-logic_um28nphslogl35udl140f/DesignWare_logic_libs/umc28nlph/35uhd/udl/svt/latest/liberty/ccs" \
  "/eda/process/28/UMC_HPC_PLUS/standcell/synopsys/svt/v-logic_um28nphslogl35udp140f/DesignWare_logic_libs/umc28nlph/35uhd/udp/svt/latest/liberty/ccs" \
  "/eda/process/28/UMC_HPC_PLUS/standcell/synopsys/svt/v-logic_um28nphslogl40udh140f/DesignWare_logic_libs/umc28nlph/40uhd/udh/svt/latest/liberty/ccs" \
  "/eda/process/28/UMC_HPC_PLUS/standcell/synopsys/svt/v-logic_um28nphslogl40udl140f/DesignWare_logic_libs/umc28nlph/40uhd/udl/svt/latest/liberty/ccs" \
  "/eda/process/28/UMC_HPC_PLUS/standcell/synopsys/svt/v-logic_um28nphslogl40udp140f/DesignWare_logic_libs/umc28nlph/40uhd/udp/svt/latest/liberty/ccs" ]

set search_path_tsmc_22ulp_tsmc_7t [list \
  "/eda/process/22/TSMC_CLN/standcell/tsmc/tcbn22ulpbwp7t30p140_100d/AN61001_20190412/TSMCHOME/digital/Front_End/timing_power_noise/CCS/tcbn22ulpbwp7t30p140_100d" \
  "/eda/process/22/TSMC_CLN/standcell/tsmc/tcbn22ulpbwp7t30p140hvt_100d/AN61001_20190412/TSMCHOME/digital/Front_End/timing_power_noise/CCS/tcbn22ulpbwp7t30p140hvt_100d" \
  "/eda/process/22/TSMC_CLN/standcell/tsmc/tcbn22ulpbwp7t30p140lvt_100d/AN61001_20190412/TSMCHOME/digital/Front_End/timing_power_noise/CCS/tcbn22ulpbwp7t30p140lvt_100d" \
  "/eda/process/22/TSMC_CLN/standcell/tsmc/tcbn22ulpbwp7t30p140mb_100d/0K56002_20200703/TSMCHOME/digital/Front_End/timing_power_noise/CCS/tcbn22ulpbwp7t30p140mb_100d" \
  "/eda/process/22/TSMC_CLN/standcell/tsmc/tcbn22ulpbwp7t30p140mbhvt_100d/0K56002_20200703/TSMCHOME/digital/Front_End/timing_power_noise/CCS/tcbn22ulpbwp7t30p140mbhvt_100d" \
  "/eda/process/22/TSMC_CLN/standcell/tsmc/tcbn22ulpbwp7t30p140mblvt_100d/0K56002_20200703/TSMCHOME/digital/Front_End/timing_power_noise/CCS/tcbn22ulpbwp7t30p140mblvt_100d" \
  "/eda/process/22/TSMC_CLN/standcell/tsmc/tcbn22ulpbwp7t30p140pm_100d/AN61001_20190412/TSMCHOME/digital/Front_End/timing_power_noise/CCS/tcbn22ulpbwp7t30p140pm_100d" \
  "/eda/process/22/TSMC_CLN/standcell/tsmc/tcbn22ulpbwp7t30p140pmhvt_100d/AN61001_20190412/TSMCHOME/digital/Front_End/timing_power_noise/CCS/tcbn22ulpbwp7t30p140pmhvt_100d" \
  "/eda/process/22/TSMC_CLN/standcell/tsmc/tcbn22ulpbwp7t30p140pmlvt_100d/AN61001_20190412/TSMCHOME/digital/Front_End/timing_power_noise/CCS/tcbn22ulpbwp7t30p140pmlvt_100d" \
  "/eda/process/22/TSMC_CLN/standcell/tsmc/tcbn22ulpbwp7t35p140_100d/AN61001_20190412/TSMCHOME/digital/Front_End/timing_power_noise/CCS/tcbn22ulpbwp7t35p140_100d" \
  "/eda/process/22/TSMC_CLN/standcell/tsmc/tcbn22ulpbwp7t35p140hvt_100d/AN61001_20190412/TSMCHOME/digital/Front_End/timing_power_noise/CCS/tcbn22ulpbwp7t35p140hvt_100d" \
  "/eda/process/22/TSMC_CLN/standcell/tsmc/tcbn22ulpbwp7t35p140lvt_100d/AN61001_20190412/TSMCHOME/digital/Front_End/timing_power_noise/CCS/tcbn22ulpbwp7t35p140lvt_100d" \
  "/eda/process/22/TSMC_CLN/standcell/tsmc/tcbn22ulpbwp7t35p140mb_100d/0K56002_20200703/TSMCHOME/digital/Front_End/timing_power_noise/CCS/tcbn22ulpbwp7t35p140mb_100d" \
  "/eda/process/22/TSMC_CLN/standcell/tsmc/tcbn22ulpbwp7t35p140mbhvt_100d/0K56002_20200703/TSMCHOME/digital/Front_End/timing_power_noise/CCS/tcbn22ulpbwp7t35p140mbhvt_100d" \
  "/eda/process/22/TSMC_CLN/standcell/tsmc/tcbn22ulpbwp7t35p140mblvt_100d/0K56002_20200703/TSMCHOME/digital/Front_End/timing_power_noise/CCS/tcbn22ulpbwp7t35p140mblvt_100d" \
  "/eda/process/22/TSMC_CLN/standcell/tsmc/tcbn22ulpbwp7t35p140pm_100d/AN61001_20190412/TSMCHOME/digital/Front_End/timing_power_noise/CCS/tcbn22ulpbwp7t35p140pm_100d" \
  "/eda/process/22/TSMC_CLN/standcell/tsmc/tcbn22ulpbwp7t35p140pmhvt_100d/AN61001_20190412/TSMCHOME/digital/Front_End/timing_power_noise/CCS/tcbn22ulpbwp7t35p140pmhvt_100d" \
  "/eda/process/22/TSMC_CLN/standcell/tsmc/tcbn22ulpbwp7t35p140pmlvt_100d/AN61001_20190412/TSMCHOME/digital/Front_End/timing_power_noise/CCS/tcbn22ulpbwp7t35p140pmlvt_100d" \
  "/eda/process/22/TSMC_CLN/standcell/tsmc/tcbn22ulpbwp7t40p140_100d/AN61001_20190412/TSMCHOME/digital/Front_End/timing_power_noise/CCS/tcbn22ulpbwp7t40p140_100d" \
  "/eda/process/22/TSMC_CLN/standcell/tsmc/tcbn22ulpbwp7t40p140hvt_100d/AN61001_20190412/TSMCHOME/digital/Front_End/timing_power_noise/CCS/tcbn22ulpbwp7t40p140hvt_100d" \
  "/eda/process/22/TSMC_CLN/standcell/tsmc/tcbn22ulpbwp7t40p140lvt_100d/AN61001_20190412/TSMCHOME/digital/Front_End/timing_power_noise/CCS/tcbn22ulpbwp7t40p140lvt_100d" \
  "/eda/process/22/TSMC_CLN/standcell/tsmc/tcbn22ulpbwp7t40p140mb_100d/0K56002_20200703/TSMCHOME/digital/Front_End/timing_power_noise/CCS/tcbn22ulpbwp7t40p140mb_100d" \
  "/eda/process/22/TSMC_CLN/standcell/tsmc/tcbn22ulpbwp7t40p140mbhvt_100d/0K56002_20200703/TSMCHOME/digital/Front_End/timing_power_noise/CCS/tcbn22ulpbwp7t40p140mbhvt_100d" \
  "/eda/process/22/TSMC_CLN/standcell/tsmc/tcbn22ulpbwp7t40p140mblvt_100d/0K56002_20200703/TSMCHOME/digital/Front_End/timing_power_noise/CCS/tcbn22ulpbwp7t40p140mblvt_100d" \
  "/eda/process/22/TSMC_CLN/standcell/tsmc/tcbn22ulpbwp7t40p140pm_100d/AN61001_20190412/TSMCHOME/digital/Front_End/timing_power_noise/CCS/tcbn22ulpbwp7t40p140pm_100d" \
  "/eda/process/22/TSMC_CLN/standcell/tsmc/tcbn22ulpbwp7t40p140pmhvt_100d/AN61001_20190412/TSMCHOME/digital/Front_End/timing_power_noise/CCS/tcbn22ulpbwp7t40p140pmhvt_100d" \
  "/eda/process/22/TSMC_CLN/standcell/tsmc/tcbn22ulpbwp7t40p140pmlvt_100d/AN61001_20190412/TSMCHOME/digital/Front_End/timing_power_noise/CCS/tcbn22ulpbwp7t40p140pmlvt_100d" ]

set search_path_tsmc_22ulp_tsmc_9t [list \
  "/eda/process/22/TSMC_CLN/standcell/tsmc/tcbn22ulpbwp30p140_100d/AN61001_20190412/TSMCHOME/digital/Front_End/timing_power_noise/CCS/tcbn22ulpbwp30p140_100d" \
  "/eda/process/22/TSMC_CLN/standcell/tsmc/tcbn22ulpbwp30p140hvt_100d/AN61001_20190412/TSMCHOME/digital/Front_End/timing_power_noise/CCS/tcbn22ulpbwp30p140hvt_100d" \
  "/eda/process/22/TSMC_CLN/standcell/tsmc/tcbn22ulpbwp30p140lvt_100d/AN61001_20190412/TSMCHOME/digital/Front_End/timing_power_noise/CCS/tcbn22ulpbwp30p140lvt_100d" \
  "/eda/process/22/TSMC_CLN/standcell/tsmc/tcbn22ulpbwp30p140pm_100d/AN61001_20190412/TSMCHOME/digital/Front_End/timing_power_noise/CCS/tcbn22ulpbwp30p140pm_100d" \
  "/eda/process/22/TSMC_CLN/standcell/tsmc/tcbn22ulpbwp30p140pmhvt_100d/AN61001_20190412/TSMCHOME/digital/Front_End/timing_power_noise/CCS/tcbn22ulpbwp30p140pmhvt_100d" \
  "/eda/process/22/TSMC_CLN/standcell/tsmc/tcbn22ulpbwp30p140pmlvt_100d/AN61001_20190412/TSMCHOME/digital/Front_End/timing_power_noise/CCS/tcbn22ulpbwp30p140pmlvt_100d" \
  "/eda/process/22/TSMC_CLN/standcell/tsmc/tcbn22ulpbwp35p140_100d/AN61001_20190412/TSMCHOME/digital/Front_End/timing_power_noise/CCS/tcbn22ulpbwp35p140_100d" \
  "/eda/process/22/TSMC_CLN/standcell/tsmc/tcbn22ulpbwp35p140hvt_100d/AN61001_20190412/TSMCHOME/digital/Front_End/timing_power_noise/CCS/tcbn22ulpbwp35p140hvt_100d" \
  "/eda/process/22/TSMC_CLN/standcell/tsmc/tcbn22ulpbwp35p140lvt_100d/AN61001_20190412/TSMCHOME/digital/Front_End/timing_power_noise/CCS/tcbn22ulpbwp35p140lvt_100d" \
  "/eda/process/22/TSMC_CLN/standcell/tsmc/tcbn22ulpbwp35p140pm_100d/AN61001_20190412/TSMCHOME/digital/Front_End/timing_power_noise/CCS/tcbn22ulpbwp35p140pm_100d" \
  "/eda/process/22/TSMC_CLN/standcell/tsmc/tcbn22ulpbwp35p140pmhvt_100d/AN61001_20190412/TSMCHOME/digital/Front_End/timing_power_noise/CCS/tcbn22ulpbwp35p140pmhvt_100d" \
  "/eda/process/22/TSMC_CLN/standcell/tsmc/tcbn22ulpbwp35p140pmlvt_100d/AN61001_20190412/TSMCHOME/digital/Front_End/timing_power_noise/CCS/tcbn22ulpbwp35p140pmlvt_100d" \
  "/eda/process/22/TSMC_CLN/standcell/tsmc/tcbn22ulpbwp40p140_100d/AN61001_20190412/TSMCHOME/digital/Front_End/timing_power_noise/CCS/tcbn22ulpbwp40p140_100d" \
  "/eda/process/22/TSMC_CLN/standcell/tsmc/tcbn22ulpbwp40p140hvt_100d/AN61001_20190412/TSMCHOME/digital/Front_End/timing_power_noise/CCS/tcbn22ulpbwp40p140hvt_100d" \
  "/eda/process/22/TSMC_CLN/standcell/tsmc/tcbn22ulpbwp40p140lvt_100d/AN61001_20190412/TSMCHOME/digital/Front_End/timing_power_noise/CCS/tcbn22ulpbwp40p140lvt_100d" \
  "/eda/process/22/TSMC_CLN/standcell/tsmc/tcbn22ulpbwp40p140pm_100d/AN61001_20190412/TSMCHOME/digital/Front_End/timing_power_noise/CCS/tcbn22ulpbwp40p140pm_100d" \
  "/eda/process/22/TSMC_CLN/standcell/tsmc/tcbn22ulpbwp40p140pmhvt_100d/AN61001_20190412/TSMCHOME/digital/Front_End/timing_power_noise/CCS/tcbn22ulpbwp40p140pmhvt_100d" \
  "/eda/process/22/TSMC_CLN/standcell/tsmc/tcbn22ulpbwp40p140pmlvt_100d/AN61001_20190412/TSMCHOME/digital/Front_End/timing_power_noise/CCS/tcbn22ulpbwp40p140pmlvt_100d" ]

set library_hlmc_55_snps_7t [list \
  "hu55npkhdut_${PVTM}.db" \
  "hu55npksdut_${PVTM}.db" \
  "hu55npkldut_${PVTM}.db"]
set hvt_hlmc_55_snps_7t                  "hu55npkhdut_${PVTM}"
set svt_hlmc_55_snps_7t                  "hu55npksdut_${PVTM}"
set lvt_hlmc_55_snps_7t                  "hu55npkldut_${PVTM}"

set library_hlmc_55_snps_9t [list \
  "hu55npkhdst_${PVTM}.db" \
  "hu55npksdst_${PVTM}.db" \
  "hu55npkldst_${PVTM}.db"]
set hvt_hlmc_55_snps_9t                  "hu55npkhdst_${PVTM}"
set svt_hlmc_55_snps_9t                  "hu55npksdst_${PVTM}"
set lvt_hlmc_55_snps_9t                  "hu55npkldst_${PVTM}"


#set library_umc_55_fara_7t [list \
#  "fsf0l_ers_generic_core_${PVTM}.db" \
#  "fsf0l_els_generic_core_${PVTM}.db"]

set library_umc_55_fara_7t [list \
  "fsf0l_ers_generic_core_${PVTM}.db"]


set hvt_umc_55_fara_7t                   ""
set svt_umc_55_fara_7t                   "fsf0l_ers_generic_core_${PVTM}"
#set lvt_umc_55_fara_7t                   "fsf0l_els_generic_core_${PVTM}"
set lvt_umc_55_fara_7t                   ""

set library_umc_55_fara_8t [list \
  "fsf0l_drs_generic_core_${PVTM}.db" \
  "fsf0l_dls_generic_core_${PVTM}.db"]
set hvt_umc_55_fara_8t                   ""
set svt_umc_55_fara_8t                   "fsf0l_drs_generic_core_${PVTM}"
set lvt_umc_55_fara_8t                   "fsf0l_dls_generic_core_${PVTM}"

set library_umc_55_snps_7t [list \
  "u055lsclpmvbdh_108c125_wc_ccs.db" \
  "u055lsclpmvbdh_108c125_wc_ccs.db"]
set hvt_umc_55_snps_7t                   ""
set svt_umc_55_snps_7t                   "u055lsclpmvbdh_108c125_wc_ccs"
set lvt_umc_55_snps_7t                   "u055lsclpmvbdh_108c125_wc_ccs"

set library_umc_55_snps_8t [list ]
set hvt_umc_55_snps_8t                   ""
set svt_umc_55_snps_8t                   ""
set lvt_umc_55_snps_8t                   ""

if { $synopsys_program_name == "pt_shell" } {
  set library_umc_40_fara_7t [list \
    "fsh0l_ehs_generic_core_${PVTM}.db" \
    "fsh0l_ers_generic_core_${PVTM}.db" \
    "fsh0l_els_generic_core_${PVTM}.db"]
  set hvt_umc_40_fara_7t                   "fsh0l_ehs_generic_core_${PVTM}"
  set svt_umc_40_fara_7t                   "fsh0l_ers_generic_core_${PVTM}"
  set lvt_umc_40_fara_7t                   "fsh0l_els_generic_core_${PVTM}"

  set library_umc_40_fara_9t [list \
    "fsh0l_bhs_generic_core_${PVTM}.db" \
    "fsh0l_brs_generic_core_${PVTM}.db" \
    "fsh0l_bls_generic_core_${PVTM}.db"]
  set hvt_umc_40_fara_9t                   "fsh0l_bhs_generic_core_${PVTM}"
  set svt_umc_40_fara_9t                   "fsh0l_brs_generic_core_${PVTM}"
  set lvt_umc_40_fara_9t                   "fsh0l_bls_generic_core_${PVTM}"
} else {
  set library_umc_40_fara_7t [list \
    "fsh0l_ers_generic_core_${PVTM}.db" \
    "fsh0l_els_generic_core_${PVTM}.db"] 
  set hvt_umc_40_fara_7t                   ""
  set svt_umc_40_fara_7t                   "fsh0l_ers_generic_core_${PVTM}"
  set lvt_umc_40_fara_7t                   "fsh0l_els_generic_core_${PVTM}"

  set library_umc_40_fara_9t [list \
    "fsh0l_brs_generic_core_${PVTM}.db" \
    "fsh0l_bls_generic_core_${PVTM}.db"]
  set hvt_umc_40_fara_9t                   ""
  set svt_umc_40_fara_9t                   "fsh0l_brs_generic_core_${PVTM}"
  set lvt_umc_40_fara_9t                   "fsh0l_bls_generic_core_${PVTM}"

}

set library_umc_28_arm_9t_hpc [list \
  "sc9mcpp140z_l28hpc_base_hvt_c30_${PVT}.db" \
  "sc9mcpp140z_l28hpc_base_rvt_c30_${PVT}.db" \
  "sc9mcpp140z_l28hpc_base_lvt_c30_${PVT}.db"]
set hvt_umc_28_arm_9t_hpc_c30            "sc9mcpp140z_l28hpc_base_hvt_c30_${PVT}"
set rvt_umc_28_arm_9t_hpc_c30            "sc9mcpp140z_l28hpc_base_rvt_c30_${PVT}"
set lvt_umc_28_arm_9t_hpc_c30            "sc9mcpp140z_l28hpc_base_lvt_c30_${PVT}"

### JWEI, 20181113
if { $LVT_EN==1 } {
  set library_umc_28p_arm_7t_hpc [list \
    "sc7mcpp140z_l28hpcp_base_hvt_c40_${PVT}.db_ccs_tn_sh5cm" \
    "sc7mcpp140z_l28hpcp_base_hvt_c35_${PVT}.db_ccs_tn_sh5cm" \
    "sc7mcpp140z_l28hpcp_base_hvt_c30_${PVT}.db_ccs_tn_sh5cm" \
    "sc7mcpp140z_l28hpcp_base_svt_c40_${PVT}.db_ccs_tn_sh5cm" \
    "sc7mcpp140z_l28hpcp_base_svt_c35_${PVT}.db_ccs_tn_sh5cm" \
    "sc7mcpp140z_l28hpcp_base_svt_c30_${PVT}.db_ccs_tn_sh5cm" \
    "sc7mcpp140z_l28hpcp_base_lvt_c40_${PVT}.db_ccs_tn_sh5cm" \
    "sc7mcpp140z_l28hpcp_base_lvt_c35_${PVT}.db_ccs_tn_sh5cm" \
    "sc7mcpp140z_l28hpcp_base_lvt_c30_${PVT}.db_ccs_tn_sh5cm" ]
  set library_umc_28p_arm_9t_hpc [list \
    "sc9mcpp140z_l28hpcp_base_hvt_c40_${PVT}.db_ccs_tn_sh5cm" \
    "sc9mcpp140z_l28hpcp_base_hvt_c35_${PVT}.db_ccs_tn_sh5cm" \
    "sc9mcpp140z_l28hpcp_base_hvt_c30_${PVT}.db_ccs_tn_sh5cm" \
    "sc9mcpp140z_l28hpcp_base_svt_c40_${PVT}.db_ccs_tn_sh5cm" \
    "sc9mcpp140z_l28hpcp_base_svt_c35_${PVT}.db_ccs_tn_sh5cm" \
    "sc9mcpp140z_l28hpcp_base_svt_c30_${PVT}.db_ccs_tn_sh5cm" \
    "sc9mcpp140z_l28hpcp_base_lvt_c40_${PVT}.db_ccs_tn_sh5cm" \
    "sc9mcpp140z_l28hpcp_base_lvt_c35_${PVT}.db_ccs_tn_sh5cm" \
    "sc9mcpp140z_l28hpcp_base_lvt_c30_${PVT}.db_ccs_tn_sh5cm" ]
  set library_umc_28p_arm_12t_hpc [list \
    "sc12mcpp140z_l28hpcp_base_hvt_c40_${PVT}.db_ccs_tn_sh5cm" \
    "sc12mcpp140z_l28hpcp_base_hvt_c35_${PVT}.db_ccs_tn_sh5cm" \
    "sc12mcpp140z_l28hpcp_base_hvt_c30_${PVT}.db_ccs_tn_sh5cm" \
    "sc12mcpp140z_l28hpcp_base_svt_c40_${PVT}.db_ccs_tn_sh5cm" \
    "sc12mcpp140z_l28hpcp_base_svt_c35_${PVT}.db_ccs_tn_sh5cm" \
    "sc12mcpp140z_l28hpcp_base_svt_c30_${PVT}.db_ccs_tn_sh5cm" \
    "sc12mcpp140z_l28hpcp_base_lvt_c40_${PVT}.db_ccs_tn_sh5cm" \
    "sc12mcpp140z_l28hpcp_base_lvt_c35_${PVT}.db_ccs_tn_sh5cm" \
    "sc12mcpp140z_l28hpcp_base_lvt_c30_${PVT}.db_ccs_tn_sh5cm" ]
} else {
  set library_umc_28p_arm_7t_hpc [list \
    "sc7mcpp140z_l28hpcp_base_hvt_c40_${PVT}.db_ccs_tn_sh5cm" \
    "sc7mcpp140z_l28hpcp_base_hvt_c35_${PVT}.db_ccs_tn_sh5cm" \
    "sc7mcpp140z_l28hpcp_base_hvt_c30_${PVT}.db_ccs_tn_sh5cm" \
    "sc7mcpp140z_l28hpcp_base_svt_c40_${PVT}.db_ccs_tn_sh5cm" \
    "sc7mcpp140z_l28hpcp_base_svt_c35_${PVT}.db_ccs_tn_sh5cm" \
    "sc7mcpp140z_l28hpcp_base_svt_c30_${PVT}.db_ccs_tn_sh5cm" ]
  set library_umc_28p_arm_9t_hpc [list \
    "sc9mcpp140z_l28hpcp_base_hvt_c40_${PVT}.db_ccs_tn_sh5cm" \
    "sc9mcpp140z_l28hpcp_base_hvt_c35_${PVT}.db_ccs_tn_sh5cm" \
    "sc9mcpp140z_l28hpcp_base_hvt_c30_${PVT}.db_ccs_tn_sh5cm" \
    "sc9mcpp140z_l28hpcp_base_svt_c40_${PVT}.db_ccs_tn_sh5cm" \
    "sc9mcpp140z_l28hpcp_base_svt_c35_${PVT}.db_ccs_tn_sh5cm" \
    "sc9mcpp140z_l28hpcp_base_svt_c30_${PVT}.db_ccs_tn_sh5cm" ]
  set library_umc_28p_arm_12t_hpc [list \
    "sc12mcpp140z_l28hpcp_base_hvt_c40_${PVT}.db_ccs_tn_sh5cm" \
    "sc12mcpp140z_l28hpcp_base_hvt_c35_${PVT}.db_ccs_tn_sh5cm" \
    "sc12mcpp140z_l28hpcp_base_hvt_c30_${PVT}.db_ccs_tn_sh5cm" \
    "sc12mcpp140z_l28hpcp_base_svt_c40_${PVT}.db_ccs_tn_sh5cm" \
    "sc12mcpp140z_l28hpcp_base_svt_c35_${PVT}.db_ccs_tn_sh5cm" \
    "sc12mcpp140z_l28hpcp_base_svt_c30_${PVT}.db_ccs_tn_sh5cm" ]
}

set hvt_umc_28p_arm_7t_hpc_c40            "sc7mcpp140z_l28hpcp_base_hvt_c40_${PVT}"
set hvt_umc_28p_arm_7t_hpc_c35            "sc7mcpp140z_l28hpcp_base_hvt_c35_${PVT}"
set hvt_umc_28p_arm_7t_hpc_c30            "sc7mcpp140z_l28hpcp_base_hvt_c30_${PVT}"
set svt_umc_28p_arm_7t_hpc_c40            "sc7mcpp140z_l28hpcp_base_svt_c40_${PVT}"
set svt_umc_28p_arm_7t_hpc_c35            "sc7mcpp140z_l28hpcp_base_svt_c35_${PVT}"
set svt_umc_28p_arm_7t_hpc_c30            "sc7mcpp140z_l28hpcp_base_svt_c30_${PVT}"
set lvt_umc_28p_arm_7t_hpc_c40            "sc7mcpp140z_l28hpcp_base_lvt_c40_${PVT}"
set lvt_umc_28p_arm_7t_hpc_c35            "sc7mcpp140z_l28hpcp_base_lvt_c35_${PVT}"
set lvt_umc_28p_arm_7t_hpc_c30            "sc7mcpp140z_l28hpcp_base_lvt_c30_${PVT}"

set hvt_umc_28p_arm_9t_hpc_c40            "sc9mcpp140z_l28hpcp_base_hvt_c40_${PVT}"
set hvt_umc_28p_arm_9t_hpc_c35            "sc9mcpp140z_l28hpcp_base_hvt_c35_${PVT}"
set hvt_umc_28p_arm_9t_hpc_c30            "sc9mcpp140z_l28hpcp_base_hvt_c30_${PVT}"
set svt_umc_28p_arm_9t_hpc_c40            "sc9mcpp140z_l28hpcp_base_svt_c40_${PVT}"
set svt_umc_28p_arm_9t_hpc_c35            "sc9mcpp140z_l28hpcp_base_svt_c35_${PVT}"
set svt_umc_28p_arm_9t_hpc_c30            "sc9mcpp140z_l28hpcp_base_svt_c30_${PVT}"
set lvt_umc_28p_arm_9t_hpc_c40            "sc9mcpp140z_l28hpcp_base_lvt_c40_${PVT}"
set lvt_umc_28p_arm_9t_hpc_c35            "sc9mcpp140z_l28hpcp_base_lvt_c35_${PVT}"
set lvt_umc_28p_arm_9t_hpc_c30            "sc9mcpp140z_l28hpcp_base_lvt_c30_${PVT}"

set hvt_umc_28p_arm_12t_hpc_c40           "sc12mcpp140z_l28hpcp_base_hvt_c40_${PVT}"
set hvt_umc_28p_arm_12t_hpc_c35           "sc12mcpp140z_l28hpcp_base_hvt_c35_${PVT}"
set hvt_umc_28p_arm_12t_hpc_c30           "sc12mcpp140z_l28hpcp_base_hvt_c30_${PVT}"
set svt_umc_28p_arm_12t_hpc_c40           "sc12mcpp140z_l28hpcp_base_svt_c40_${PVT}"
set svt_umc_28p_arm_12t_hpc_c35           "sc12mcpp140z_l28hpcp_base_svt_c35_${PVT}"
set svt_umc_28p_arm_12t_hpc_c30           "sc12mcpp140z_l28hpcp_base_svt_c30_${PVT}"
set lvt_umc_28p_arm_12t_hpc_c40           "sc12mcpp140z_l28hpcp_base_lvt_c40_${PVT}"
set lvt_umc_28p_arm_12t_hpc_c35           "sc12mcpp140z_l28hpcp_base_lvt_c35_${PVT}"
set lvt_umc_28p_arm_12t_hpc_c30           "sc12mcpp140z_l28hpcp_base_lvt_c30_${PVT}"

set library_umc_28p_snps_ud [list \
    "um28nphhlogl30udh140f_${PVT}.db" \
    "um28nphhlogl30udl140f_${PVT}.db" \
    "um28nphhlogl30udp140f_${PVT}.db" \
    "um28nphhlogl35udh140f_${PVT}.db" \
    "um28nphhlogl35udl140f_${PVT}.db" \
    "um28nphhlogl35udp140f_${PVT}.db" \
    "um28nphhlogl40udh140f_${PVT}.db" \
    "um28nphhlogl40udl140f_${PVT}.db" \
    "um28nphhlogl40udp140f_${PVT}.db" \
    "um28nphslogl30udh140f_${PVT}.db" \
    "um28nphslogl30udl140f_${PVT}.db" \
    "um28nphslogl30udp140f_${PVT}.db" \
    "um28nphslogl35udh140f_${PVT}.db" \
    "um28nphslogl35udl140f_${PVT}.db" \
    "um28nphslogl35udp140f_${PVT}.db" \
    "um28nphslogl40udh140f_${PVT}.db" \
    "um28nphslogl40udl140f_${PVT}.db" \
    "um28nphslogl40udp140f_${PVT}.db" ]

set hvt_umc_28p_snps_30udh                "um28nphhlogl30udh140f_${PVT}"
set hvt_umc_28p_snps_30udl                "um28nphhlogl30udl140f_${PVT}"
set hvt_umc_28p_snps_30udp                "um28nphhlogl30udp140f_${PVT}"
set hvt_umc_28p_snps_35udh                "um28nphhlogl35udh140f_${PVT}"
set hvt_umc_28p_snps_35udl                "um28nphhlogl35udl140f_${PVT}"
set hvt_umc_28p_snps_35udp                "um28nphhlogl35udp140f_${PVT}"
set hvt_umc_28p_snps_40udh                "um28nphhlogl40udh140f_${PVT}"
set hvt_umc_28p_snps_40udl                "um28nphhlogl40udl140f_${PVT}"
set hvt_umc_28p_snps_40udp                "um28nphhlogl40udp140f_${PVT}"
set svt_umc_28p_snps_30udh                "um28nphslogl30udh140f_${PVT}"
set svt_umc_28p_snps_30udl                "um28nphslogl30udl140f_${PVT}"
set svt_umc_28p_snps_30udp                "um28nphslogl30udp140f_${PVT}"
set svt_umc_28p_snps_35udh                "um28nphslogl35udh140f_${PVT}"
set svt_umc_28p_snps_35udl                "um28nphslogl35udl140f_${PVT}"
set svt_umc_28p_snps_35udp                "um28nphslogl35udp140f_${PVT}"
set svt_umc_28p_snps_40udh                "um28nphslogl40udh140f_${PVT}"
set svt_umc_28p_snps_40udl                "um28nphslogl40udl140f_${PVT}"
set svt_umc_28p_snps_40udp                "um28nphslogl40udp140f_${PVT}"
if {$LVT_EN == 1} {
set library_tsmc_22ulp_tsmc_7t [list \
    "tcbn22ulpbwp7t30p140${PVTM}_ccs.db" \
    "tcbn22ulpbwp7t30p140hvt${PVTM}_ccs.db" \
    "tcbn22ulpbwp7t30p140mb${PVTM}_ccs.db" \
    "tcbn22ulpbwp7t30p140mbhvt${PVTM}_ccs.db" \
    "tcbn22ulpbwp7t30p140pm${PVTM}_ccs.db" \
    "tcbn22ulpbwp7t30p140pmhvt${PVTM}_ccs.db" \
    "tcbn22ulpbwp7t35p140${PVTM}_ccs.db" \
    "tcbn22ulpbwp7t35p140hvt${PVTM}_ccs.db" \
    "tcbn22ulpbwp7t35p140mb${PVTM}_ccs.db" \
    "tcbn22ulpbwp7t35p140mbhvt${PVTM}_ccs.db" \
    "tcbn22ulpbwp7t35p140pm${PVTM}_ccs.db" \
    "tcbn22ulpbwp7t35p140pmhvt${PVTM}_ccs.db" \
    "tcbn22ulpbwp7t40p140${PVTM}_ccs.db" \
    "tcbn22ulpbwp7t40p140hvt${PVTM}_ccs.db" \
    "tcbn22ulpbwp7t40p140mb${PVTM}_ccs.db" \
    "tcbn22ulpbwp7t40p140mbhvt${PVTM}_ccs.db" \
    "tcbn22ulpbwp7t40p140pm${PVTM}_ccs.db" \
    "tcbn22ulpbwp7t40p140pmhvt${PVTM}_ccs.db" \
    "tcbn22ulpbwp7t30p140lvt${PVTM}_ccs.db"    \
    "tcbn22ulpbwp7t30p140mblvt${PVTM}_ccs.db"  \
    "tcbn22ulpbwp7t30p140pmlvt${PVTM}_ccs.db"  \
    "tcbn22ulpbwp7t35p140lvt${PVTM}_ccs.db"    \
    "tcbn22ulpbwp7t35p140mblvt${PVTM}_ccs.db"  \
    "tcbn22ulpbwp7t35p140pmlvt${PVTM}_ccs.db"  \
    "tcbn22ulpbwp7t40p140lvt${PVTM}_ccs.db"   \
    "tcbn22ulpbwp7t40p140mblvt${PVTM}_ccs.db" \
    "tcbn22ulpbwp7t40p140pmlvt${PVTM}_ccs.db" \
    ]
} else {
set library_tsmc_22ulp_tsmc_7t [list \
    "tcbn22ulpbwp7t30p140${PVTM}_ccs.db" \
    "tcbn22ulpbwp7t30p140hvt${PVTM}_ccs.db" \
    "tcbn22ulpbwp7t30p140mb${PVTM}_ccs.db" \
    "tcbn22ulpbwp7t30p140mbhvt${PVTM}_ccs.db" \
    "tcbn22ulpbwp7t30p140pm${PVTM}_ccs.db" \
    "tcbn22ulpbwp7t30p140pmhvt${PVTM}_ccs.db" \
    "tcbn22ulpbwp7t35p140${PVTM}_ccs.db" \
    "tcbn22ulpbwp7t35p140hvt${PVTM}_ccs.db" \
    "tcbn22ulpbwp7t35p140mb${PVTM}_ccs.db" \
    "tcbn22ulpbwp7t35p140mbhvt${PVTM}_ccs.db" \
    "tcbn22ulpbwp7t35p140pm${PVTM}_ccs.db" \
    "tcbn22ulpbwp7t35p140pmhvt${PVTM}_ccs.db" \
    "tcbn22ulpbwp7t40p140${PVTM}_ccs.db" \
    "tcbn22ulpbwp7t40p140hvt${PVTM}_ccs.db" \
    "tcbn22ulpbwp7t40p140mb${PVTM}_ccs.db" \
    "tcbn22ulpbwp7t40p140mbhvt${PVTM}_ccs.db" \
    "tcbn22ulpbwp7t40p140pm${PVTM}_ccs.db" \
    "tcbn22ulpbwp7t40p140pmhvt${PVTM}_ccs.db" \
    ]
}
set hvt_tsmc_22ulp_tsmc_30_7t                "tcbn22ulpbwp7t30p140hvt${PVTM}_ccs"
set hvt_tsmc_22ulp_tsmc_30mb_7t              "tcbn22ulpbwp7t30p140mbhvt${PVTM}_ccs"
set hvt_tsmc_22ulp_tsmc_30pm_7t              "tcbn22ulpbwp7t30p140pmhvt${PVTM}_ccs"
set hvt_tsmc_22ulp_tsmc_35_7t                "tcbn22ulpbwp7t35p140hvt${PVTM}_ccs"
set hvt_tsmc_22ulp_tsmc_35mb_7t              "tcbn22ulpbwp7t35p140mbhvt${PVTM}_ccs"
set hvt_tsmc_22ulp_tsmc_35pm_7t              "tcbn22ulpbwp7t35p140pmhvt${PVTM}_ccs"
set hvt_tsmc_22ulp_tsmc_40_7t                "tcbn22ulpbwp7t40p140hvt${PVTM}_ccs"
set hvt_tsmc_22ulp_tsmc_40mb_7t              "tcbn22ulpbwp7t40p140mbhvt${PVTM}_ccs"
set hvt_tsmc_22ulp_tsmc_40pm_7t              "tcbn22ulpbwp7t40p140pmhvt${PVTM}_ccs"
set svt_tsmc_22ulp_tsmc_30_7t                "tcbn22ulpbwp7t30p140${PVTM}_ccs"
set svt_tsmc_22ulp_tsmc_30mb_7t              "tcbn22ulpbwp7t30p140mb${PVTM}_ccs"
set svt_tsmc_22ulp_tsmc_30pm_7t              "tcbn22ulpbwp7t30p140pm${PVTM}_ccs"
set svt_tsmc_22ulp_tsmc_35_7t                "tcbn22ulpbwp7t35p140${PVTM}_ccs"
set svt_tsmc_22ulp_tsmc_35mb_7t              "tcbn22ulpbwp7t35p140mb${PVTM}_ccs"
set svt_tsmc_22ulp_tsmc_35pm_7t              "tcbn22ulpbwp7t35p140pm${PVTM}_ccs"
set svt_tsmc_22ulp_tsmc_40_7t                "tcbn22ulpbwp7t40p140${PVTM}_ccs"
set svt_tsmc_22ulp_tsmc_40mb_7t              "tcbn22ulpbwp7t40p140mb${PVTM}_ccs"
set svt_tsmc_22ulp_tsmc_40pm_7t              "tcbn22ulpbwp7t40p140pm${PVTM}_ccsi"
set lvt_tsmc_22ulp_tsmc_30_7t                "tcbn22ulpbwp7t30p140lvt${PVTM}_ccs"
set lvt_tsmc_22ulp_tsmc_30mb_7t              "tcbn22ulpbwp7t30p140mblvt${PVTM}_ccs"
set lvt_tsmc_22ulp_tsmc_30pm_7t              "tcbn22ulpbwp7t30p140pmlvt${PVTM}_ccs"
set lvt_tsmc_22ulp_tsmc_35_7t                "tcbn22ulpbwp7t35p140lvt${PVTM}_ccs"
set lvt_tsmc_22ulp_tsmc_35mb_7t              "tcbn22ulpbwp7t35p140mblvt${PVTM}_ccs"
set lvt_tsmc_22ulp_tsmc_35pm_7t              "tcbn22ulpbwp7t35p140pmlvt${PVTM}_ccs"
set lvt_tsmc_22ulp_tsmc_40_7t                "tcbn22ulpbwp7t40p140lvt${PVTM}_ccs"
set lvt_tsmc_22ulp_tsmc_40mb_7t              "tcbn22ulpbwp7t40p140mblvt${PVTM}_ccs"
set lvt_tsmc_22ulp_tsmc_40pm_7t              "tcbn22ulpbwp7t40p140pmlvt${PVTM}_ccs"

if {$LVT_EN == 1} {
set library_tsmc_22ulp_tsmc_9t [list \
    "tcbn22ulpbwp30p140${PVTM}_ccs.db" \
    "tcbn22ulpbwp30p140hvt${PVTM}_ccs.db" \
    "tcbn22ulpbwp30p140pm${PVTM}_ccs.db" \
    "tcbn22ulpbwp30p140pmhvt${PVTM}_ccs.db" \
    "tcbn22ulpbwp35p140${PVTM}_ccs.db" \
    "tcbn22ulpbwp35p140hvt${PVTM}_ccs.db" \
    "tcbn22ulpbwp35p140pm${PVTM}_ccs.db" \
    "tcbn22ulpbwp35p140pmhvt${PVTM}_ccs.db" \
    "tcbn22ulpbwp40p140${PVTM}_ccs.db" \
    "tcbn22ulpbwp40p140hvt${PVTM}_ccs.db" \
    "tcbn22ulpbwp40p140pm${PVTM}_ccs.db" \
    "tcbn22ulpbwp40p140pmhvt${PVTM}_ccs.db" \
    "tcbn22ulpbwp30p140lvt${PVTM}_ccs.db"   \
    "tcbn22ulpbwp30p140pmlvt${PVTM}_ccs.db"  \
    "tcbn22ulpbwp35p140lvt${PVTM}_ccs.db"   \
    "tcbn22ulpbwp35p140pmlvt${PVTM}_ccs.db"  \
    "tcbn22ulpbwp40p140lvt${PVTM}_ccs.db"   \
    "tcbn22ulpbwp40p140pmlvt${PVTM}_ccs.db" \
  ]
} else {

set library_tsmc_22ulp_tsmc_9t [list \
    "tcbn22ulpbwp30p140${PVTM}_ccs.db" \
    "tcbn22ulpbwp30p140hvt${PVTM}_ccs.db" \
    "tcbn22ulpbwp30p140pm${PVTM}_ccs.db" \
    "tcbn22ulpbwp30p140pmhvt${PVTM}_ccs.db" \
    "tcbn22ulpbwp35p140${PVTM}_ccs.db" \
    "tcbn22ulpbwp35p140hvt${PVTM}_ccs.db" \
    "tcbn22ulpbwp35p140pm${PVTM}_ccs.db" \
    "tcbn22ulpbwp35p140pmhvt${PVTM}_ccs.db" \
    "tcbn22ulpbwp40p140${PVTM}_ccs.db" \
    "tcbn22ulpbwp40p140hvt${PVTM}_ccs.db" \
    "tcbn22ulpbwp40p140pm${PVTM}_ccs.db" \
    "tcbn22ulpbwp40p140pmhvt${PVTM}_ccs.db" ]

}


set hvt_tsmc_22ulp_tsmc_30_9t                "tcbn22ulpbwp30p140hvt${PVTM}_ccs"
set hvt_tsmc_22ulp_tsmc_30pm_9t              "tcbn22ulpbwp30p140pmhvt${PVTM}_ccs"
set hvt_tsmc_22ulp_tsmc_35_9t                "tcbn22ulpbwp35p140hvt${PVTM}_ccs"
set hvt_tsmc_22ulp_tsmc_35pm_9t              "tcbn22ulpbwp35p140pmhvt${PVTM}_ccs"
set hvt_tsmc_22ulp_tsmc_40_9t                "tcbn22ulpbwp40p140hvt${PVTM}_ccs"
set hvt_tsmc_22ulp_tsmc_40pm_9t              "tcbn22ulpbwp40p140pmhvt${PVTM}_ccs"
set svt_tsmc_22ulp_tsmc_30_9t                "tcbn22ulpbwp30p140${PVTM}_ccs"
set svt_tsmc_22ulp_tsmc_30pm_9t              "tcbn22ulpbwp30p140pm${PVTM}_ccs"
set svt_tsmc_22ulp_tsmc_35_9t                "tcbn22ulpbwp35p140${PVTM}_ccs"
set svt_tsmc_22ulp_tsmc_35pm_9t              "tcbn22ulpbwp35p140pm${PVTM}_ccs"
set svt_tsmc_22ulp_tsmc_40_9t                "tcbn22ulpbwp40p140${PVTM}_ccs"
set svt_tsmc_22ulp_tsmc_40pm_9t              "tcbn22ulpbwp40p140pm${PVTM}_ccs"

set lvt_tsmc_22ulp_tsmc_30_9t                "tcbn22ulpbwp30p140lvt${PVTM}_ccs"
set lvt_tsmc_22ulp_tsmc_30pm_9t              "tcbn22ulpbwp30p140pmlvt${PVTM}_ccs"
set lvt_tsmc_22ulp_tsmc_35_9t                "tcbn22ulpbwp35p140lvt${PVTM}_ccs"
set lvt_tsmc_22ulp_tsmc_35pm_9t              "tcbn22ulpbwp35p140pmlvt${PVTM}_ccs"
set lvt_tsmc_22ulp_tsmc_40_9t                "tcbn22ulpbwp40p140lvt${PVTM}_ccs"
set lvt_tsmc_22ulp_tsmc_40pm_9t              "tcbn22ulpbwp40p140pmlvt${PVTM}_ccs"

set library_umc_40_snps_9t [list \
  "um40npkhdst_${PVTM}.db" \
  "um40npksdst_${PVTM}.db" \
  "um40npkldst_${PVTM}.db"]
set hvt_umc_40_snps_9t                   "um40npkhdst_${PVTM}"
set svt_umc_40_snps_9t                   "um40npksdst_${PVTM}"
set lvt_umc_40_snps_9t                   "um40npkldst_${PVTM}"


set serch_path       [list ]
if { [regexp {hlmc_55_snps_7t} $LINK_LIB] || [regexp {hlmc_55_snps_7t} $TAR_LIB] } {
  set search_path [concat $search_path $search_path_hlmc_55_snps_7t]
} 
if { [regexp {hlmc_55_snps_9t} $LINK_LIB] || [regexp {hlmc_55_snps_9t} $TAR_LIB] } {
  set search_path [concat $search_path $search_path_hlmc_55_snps_9t]
} 
if { [regexp {umc_55_fara_7t} $LINK_LIB] || [regexp {umc_55_fara_7t} $TAR_LIB] } {
  set search_path [concat $search_path $search_path_umc_55_fara_7t]
}
if { [regexp {umc_55_fara_8t} $LINK_LIB] || [regexp {umc_55_fara_8t} $TAR_LIB] } {
  set search_path [concat $search_path $search_path_umc_55_fara_8t]
}
if { [regexp {umc_55_snps_7t} $LINK_LIB] || [regexp {umc_55_snps_7t} $TAR_LIB] } {
  set search_path [concat $search_path $search_path_umc_55_snps_7t]
}
if { [regexp {umc_55_snps_8t} $LINK_LIB] || [regexp {umc_55_snps_8t} $TAR_LIB] } {
  set search_path [concat $search_path $search_path_umc_55_snps_8t]
}
if { [regexp {umc_40_fara_7t} $LINK_LIB] || [regexp {umc_40_fara_7t} $TAR_LIB] } {
  set search_path [concat $search_path $search_path_umc_40_fara_7t]
}
if { [regexp {umc_40_fara_9t} $LINK_LIB] || [regexp {umc_40_fara_9t} $TAR_LIB] } {
  set search_path [concat $search_path $search_path_umc_40_fara_9t]
}
if { [regexp {umc_40_snps_9t} $LINK_LIB] || [regexp {umc_40_snps_9t} $TAR_LIB] } {
  set search_path [concat $search_path $search_path_umc_40_snps_9t]
}

if { [regexp {umc_28_arm_9t_hpc} $LINK_LIB] || [regexp {umc_28_arm_9t_hpc} $TAR_LIB] } {
  set search_path [concat $search_path $search_path_umc_28_arm_9t_hpc]
}

if { [regexp {umc_28p_arm_7t_hpc} $LINK_LIB] || [regexp {umc_28p_arm_7t_hpc} $TAR_LIB] } {
  set search_path [concat $search_path $search_path_umc_28p_arm_7t_hpc]
}
if { [regexp {umc_28p_arm_9t_hpc} $LINK_LIB] || [regexp {umc_28p_arm_9t_hpc} $TAR_LIB] } {
  set search_path [concat $search_path $search_path_umc_28p_arm_9t_hpc]
}
if { [regexp {umc_28p_arm_12t_hpc} $LINK_LIB] || [regexp {umc_28p_arm_12t_hpc} $TAR_LIB] } {
  set search_path [concat $search_path $search_path_umc_28p_arm_12t_hpc]
}
if { [regexp {umc_28p_snps_ud} $LINK_LIB] || [regexp {umc_28p_snps_ud} $TAR_LIB] } {
  set search_path [concat $search_path $search_path_umc_28p_snps_ud]
}

if {$synopsys_program_name != "pt_shell"} {
if { [regexp {tsmc_22ulp_tsmc_7t} $LINK_LIB] || [regexp {tsmc_22ulp_tsmc_7t} $TAR_LIB] } {
  set search_path [concat $search_path $search_path_tsmc_22ulp_tsmc_7t]
}
if { [regexp {tsmc_22ulp_tsmc_9t} $LINK_LIB] || [regexp {tsmc_22ulp_tsmc_9t} $TAR_LIB] } {
  set search_path [concat $search_path $search_path_tsmc_22ulp_tsmc_9t]
}
} else {
if { [regexp {tsmc_22ulp_tsmc} $LINK_LIB] || [regexp {tsmc_22ulp_tsmc} $TAR_LIB] } {
  set search_path [concat $search_path $search_path_tsmc_22ulp_tsmc_7t $search_path_tsmc_22ulp_tsmc_9t]
}
}
set search_path [concat $search_path $mem_search_path $ana_search_path]



set link_library     [list ]
set lib_svt_name     [list ]
set lib_hvt_name     [list ]
set lib_lvt_name     [list ]
if { [regexp {hlmc_55_snps_7t} $LINK_LIB] } {
  set link_library [concat $link_library $library_hlmc_55_snps_7t]
} 
if { [regexp {hlmc_55_snps_9t} $LINK_LIB] } {
  set link_library [concat $link_library $library_hlmc_55_snps_9t]
} 
if { [regexp {umc_55_fara_7t} $LINK_LIB]  } {
  set link_library [concat $link_library $library_umc_55_fara_7t]

}
if { [regexp {umc_55_fara_8t} $LINK_LIB]  } {
  set link_library [concat $link_library $library_umc_55_fara_8t]

}
if { [regexp {umc_55_snps_7t} $LINK_LIB]  } {
  set link_library [concat $link_library $library_umc_55_snps_7t]

}
if { [regexp {umc_55_snps_8t} $LINK_LIB]  } {
  set link_library [concat $link_library $library_umc_55_snps_8t]

}
if { [regexp {umc_40_fara_7t} $LINK_LIB]  } {
  set link_library [concat $link_library $library_umc_40_fara_7t]

}
if { [regexp {umc_40_fara_9t} $LINK_LIB]  } {
  set link_library [concat $link_library $library_umc_40_fara_9t]

}
if { [regexp {umc_40_snps_9t} $LINK_LIB]  } {
  set link_library [concat $link_library $library_umc_40_snps_9t]

}
if { [regexp {umc_28_arm_9t_hpc} $LINK_LIB]  } {
  set link_library [concat $link_library $library_umc_28_arm_9t_hpc]
}

if { [regexp {umc_28p_arm_7t_hpc} $LINK_LIB]  } {
  set link_library [concat $link_library $library_umc_28p_arm_7t_hpc]
}
if { [regexp {umc_28p_arm_9t_hpc} $LINK_LIB]  } {
  set link_library [concat $link_library $library_umc_28p_arm_9t_hpc]
}
if { [regexp {umc_28p_arm_12t_hpc} $LINK_LIB]  } {
  set link_library [concat $link_library $library_umc_28p_arm_12t_hpc]
}
if { [regexp {umc_28p_snps_ud} $LINK_LIB]  } {
  set link_library [concat $link_library $library_umc_28p_snps_ud]
}
if {$synopsys_program_name != "pt_shell"} {
if { [regexp {tsmc_22ulp_tsmc_7t} $LINK_LIB]  } {
  set link_library [concat $link_library $library_tsmc_22ulp_tsmc_7t]
}
if { [regexp {tsmc_22ulp_tsmc_9t} $LINK_LIB]  } {
  set link_library [concat $link_library $library_tsmc_22ulp_tsmc_9t]
}
} else {
if { [regexp {tsmc_22ulp_tsmc} $LINK_LIB]  } {
  set link_library [concat $link_library $library_tsmc_22ulp_tsmc_7t $library_tsmc_22ulp_tsmc_9t]
}
}

set target_library     [list ]
if { [regexp {hlmc_55_snps_7t} $TAR_LIB] } {
  set target_library [concat $target_library $library_hlmc_55_snps_7t]
  set lib_svt_name [concat $lib_svt_name $svt_hlmc_55_snps_7t]
  set lib_hvt_name [concat $lib_hvt_name $hvt_hlmc_55_snps_7t]
  set lib_lvt_name [concat $lib_lvt_name $lvt_hlmc_55_snps_7t]
} 
if { [regexp {hlmc_55_snps_9t} $TAR_LIB] } {
  set target_library [concat $target_library $library_hlmc_55_snps_9t]
  set lib_svt_name [concat $lib_svt_name $svt_hlmc_55_snps_9t]
  set lib_hvt_name [concat $lib_hvt_name $hvt_hlmc_55_snps_9t]
  set lib_lvt_name [concat $lib_lvt_name $lvt_hlmc_55_snps_9t]
} 
if { [regexp {umc_55_fara_7t} $TAR_LIB]  } {
  set target_library [concat $target_library $library_umc_55_fara_7t]
  set lib_svt_name [concat $lib_svt_name $svt_umc_55_fara_7t]
  set lib_hvt_name [concat $lib_hvt_name $hvt_umc_55_fara_7t]
  set lib_lvt_name [concat $lib_lvt_name $lvt_umc_55_fara_7t]
}
if { [regexp {umc_55_fara_8t} $TAR_LIB]  } {
  set target_library [concat $target_library $library_umc_55_fara_8t]
  set lib_svt_name [concat $lib_svt_name $svt_umc_55_fara_8t]
  set lib_hvt_name [concat $lib_hvt_name $hvt_umc_55_fara_8t]
  set lib_lvt_name [concat $lib_lvt_name $lvt_umc_55_fara_8t]
}
if { [regexp {umc_55_snps_7t} $TAR_LIB]  } {
  set target_library [concat $target_library $library_umc_55_snps_7t]
  set lib_svt_name [concat $lib_svt_name $svt_umc_55_snps_7t]
  set lib_hvt_name [concat $lib_hvt_name $hvt_umc_55_snps_7t]
  set lib_lvt_name [concat $lib_lvt_name $lvt_umc_55_snps_7t]
}
if { [regexp {umc_55_snps_8t} $TAR_LIB]  } {
  set target_library [concat $target_library $library_umc_55_snps_8t]
  set lib_svt_name [concat $lib_svt_name $svt_umc_55_snps_8t]
  set lib_hvt_name [concat $lib_hvt_name $hvt_umc_55_snps_8t]
  set lib_lvt_name [concat $lib_lvt_name $lvt_umc_55_snps_8t]
}
if { [regexp {umc_40_fara_7t} $TAR_LIB]  } {
  set target_library [concat $target_library $library_umc_40_fara_7t]
  set lib_svt_name [concat $lib_svt_name $svt_umc_40_fara_7t]
  set lib_hvt_name [concat $lib_hvt_name $hvt_umc_40_fara_7t]
  set lib_lvt_name [concat $lib_lvt_name $lvt_umc_40_fara_7t]
}
if { [regexp {umc_40_fara_9t} $TAR_LIB]  } {
  set target_library [concat $target_library $library_umc_40_fara_9t]
  set lib_svt_name [concat $lib_svt_name $svt_umc_40_fara_9t]
  set lib_hvt_name [concat $lib_hvt_name $hvt_umc_40_fara_9t]
  set lib_lvt_name [concat $lib_lvt_name $lvt_umc_40_fara_9t]
}
if { [regexp {umc_40_snps_9t} $TAR_LIB]  } {
  set target_library [concat $target_library $library_umc_40_snps_9t]
  set lib_svt_name [concat $lib_svt_name $svt_umc_40_snps_9t]
  set lib_hvt_name [concat $lib_hvt_name $hvt_umc_40_snps_9t]
  set lib_lvt_name [concat $lib_lvt_name $lvt_umc_40_snps_9t]
}

if { [regexp {umc_28_arm_9t_hpc} $TAR_LIB]  } {
  set target_library [concat $target_library $library_umc_28_arm_9t_hpc]
  set lib_hvt_name [concat $lib_hvt_name $hvt_umc_28_arm_9t_hpc_c30]
  set lib_svt_name [concat $lib_svt_name $rvt_umc_28_arm_9t_hpc_c30]
  set lib_lvt_name [concat $lib_lvt_name $lvt_umc_28_arm_9t_hpc_c30]
}

if { [regexp {umc_28p_arm_7t_hpc} $TAR_LIB]  } {
  set target_library [concat $target_library $library_umc_28p_arm_7t_hpc]
  set lib_hvt_name [concat $lib_hvt_name $hvt_umc_28p_arm_7t_hpc_c40 $hvt_umc_28p_arm_7t_hpc_c35 $hvt_umc_28p_arm_7t_hpc_c30]
  set lib_svt_name [concat $lib_svt_name $svt_umc_28p_arm_7t_hpc_c40 $svt_umc_28p_arm_7t_hpc_c35 $svt_umc_28p_arm_7t_hpc_c30]
  set lib_lvt_name [concat $lib_lvt_name $lvt_umc_28p_arm_7t_hpc_c40 $lvt_umc_28p_arm_7t_hpc_c35 $lvt_umc_28p_arm_7t_hpc_c30]
}
if { [regexp {umc_28p_arm_9t_hpc} $TAR_LIB]  } {
  set target_library [concat $target_library $library_umc_28p_arm_9t_hpc]
  set lib_hvt_name [concat $lib_hvt_name $hvt_umc_28p_arm_9t_hpc_c40 $hvt_umc_28p_arm_9t_hpc_c35 $hvt_umc_28p_arm_9t_hpc_c30]
  set lib_svt_name [concat $lib_svt_name $svt_umc_28p_arm_9t_hpc_c40 $svt_umc_28p_arm_9t_hpc_c35 $svt_umc_28p_arm_9t_hpc_c30]
  set lib_lvt_name [concat $lib_lvt_name $lvt_umc_28p_arm_9t_hpc_c40 $lvt_umc_28p_arm_9t_hpc_c35 $lvt_umc_28p_arm_9t_hpc_c30]
}
if { [regexp {umc_28p_arm_12t_hpc} $TAR_LIB]  } {
  set target_library [concat $target_library $library_umc_28p_arm_12t_hpc]
  set lib_hvt_name [concat $lib_hvt_name $hvt_umc_28p_arm_12t_hpc_c40 $hvt_umc_28p_arm_12t_hpc_c35 $hvt_umc_28p_arm_12t_hpc_c30]
  set lib_svt_name [concat $lib_svt_name $svt_umc_28p_arm_12t_hpc_c40 $svt_umc_28p_arm_12t_hpc_c35 $svt_umc_28p_arm_12t_hpc_c30]
  set lib_lvt_name [concat $lib_lvt_name $lvt_umc_28p_arm_12t_hpc_c40 $lvt_umc_28p_arm_12t_hpc_c35 $lvt_umc_28p_arm_12t_hpc_c30]
}
if { [regexp {umc_28p_snps_ud} $TAR_LIB]  } {
  set target_library [concat $target_library $library_umc_28p_snps_ud]
  set lib_hvt_name [concat $lib_hvt_name $hvt_umc_28p_snps_30udh $hvt_umc_28p_snps_30udl $hvt_umc_28p_snps_30udp \
                                         $hvt_umc_28p_snps_35udh $hvt_umc_28p_snps_35udl $hvt_umc_28p_snps_35udp \
                                         $hvt_umc_28p_snps_40udh $hvt_umc_28p_snps_40udl $hvt_umc_28p_snps_40udp]
  set lib_svt_name [concat $lib_svt_name $svt_umc_28p_snps_30udh $svt_umc_28p_snps_30udl $svt_umc_28p_snps_30udp \
                                         $svt_umc_28p_snps_35udh $svt_umc_28p_snps_35udl $svt_umc_28p_snps_35udp \
                                         $svt_umc_28p_snps_40udh $svt_umc_28p_snps_40udl $svt_umc_28p_snps_40udp]
}
if {$synopsys_program_name != "pt_shell"} {
if { [regexp {tsmc_22ulp_tsmc_7t} $TAR_LIB]  } {
  set target_library [concat $target_library $library_tsmc_22ulp_tsmc_7t]
  set lib_hvt_name [concat $lib_hvt_name $hvt_tsmc_22ulp_tsmc_30_7t   $hvt_tsmc_22ulp_tsmc_30mb_7t $hvt_tsmc_22ulp_tsmc_30pm_7t \
                                         $hvt_tsmc_22ulp_tsmc_35_7t   $hvt_tsmc_22ulp_tsmc_35mb_7t $hvt_tsmc_22ulp_tsmc_35pm_7t \
                                         $hvt_tsmc_22ulp_tsmc_40_7t   $hvt_tsmc_22ulp_tsmc_40mb_7t $hvt_tsmc_22ulp_tsmc_40pm_7t]
  set lib_svt_name [concat $lib_svt_name $svt_tsmc_22ulp_tsmc_30_7t   $svt_tsmc_22ulp_tsmc_30mb_7t $svt_tsmc_22ulp_tsmc_30pm_7t \
                                         $svt_tsmc_22ulp_tsmc_35_7t   $svt_tsmc_22ulp_tsmc_35mb_7t $svt_tsmc_22ulp_tsmc_35pm_7t \
                                         $svt_tsmc_22ulp_tsmc_40_7t   $svt_tsmc_22ulp_tsmc_40mb_7t $svt_tsmc_22ulp_tsmc_40pm_7t]
} 
if { [regexp {tsmc_22ulp_tsmc_9t} $TAR_LIB]  } {
  set target_library [concat $target_library $library_tsmc_22ulp_tsmc_9t]
  set lib_hvt_name [concat $lib_hvt_name $hvt_tsmc_22ulp_tsmc_30_9t   $hvt_tsmc_22ulp_tsmc_30pm_9t $hvt_tsmc_22ulp_tsmc_35_9t \
                                         $hvt_tsmc_22ulp_tsmc_35pm_9t $hvt_tsmc_22ulp_tsmc_40_9t   $hvt_tsmc_22ulp_tsmc_40pm_9t]
  set lib_svt_name [concat $lib_svt_name $svt_tsmc_22ulp_tsmc_30_9t   $svt_tsmc_22ulp_tsmc_30pm_9t $svt_tsmc_22ulp_tsmc_35_9t \
                                         $svt_tsmc_22ulp_tsmc_35pm_9t $svt_tsmc_22ulp_tsmc_40_9t   $svt_tsmc_22ulp_tsmc_40pm_9t]
}
} else {
if { [regexp {tsmc_22ulp_tsmc} $TAR_LIB]  } {
  set target_library [concat $target_library $library_tsmc_22ulp_tsmc_7t $library_tsmc_22ulp_tsmc_9t]
  set lib_hvt_name [concat $lib_hvt_name $hvt_tsmc_22ulp_tsmc_30_7t   $hvt_tsmc_22ulp_tsmc_30mb_7t $hvt_tsmc_22ulp_tsmc_30pm_7t \
                                         $hvt_tsmc_22ulp_tsmc_35_7t   $hvt_tsmc_22ulp_tsmc_35mb_7t $hvt_tsmc_22ulp_tsmc_35pm_7t \
                                         $hvt_tsmc_22ulp_tsmc_40_7t   $hvt_tsmc_22ulp_tsmc_40mb_7t $hvt_tsmc_22ulp_tsmc_40pm_7t \
                                         $hvt_tsmc_22ulp_tsmc_30_9t   $hvt_tsmc_22ulp_tsmc_30pm_9t $hvt_tsmc_22ulp_tsmc_35_9t \
                                         $hvt_tsmc_22ulp_tsmc_35pm_9t $hvt_tsmc_22ulp_tsmc_40_9t   $hvt_tsmc_22ulp_tsmc_40pm_9t]
  set lib_svt_name [concat $lib_svt_name $svt_tsmc_22ulp_tsmc_30_7t   $svt_tsmc_22ulp_tsmc_30mb_7t $svt_tsmc_22ulp_tsmc_30pm_7t \
                                         $svt_tsmc_22ulp_tsmc_35_7t   $svt_tsmc_22ulp_tsmc_35mb_7t $svt_tsmc_22ulp_tsmc_35pm_7t \
                                         $svt_tsmc_22ulp_tsmc_40_7t   $svt_tsmc_22ulp_tsmc_40mb_7t $svt_tsmc_22ulp_tsmc_40pm_7t \
                                         $svt_tsmc_22ulp_tsmc_30_9t   $svt_tsmc_22ulp_tsmc_30pm_9t $svt_tsmc_22ulp_tsmc_35_9t \
                                         $svt_tsmc_22ulp_tsmc_35pm_9t $svt_tsmc_22ulp_tsmc_40_9t   $svt_tsmc_22ulp_tsmc_40pm_9t]
}
}

if { $MEM_FARA_EN==0 && $MEM_SNPS_EN==0 && $MEM_ARM_EN==0 } {
  set link_library [concat $link_library $ana_link_library]
} else {
  set link_library [concat $link_library $mem_link_library $ana_link_library]
}


