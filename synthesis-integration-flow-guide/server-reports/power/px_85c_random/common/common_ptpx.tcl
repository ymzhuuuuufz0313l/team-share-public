set svr_keep_unconnected_nets                       true
set timing_report_unconstrained_paths               true
set sh_enable_page_mode                             false
#for pre layout only
set link_create_black_boxes                         true
set sh_continue_on_error                            false
set sh_source_uses_search_path                      true
set timing_disable_internal_inout_net_arcs          true
set timing_disable_clock_gating_checks              false
set timing_remove_clock_reconvergence_pessimism     true
set timing_report_always_use_valid_start_end_points false
set report_default_significant_digits               6
set timing_reduce_multi_drive_net_arcs              true
set timing_crpr_threshold_ps                        10
set case_analysis_log_file                          rep_dir/case_analysis.log
set timing_clock_source_driver_pin_use_dirrver_arc_compatibility false
set CONS_CHECK 1
source /project/HK3671/designer/DD/ppchen/HK3671/SYNTHESIS/common/tcl_dir/common/common_db.tcl -verbose -echo
set link_path [concat "*" $link_library]

## read_verilog
set verilog_file_num [llength $verilog_file]
echo "" > rep_dir/read_verilog.log
foreach vfile $verilog_file {
  echo "read_verilog ${vfile}"
  read_verilog $vfile  >> rep_dir/read_verilog.log
}



current_design $TOP_NAME
link_design $TOP_NAME > rep_dir/link_design.log

#source $TCL_DIR/design_rule.tcl -verbose -echo


#set auto_wire_load_selection false
##set_wire_load_mode enclosed
#set_wire_load_mode top
#set_wire_load_model -name G0K -library $lib_hvt_name
#set_operating_conditions WCCOM -library $lib_hvt_name
echo "" > ./rep_dir/sdc.log
foreach sfile $sdc_file {
  puts "source ${sfile}"
  source $sfile -verbose -echo >> ./rep_dir/sdc.log
}

#update_timing > ./rep_dir/update_timing.log

set CONS_REPORT     ./rep_dir/${TOP_NAME}_cons.rpt
set COVERAGE_REPORT ./rep_dir/${TOP_NAME}_coverage.rpt
set TIMING_REPORT   ./rep_dir/${TOP_NAME}_timing.rpt

source ${TCL_DIR}dc/dc_user_proc.tcl
##source $TCL_DIR/pt_report.tcl  -echo
#
##sh grep -v "/CDN" ./rep_dir/check_timing.log > a 
##sh grep -v "/SDN" a  > b 
##sh grep -v "/latch/E" b > ./rep_dir/uncons.rpt
#
#
#report_timing > ./rep_dir/report_timing.log
#
#write_sdc -nosplit ./rep_dir/${TOP_NAME}.sdc
#
#alias rpt report_timing -nosplit -derate -net -cap -trans -path_type full_clock_ex
#alias h   his
#
###report dff
#kv_report_dff_num rep_dir/report_dff_num.rpt
#
#
###ck floating
#if {$CK_FLT_EN == 1} {
#    source $TCL_DIR/pt_check_design.tcl
#    PT_check_design -type input_float
#    PT_check_design -type output_short
#}

