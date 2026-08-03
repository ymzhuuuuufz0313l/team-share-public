

set pr_dir "/project/HV2M23/DataBase/APR/${TOP_NAME}/latest/" 

    #set CORNER "wc_cmax_125_setup"  
    #set CORNER "wc_rcmax_125_setup" 
    #set CORNER "wc_cmax_125_hold"   
    #set CORNER "wc_rcmax_125_hold"  
    
    #set CORNER "wcz_cmax_0_hold"    
    #set CORNER "wcz_rcmax_0_hold"   
    #set CORNER "wcz_cmax_0_setup"   
    #set CORNER "wcz_rcmax_0_setup" 

    #set CORNER "wcl_cmax_m40_setup" 
    #set CORNER "wcl_rcmax_m40_setup"
    #set CORNER "wcl_cmax_m40_hold"  
    #set CORNER "wcl_rcmax_m40_hold" 
    
    #set CORNER "lt_cmax_m40_hold"   
    #set CORNER "lt_rcmax_m40_hold"  
    #set CORNER "lt_cmin_m40_hold"   
    #set CORNER "lt_rcmin_m40_hold"  
    #set CORNER "bc_cmax_0_hold"     
    #set CORNER "bc_rcmax_0_hold"    
    #set CORNER "bc_cmin_0_hold"     
    #set CORNER "bc_rcmin_0_hold"    
    #set CORNER "ml_cmax_125_hold"   
    #set CORNER "ml_rcmax_125_hold"  
    #set CORNER "ml_cmin_125_hold"   
    #set CORNER "ml_rcmin_125_hold"

   set CORNER "tt_typ" 

#set verilog_file "/project/HK4U31/DataBase/Digital/Release/Netlist/APR/latest/HK4U31.v.gz"
set verilog_file "/project/HV2M23/designer/AD/yzhao/release/HV2M23_digital_top/timing/latest/HV2M23_digital_top.v.gz"
set sdc_file     [list "/project/HV2M23/DataBase/Digital/Release/HV2M23_digital_top_to_APR/latest/HV2M23_digital_top_postcts.sdc"]
#set upf_file     [list "/project/HK6888/designer/DD/ttao/HK6888/Release/Netlist/Prescan/HK6888_PLANB_to_APR/latest/HK6888_final.upf"]
set spef_dir     "/project/HV2M23/designer/AD/yzhao/release/HV2M23_digital_top/timing/latest/"

set saif_file    ""
# vcd|saif
set use_vcd_saif "vcd"

#set  power_mode "averaged" 
set  power_mode "time_based" 


set ip0_inst       "HV2M23_digital_top"
set ip0_strip      "chip_tb_top/u_HV2M23/u_HV2M23_digital_top"
#set ip0_vcd        "/simulation/yfzhong/HK6888/TOP_NETLIST_PLANB/t_4400_2250_120_8b8p2l_full_480/verilog.dump"
#set ip0_vcd        "/simulation/ttao/HK3M31/TOP_NETLIST_POST/t_2560_1440_90_8b4p2l_1920chmod_1shl_0dotc_full_L/verilog1.dump" 
set ip0_vcd        "/sim_dd/ymzhu/HV2M23/TOP_NETLIST_POST_TCON_C/four_line_fre1p8_2lane_tt_0729v0.dump" 
#set ip0_vcd        "/simulation/ttao/HK3M31/TOP_NETLIST_POST/t_2560_1440_165_8b4p4l_1920chmod_1shl_0dotc_full_R/one_line.dump" 
# inst strip_path vcd
set vcd_file "\
            $ip0_inst $ip0_strip $ip0_vcd \
              "

#set vcd_stribe_path   "HV8107_testbench/HV8107/u_sub1_cap"
