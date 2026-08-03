
source ./design.set -verbose -echo
source ./px_cfg.tcl

if {[file exist "rep_dir"] == 0} { [sh mkdir rep_dir]}

set CK_FLT_EN 0
set CK_TIM_EN 1
set CK_PWR_EN 1

set power_enable_analysis TRUE
set power_analysis_mode $power_mode
#set_power_analysis_options -waveform_interval 1.666 
#below is default
#set power_analysis_mode averaged

#source $TCL_DIR/common_pt.tcl -verbose -echo
source ./common/common_ptpx.tcl -verbose -echo

# Power Px
#set power_enable_analysis TRUE
#set power_analysis_mode time_based
set si_enable_analysis true
set power_limit_extrapolation_range false 
set power_use_ccsp_pin_capacitance false 
read_parasitics -keep_capacitive_coupling -complete_with zero -verbose /project/HV1V22/designer/AD/yzhao/release/HV1V22_digital_top/timing/latest/HV1V22_digital_top_typical_25c.spef.gz > ./rep_dir/read_parasitics_verbose.log
report_annotated_parasitics -check > ./rep_dir/report_annotated_parasitics.log
#set_operating_conditions tt0p9v85c -analysis_type on_chip_variation
set_operating_conditions  -analysis_type on_chip_variation

set_propagated_clock [all_clocks]
#update_timing

set i 0
#read_vcd "$vcd_file" -strip_path "bench_hv8107_top/u_hv8107_chp/u_cpu_sys"
if {$use_vcd_saif == "vcd"} {
     
     foreach {inst strip vcd} $vcd_file {
       incr i
       if {$inst == $TOP_NAME} {
         read_vcd "$vcd"  -strip_path "$strip"
         echo "read_vcd $i inst:$inst strip:$strip vcd:$vcd"
       } else {
         read_vcd "$vcd" -path $inst  -strip_path "$strip"
         echo "read_vcd $i inst:$inst strip:$strip vcd:$vcd"
       }
    }
}
if {$use_vcd_saif == "saif"} {
     read_saif "$saif_file" -strip_path "$vcd_stribe_path"
     echo "use $use_vcd_saif"
     echo "saif_file is $saif_file"
}

if {$USE_UPF =="1"} {
source -e -v ${upf_file} > load_upf.txt
create_power_switch vdd1p2d_sw \
                              -domain PD_AON \
                              -output_supply_port {NSLEEPOUT DVDD} \
                              -input_supply_port {NSLEEPIN VDD1P2AON} \
                              -on_state {state1 NSLEEPIN {!CNTL}} \
                              -control_port { CNTL u_cgu_rgu_sd/u_sd_analog/pmu_ldo1p2d_pd } \
							  -off_state {OFF {CNTL} }
create_power_switch vdd1p2a_sw \
                              -domain PD_AON \
                              -output_supply_port {NSLEEPOUT VDD12_ANA} \
                              -input_supply_port {NSLEEPIN VDD1P2AON} \
                              -on_state {state1 NSLEEPIN {!CNTL}} \
                              -control_port { CNTL u_cgu_rgu_sd/u_sd_analog/pmu_ldo1p2a_pd } \
							  -off_state {OFF {CNTL} }
create_power_switch vdd2pd_sw \
                              -domain PD_AON \
                              -output_supply_port {NSLEEPOUT VDD25} \
                              -input_supply_port {NSLEEPIN VDD1P2AON} \
                              -on_state {state1 NSLEEPIN {!CNTL}} \
                              -control_port { CNTL u_cgu_rgu_sd/u_sd_analog/pmu_ldo2p5d_pd } \
							  -off_state {OFF {CNTL} }



set_voltage 5.0 -object_list VSSH_ANAL 
set_voltage 5.0 -object_list VDDH_ANAB 
set_voltage 0.0 -object_list DVSS 
set_voltage 0.0 -object_list VSSH_ANAB 
set_voltage 0.0 -object_list AVSS_ADC 
set_voltage 5.0 -object_list VDDH_ANAL 
set_voltage 5.0 -object_list AVDDH_ADC 
set_voltage 5.0 -object_list VDDIO 
set_voltage 1.2 -object_list DVDD 
set_voltage 1.2 -object_list VDD1P2AON 
set_voltage 1.2 -object_list VDD12_ANA 
set_voltage 2.5 -object_list VDD25 
}



update_timing > update_timing.log
#set power_scale_dynamic_power_at_power_off true
##below power analysis begin
#set power_enable_analysis TRUE
#set power_analysis_mode time_based
#below is default
#set power_analysis_mode averaged

set power_enable_multi_rail_analysis true 
#set_power_analysis_options -waveform_format fsdb -waveform_output ${TOP_NAME}  -waveform_interval 1.666  
 #read_vcd -rtl "./fsdb/wva_clkg_memg_deqf_20190110.fsdb" -strip_path "tb/u_kv_wva_top" -time {2597272 2787180}

#report_switching_activity -list_not_annotated -include_only sequential > wva_switch.rpt
#report_switching_activity -coverage -hierarchy >> wva_switch.rpt

#####################################################################
##       check/update/report power 
######################################################################
set pt_rpt "rep_dir"
check_power -verbose  > ./${pt_rpt}/check_power.log
update_power > ./${pt_rpt}/update_power.log
report_power -leaf -hierarch -verbose > ./${pt_rpt}/${TOP_NAME}_power.rpt
report_switching_activity -average_activity -hierarchy > ./${pt_rpt}/${TOP_NAME}_toggle_rate.rpt
report_switching_activity -hierarchy > ./${pt_rpt}/${TOP_NAME}_toggle_rate_detail.rpt
#set_power_analysis_options -waveform_format fsdb -waveform_output ./${pt_rpt}/${TOP_NAME}

if {$USE_UPF == "1"} {
  set all_power_ports "VDD1P2AON DVDD VDD12_ANA VDD25 VDDIO VDDH_ANAB VDDH_ANAL AVDDH_ADC"
  foreach power_port $all_power_ports {
  set_current_power_net $power_port
  #update_power
  report_power -hier -leaf -verbose > ./${pt_rpt}/${power_port}_power.rpt
  }
}
return


alias rpt report_timing
alias h   his

kv_report_dff_num > pt_rpt/report_dff_num.rpt
#}



#quit



