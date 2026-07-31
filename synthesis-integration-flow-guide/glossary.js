// Hover glossary for the synthesis flow guide
// Auto-wraps defined terms in #article with <span class="term" data-def="...">

(function () {
  'use strict';

  const glossary = {
    'design.set': '综合环境的总控配置文件，记录顶层名、工具选择、库文件、PVT corner、宏定义等关键参数，是 flow 各阶段读取的权威输入。',
    'RTL filelist': '列出所有参与综合的 RTL/SystemVerilog 源文件路径的文本清单，综合工具按此顺序读取并解析设计。',
    'filelist': '列出所有参与综合的 RTL/SystemVerilog 源文件路径的文本清单，综合工具按此顺序读取并解析设计。',
    'gensyn': '项目内部封装的环境初始化脚本，用于自动生成标准综合目录结构并完成版本管理 check in。',
    'CKF': 'Connectivity Check Flow 的缩写，用于检查 RTL 端口连接性、black box、Floating 信号等连接问题，是综合前的必要检查。',
    'nLint': 'RTL 语法、可综合性与代码风格检查工具，在综合前发现 latch、未初始化等问题。',
    'LEC': 'Logic Equivalence Check，形式验证方法，用于确认综合后的门级网表与 RTL 功能等价。',
    'UPF': 'Unified Power Format，描述芯片电源域划分、供电网络及低功耗控制意图的规范文件。',
    'Design Compiler': 'Synopsys 逻辑综合工具，将 RTL 描述映射为基于标准单元的门级网表。',
    'DC': 'Synopsys 逻辑综合工具，将 RTL 描述映射为基于标准单元的门级网表。',
    'Genus': 'Cadence 逻辑综合工具，功能与 DC 类似，部分 flow 用它生成综合网表或 final UPF。',
    'PrimeTime': 'Synopsys 静态时序分析工具，用于验证综合后或 APR 后门级网表的时序收敛。',
    'PT': 'Synopsys 静态时序分析工具，用于验证综合后或 APR 后门级网表的时序收敛。',
    'PVT corner': '工艺、电压、温度三种条件组合成的仿真角，用于覆盖芯片在不同工况下的时序与功耗。',
    'CORNER': '工艺、电压、温度三种条件组合成的仿真角，用于覆盖芯片在不同工况下的时序与功耗。',
    'SAIF': 'Switching Activity Interchange Format，记录电路节点翻转活动的文件，主要用于功耗分析。',
    'LVT': '低阈值标准单元，阈值越低速度越快但漏电越大。',
    'SVT': '标准阈值标准单元，在速度与功耗之间取得平衡。',
    'RVT': '常规阈值标准单元，在速度与功耗之间取得平衡。',
    'HVT': '高阈值标准单元，阈值越高速度越慢但漏电越小。',
    'analog db': '模拟 IP 宏单元的时序、功耗库文件，供综合与 STA 工具查表使用。',
    'memory db': 'SRAM 等 memory 宏单元的时序、功耗库文件，供综合与 STA 工具查表使用。',
    'DDC': 'Design Compiler 数据库格式，保存综合后的设计信息，可被后续工具读取与恢复。',
    'black box': '仅有端口声明而无内部实现的模块，综合工具无法看到其内部功能，常用于 IP 或待实现模块。',
    'Floating': '未连接任何驱动源或负载的信号或端口，通常反映 RTL 连接遗漏或接口声明错误。',
    'Latch': '电平敏感的存储单元，非预期引入可能带来时序不确定性和综合优化困难，应重点检查。',
    'netlist': '综合后得到的门级网表，由标准单元、宏单元及互连描述组成，是后端布局布线的输入。',
    'lec_upf': '检查手写 UPF 语法正确性与电源意图一致性的流程，通常在综合前执行。',
    'genus_upf': '借助 Genus 工具解析电源意图并生成最终 *_final.upf 的脚本流程。',
    'set_false_path': '告知时序工具不对指定路径做建立/保持检查，常用于异步跨时钟域路径。',
    'set_multicycle_path': '允许指定路径在多个时钟周期内完成数据传输的时序约束命令。',
    'set_dont_touch': '标记单元或网络禁止综合工具优化、合并或删除，常用于关键路径或 IP 边界。',
    'set_ideal_network': '将 clock、reset 等网络设为理想网络，阻止工具自动插入 buffer 或调整延迟。',
    'timing slack': '时序裕量，表示数据实际到达时间与要求到达时间之差，正值表示满足时序。',
    'slack': '时序裕量，表示数据实际到达时间与要求到达时间之差，正值表示满足时序。',
    'abort point': 'LEC 中工具因无法完成比较而放弃的对应点，需人工介入分析其等价性。',
    'non-equivalent point': 'LEC 判定 RTL 与网表在功能上不一致的比较点，必须逐一定位并修复。',
    'unmapped point': 'LEC 无法在参考设计与实现设计之间建立一一对应关系的比较点。',
    'ECO': 'Engineering Change Order，工程变更指令，通常指对网表或 RTL 进行的小规模工程修改。',
    'signoff': '综合、时序、形式验证等关键检查全部通过后的最终确认与交付流程。',
    'signoff fake': '部分检查项未完全通过时，经项目审批后执行的临时性或有条件签核。',
    'silver netlist': '项目流程中某一阶段释放的中间版本网表，通常接近最终版用于下游提前开展工作。',
    'Pre-PT': '基于综合后网表进行的预布局布线静态时序分析，用于评估综合阶段时序质量。',
    'Post-PT': '基于 APR 后端输出网表进行的 signoff 级静态时序分析，是最终时序验收环节。',
    'wc': '典型 PVT corner 之一，对应低压高温（LVHT）工况。',
    'wcl': '典型 PVT corner 之一，对应低压低温（LVLT）工况。',
    'lt': '典型 PVT corner 之一，对应高压低温（HVLT）工况。',
    'ml': '典型 PVT corner 之一，对应高压高温（HVHT）工况。',
    'tt': '典型 PVT corner 之一，对应典型温度、典型电压工况。',
    'memory compiler': '按工艺参数自动生成 SRAM 或 memory 宏单元的模型、版图及库文件的专用工具。',
    'mem_wrap': '对 memory 硬核进行接口封装的 RTL 层，统一端口命名、电源、测试等信号。',
    'memory wrapper': '对 memory 硬核进行接口封装的 RTL 层，统一端口命名、电源、测试等信号。',
    'PTPX': '基于 PrimeTime 的功耗分析工具，通常使用 VCD 或 SAIF 作为开关活动输入。',
    'VCD': 'Value Change Dump，记录仿真过程中信号值变化的通用波形文件格式。',
    'SDF': 'Standard Delay Format，包含门级网表延迟反标信息的时序文件，用于后端 signoff。',
    'SDC': 'Synopsys Design Constraints，时序约束文件，描述时钟、I/O 延迟、false path / multicycle 等约束；prePT 展开产物放 sdc_pr/ 供 APR 使用，postPT 读 APR 返回的 postcts SDC。',
    'FSDB': 'Fast Signal DataBase，Verdi 工具常用的高效压缩波形文件格式。',
    'toggle rate': '信号在单位时间内发生 0/1 翻转的平均次数，是评估动态功耗的重要指标。',
    'set_dont_touch_network': '将指定网络及其下游触发器整体设为不可优化对象，作用范围比 set_dont_touch 更广。',
    'asynchronous clocks': '频率或相位无固定关系的时钟，跨此类时钟域的路径通常设为 false path。',
    'STA': 'Static Timing Analysis，静态时序分析，不依赖仿真向量、对全部时序路径做穷举式检查的验证方法，数字签核以其结果为准。',
    'skew': '时钟或数据信号到达不同点的时间差；clock skew 由 clock tree balance 控制通常不大，data skew 相对 clock 衡量并需按规格收敛。',
    'clock skew': '时钟到达不同寄存器 clock 端的时间差；max 与 min 差很多通常说明 clock tree 做歪了。',
    'data skew': 'data 信号相对 clock 的偏移量，接口时序的关键收敛指标，通常要求落在以 clock 为中心的窗口内（如 ±3.5 ns）。',
    'uncertainty': '时钟不确定度，用 set_clock_uncertainty 施加的额外时序裕量，来源于历史经验值（如 setup 400 ps / hold 150 ps）。',
    'false path': '不需要做时序检查的路径，用 set_false_path 声明；判定错误会把真实路径漏报，必须逐条人工确认。',
    'multicycle': '允许路径跨多个时钟周期完成数据传输的约束，用 set_multicycle_path 声明，常用于慢速控制路径。',
    'corner': 'PVT 仿真角的简称；当前工艺共 10 个 corner，setup / hold / transition 需全量校验，不做取舍。',
    'signal integrity': '信号完整性分析（SI），评估串扰 noise 对 cell delay 的影响；保守做法是全程打开、不做取舍。',
    'OCV': 'On-Chip Variation，片内工艺偏差分析，通过额外 derate 覆盖同一芯片上不同位置的时序差异。',
    'quasi-static': '准静态信号，一帧才变一次或由寄存器配置出的控制信号，可设 false path 不做时序检查。',
    'dco': '集中书写 false path / multicycle 等约束的源文件，经 prePT 展开生成正式 SDC，禁止直接修改 SDC。',
    'live PT': '手工打开的交互式 PrimeTime session，用于临时报路径、验证约束效果，确认后再写回 dco。',
    'report_timing': 'PrimeTime 报时序路径的命令，常用 -input_pins 列出每级 pin；起点选错会夹带假路径。',
    'clock latency': 'clock 从源头到寄存器 clock 端的实际延迟；clock 间做过 balance 不应差很多，与 data 差得多是正常的。',
    'margin': '时序裕量，本流程有三种用法：① 综合加严量——下给 DC 的约束比频率目标再收紧的经验值（约 0.8 ns，曾试 0.6），"对自己紧一点、对后端松一点"（会议经验值，脚本中无对应设置）；② skew margin——skew 报表中 data 相对 clock 的裕量，由 merge_sd_busskew.pl 按 data_max−clk_min、data_min−clk_max 逐组计算，规格区间如 [-1:6]；③ setup/hold margin——接口时序推导中前后各预留的窗口（如 15 ns 周期前后各留 4 ns，中间 7 ns 即 skew ±3.5 ns 的来源）。',
    'min_pulse_width': '最小时钟脉冲宽度检查；PT 报的是 rise/fall latency 差而非真实占空比，占空比需靠后仿波形确认。',
    'spread spectrum': '展频，让 clock 频率在小范围内抖动以分散 EMI 峰值，约束需把展频比例计入周期定义。',
    'duty cycle': '占空比，clock 高电平时间占周期的比例；非 50% 时下降沿不在窗口中间，修 skew 需相应推 clock。',
    'PowerPro': 'Mentor（西门子 EDA）RTL 级功耗评估与优化工具，已集成到 IP 综合环境（gensyn 自动生成 powerpro 目录）；RTL level 用于 IP 设计阶段低功耗优化，gate level 用于后端 whole-chip 功耗对比。',
    'clock gating': '时钟门控：在时钟路径上插入门控单元（CGIC/ICG），enable 无效时关断时钟以消除冗余翻转功耗；PowerPro signoff 要求其冗余占比 < 5%。',
    'CGIC': 'Clock Gating Integrated Cell，集成时钟门控单元（也写作 ICG），根据 enable 条件关断/放行时钟。',
    'light sleep': 'memory 的轻休眠模式：空闲期关断部分内部电路以节省漏电；进入条件是空闲期可预估、且节省的 leakage 大于浪费的动态功耗。',
    'gray box': 'PowerPro 中设为不优化的模块（set_gray_box），其内部逻辑不参与功耗优化改写；环境默认 STD_IP 与 clk_cell。',
    'toggle': '信号翻转（0/1 跳变）；动态功耗的直接来源，冗余 toggle 是 PowerPro 各类冗余检查的主要消除对象。',
    'observability': '可观测性分析：判断信号翻转是否能传播到被消费的输出；翻转而不可观测（无人消费）的功耗即冗余功耗。'
  };

  // 命令悬浮窗：命令以 ⌨ 特殊标记，悬浮显示用法示例（内容出自 HV1V21_Synthesis_Integration_Flow.docx）
  const cmdGlossary = {
    'gensyn': '环境初始化命令。用法示例：gensyn <TOP_NAME>（默认自动 check in）；gensyn <TOP_NAME> -noadd（不 check in）；gensyn <TOP_NAME> -noadd <目录名>（自定义目录名）。模板有更新时再次执行 gensyn <TOP_NAME>，系统会自动 copy 新模板并备份原文件（filelist 与 constraint 一般不更新）。',
    'run_ckf': 'CKF 连接性检查入口，需在 run_dc 之前执行。用法：cd ckf && run_ckf；用 bsub 提交时必须带 batch 参数：bsub -Ip run_ckf 1。检查后看 ckf.log 与 ckf.rpt：Floating 必须清零，black box 逐一确认，Latch 只允许 gclk / io_latch 等统一引入的。',
    'run_nlint': 'nLint 检查入口，需在 run_dc 之前执行。用法：cd nlint && run_nlint，检查 nlint.log 与 nlint.rpt；确认无风险的 error 可粘贴进 nlint_waive.list，下次自动 mask。',
    'run_dc': 'DC 综合入口。用法：cd dc && run_dc（跑完留在交互 shell 调试）；run_dc 1（带任意参数 = batch 模式，跑完自动 exit，bsub 必须加参数）。检查 dc.log（Error / unresolved）、*.chk_design（undrive）与 *.rpt（area 合理、signoff 版本 slack > 0）。',
    'run_genus': 'Genus 综合入口。用法：cd genus && run_genus，检查 genus.log 与 *.rpt。运行 DC 时 genus 不需要跑；genus_upf 流程用于生成 *_final.upf。',
    'run_lec': 'LEC 形式验证入口。用法：cd lec && run_lec。通过标准：abort.rpt / non_eq.rpt / unmapped.rpt 均为 0（abort 经 analyze_abort 全部解决也算 PASS）。注意：没弹窗 ≠ 通过，可能只是没跑起来，必须看 log 确认真的 PASS。',
    'run_pt': 'PrimeTime 时序分析入口。用法：prePT 在 pt/ 下 run_pt；postPT 在 sta/post/pt/<corner>/ 下 run_pt。检查 pt.log 无 Error、*.rpt 中 timing slack > 0。',
    'run_ptpx': 'PTPX 功耗仿真入口。在 power/0.px_template/ 下改好 design.set 与 px_cfg.tcl 后执行 run_ptpx；结果看 rep_dir 下 *_toggle_rate_detail.rpt（翻转率）与 *_power.rpt（功耗），上层目录的 fsdb 可用 Verdi 打开看功耗波形。',
    'run_lc': 'Library Compiler 生成 db。用法：bsub -Ip run_lc（单独生成 db，可跳过，直接做 merge 也行）。',
    'do_merge_db': 'mem_db 流程：merge lib 和 db，生成 merged lib/db 放在 *_merged 文件夹下。',
    'do_merge_back': 'mem_db 流程：把 *_merged 文件夹下生成的 merged lib/db 复制回对应的 corner 文件夹下。',
    'gen_tcl.pl': 'mem_db 流程：修改 sram.list / corner.list 后执行 gen_tcl.pl，生成 cp_lib 与 gen_db_tcl。',
    'cp_lib': 'mem_db 流程：新建 cfg cir db ds dummy gds lef lib lvlib sim pglib 等目录后执行 cp_lib 拷库。',
    'source run.tcl': 'mem_wrap 生成：在 wrapper 目录执行 source run.tcl（注意是 source），生成 wrapper.v、fault_info_mux.v、hv_mem_bist_info.v，再把 .v 复制到 HDL/mem_wrap/ 下。',
    'fsdb2vcd': '从 fsdb 截取 vcd 波形。用法示例：fsdb2vcd chip_tb_top_000.fsdb -bt 500ps -et 700ps -o verilog.dump（-bt/-et 指定起止时间）。',
    '$dumpvars': 'Verilog 系统函数：把 testbench 里原来 dump fsdb 的函数换成 $dumpvars 即可直接 dump VCD 波形，供 PTPX 功耗仿真使用。',
    'analyze_abort': 'LEC 中分析 abort point 的命令；abort point 经 analyze_abort 全部解决后同样视为 PASS。',
    'run_power_opt': 'PowerPro 运行脚本。用法：source powerpro cshrc 后 cd powerpro && bsub -Ip run_power_opt；跑完用 python3 powerpro_script.py 汇总 report_info，再用 powerpro_chk.py 生成含指标占比的 report_info2。',
    'fsdbextract': '截取 fsdb 波形的某一段用于功耗评估。用法：fsdbextract xxx.fsdb -bt xxxxns -et xxxxns -o xxx_cut.fsdb（-bt 开始时间、-et 结束时间、-o 输出文件）。',
    'show_analyzer': 'PowerPro 图形化界面启动命令，run_power_opt 跑完后执行，用于查看 Efficiency / Dashboard 并对各项指标做 GUI 优化。'
  };

  const skipTags = new Set(['PRE', 'CODE', 'A', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'SCRIPT', 'STYLE', 'TERM-TOOLTIP']);
  const terms = Object.keys(glossary).sort((a, b) => b.length - a.length);
  const cmds = Object.keys(cmdGlossary).sort((a, b) => b.length - a.length);

  // 注入命令悬浮窗样式（.cmd）：与术语 .term 区分开，⌨ 图标 + 不同颜色，明示可悬浮
  const cmdStyle = document.createElement('style');
  cmdStyle.textContent = `
.cmd {
  position: relative;
  border-bottom: 1px dashed #2563eb;
  cursor: help;
  color: #2563eb;
  transition: background 0.15s ease, border-bottom-style 0.15s ease;
}
.cmd::before {
  content: '⌨ ';
  font-size: 0.85em;
}
.cmd:hover {
  background: rgba(37, 99, 235, 0.12);
  border-bottom-style: solid;
  border-radius: 4px;
}
@media (prefers-color-scheme: dark) {
  .cmd { color: #60a5fa; border-bottom-color: #60a5fa; }
  .cmd:hover { background: rgba(96, 165, 250, 0.15); }
}
.cmd-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 6px 18px;
  padding: 10px 16px;
  margin: 0 0 20px;
  background: var(--bg);
  border: 1px solid var(--line);
  border-radius: 10px;
  font-size: 13px;
  color: var(--muted);
}
.cmd-legend .lg { display: inline-flex; align-items: center; gap: 5px; }
.cmd-legend .swatch-term { color: var(--accent); border-bottom: 1px dashed var(--accent); }
.cmd-legend .swatch-cmd { color: #2563eb; border-bottom: 1px dashed #2563eb; }

/* 重点高亮块 callout：md 中以 WARNING:/NOTE:/TIP:/ASSUMPTION:/KEY: 开头的段落自动渲染 */
.callout {
  border-left: 4px solid;
  border-radius: 0 10px 10px 0;
  padding: 12px 18px;
  margin: 18px 0;
  font-size: 15px;
  line-height: 1.7;
}
.callout .callout-tag {
  display: inline-block;
  font-size: 12px;
  font-weight: 700;
  padding: 1px 10px;
  border-radius: 999px;
  margin-right: 8px;
  color: #fff;
  vertical-align: 1px;
}
.callout-warn  { border-color: #dc2626; background: rgba(220, 38, 38, 0.07); }
.callout-warn  .callout-tag { background: #dc2626; }
.callout-note  { border-color: #2563eb; background: rgba(37, 99, 235, 0.07); }
.callout-note  .callout-tag { background: #2563eb; }
.callout-tip   { border-color: #16a34a; background: rgba(22, 163, 74, 0.08); }
.callout-tip   .callout-tag { background: #16a34a; }
.callout-assume { border-color: #9333ea; background: rgba(147, 51, 234, 0.07); }
.callout-assume .callout-tag { background: #9333ea; }
.callout-key {
  border-color: var(--accent);
  background: var(--accent-soft);
  box-shadow: 0 4px 18px rgba(13, 148, 136, 0.15);
  font-weight: 500;
}
.callout-key .callout-tag { background: var(--accent); }
.callout-head { padding: 7px 14px; }
`;
  document.head.appendChild(cmdStyle);

  // 词边界匹配：术语前后不能紧跟 [A-Za-z0-9_]（中文字符不算阻挡，紧贴中文仍匹配）
  function escapeRegExp(s) {
    return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }
  const termRegexes = terms.map(term => ({
    term,
    re: new RegExp('(?<![A-Za-z0-9_])' + escapeRegExp(term) + '(?![A-Za-z0-9_])', 'g')
  }));
  const cmdRegexes = cmds.map(cmd => ({
    term: cmd,
    re: new RegExp('(?<![A-Za-z0-9_])' + escapeRegExp(cmd) + '(?![A-Za-z0-9_])', 'g')
  }));

  function wrapTerms(root, regexes, dict, cls) {
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
      acceptNode(node) {
        let el = node.parentElement;
        while (el && el !== root) {
          if (skipTags.has(el.tagName) || el.classList.contains('term') || el.classList.contains('cmd')) {
            return NodeFilter.FILTER_REJECT;
          }
          el = el.parentElement;
        }
        return node.nodeValue.trim() ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_SKIP;
      }
    });

    const nodesToReplace = [];
    while (walker.nextNode()) {
      nodesToReplace.push(walker.currentNode);
    }

    nodesToReplace.forEach(textNode => {
      const text = textNode.nodeValue;
      let hasMatch = false;
      for (const { re } of regexes) {
        re.lastIndex = 0;
        if (re.test(text)) {
          hasMatch = true;
          break;
        }
      }
      if (!hasMatch) return;

      const frag = document.createDocumentFragment();
      let lastIndex = 0;
      while (lastIndex < text.length) {
        let earliestTerm = null;
        let earliestIndex = Infinity;
        for (const { term, re } of regexes) {
          re.lastIndex = lastIndex;
          const m = re.exec(text);
          if (m && m.index < earliestIndex) {
            earliestIndex = m.index;
            earliestTerm = term;
          }
        }
        if (!earliestTerm) {
          frag.appendChild(document.createTextNode(text.slice(lastIndex)));
          break;
        }
        if (earliestIndex > lastIndex) {
          frag.appendChild(document.createTextNode(text.slice(lastIndex, earliestIndex)));
        }
        const span = document.createElement('span');
        span.className = cls;
        span.dataset.def = dict[earliestTerm];
        span.textContent = earliestTerm;
        frag.appendChild(span);
        lastIndex = earliestIndex + earliestTerm.length;
      }
      textNode.parentNode.replaceChild(frag, textNode);
    });
  }

  function applyGlossary(root) {
    if (!root) return;
    wrapTerms(root, termRegexes, glossary, 'term');
  }

  // 命令悬浮窗：行内 <code> 精确匹配 + 正文文本匹配，统一加 .cmd 标记（⌨ 图标由 CSS ::before 提供）
  function applyCmdGlossary(root) {
    if (!root) return;
    root.querySelectorAll('code').forEach(code => {
      if (code.closest('pre')) return;
      const text = code.textContent.trim();
      if (cmdGlossary[text]) {
        code.classList.add('cmd');
        code.dataset.def = cmdGlossary[text];
      }
    });
    wrapTerms(root, cmdRegexes, cmdGlossary, 'cmd');
    // 页面顶部放一次图例，明示 ⌨ 标记可悬浮
    if (root.querySelector('.cmd') && !root.querySelector('.cmd-legend')) {
      const legend = document.createElement('div');
      legend.className = 'cmd-legend';
      legend.innerHTML =
        '<span class="lg"><span class="swatch-term">术语</span>：悬浮查看名词解释</span>' +
        '<span class="lg"><span class="swatch-cmd">⌨ 命令</span>：悬浮查看用法示例与注意事项</span>';
      root.insertBefore(legend, root.firstChild);
    }
  }

  // 高亮块转换：把以 WARNING:/NOTE:/TIP:/ASSUMPTION:/KEY: 开头的 <p> 渲染为彩色 callout
  const calloutMap = {
    'WARNING':    { cls: 'warn',   label: '警告' },
    'NOTE':       { cls: 'note',   label: '注意' },
    'TIP':        { cls: 'tip',    label: '贴士' },
    'ASSUMPTION': { cls: 'assume', label: '假设' },
    'KEY':        { cls: 'key',    label: '⭐ 重点' }
  };

  function applyCallouts(root) {
    if (!root) return;
    root.querySelectorAll('p').forEach(p => {
      const m = p.textContent.trim().match(/^(WARNING|NOTE|TIP|ASSUMPTION|KEY)\s*[:：]\s*/);
      if (!m) return;
      const conf = calloutMap[m[1]];
      // 从首个文本节点中剥掉标记前缀
      const first = p.firstChild;
      if (first && first.nodeType === 3) {
        first.nodeValue = first.nodeValue.replace(/^\s*(WARNING|NOTE|TIP|ASSUMPTION|KEY)\s*[:：]\s*/, '');
      }
      const div = document.createElement('div');
      const empty = !p.textContent.trim();
      div.className = 'callout callout-' + conf.cls + (empty ? ' callout-head' : '');
      const tag = document.createElement('span');
      tag.className = 'callout-tag';
      tag.textContent = conf.label;
      div.appendChild(tag);
      while (p.firstChild) div.appendChild(p.firstChild);
      p.replaceWith(div);
    });
  }

  let activeTooltip = null;

  function showTooltip(term) {
    hideTooltip();
    const tooltip = document.createElement('div');
    tooltip.className = 'term-tooltip';
    tooltip.textContent = term.dataset.def;
    document.body.appendChild(tooltip);

    const rect = term.getBoundingClientRect();
    const margin = 12;
    const tooltipRect = tooltip.getBoundingClientRect();

    let top = rect.top - tooltipRect.height - margin;
    let arrowClass = 'arrow-bottom';
    if (top < margin) {
      top = rect.bottom + margin;
      arrowClass = 'arrow-top';
    }

    let left = rect.left + rect.width / 2 - tooltipRect.width / 2;
    left = Math.max(margin, Math.min(window.innerWidth - tooltipRect.width - margin, left));

    tooltip.style.top = top + 'px';
    tooltip.style.left = left + 'px';
    tooltip.classList.add(arrowClass);

    requestAnimationFrame(() => tooltip.classList.add('visible'));
    activeTooltip = tooltip;
  }

  function hideTooltip() {
    if (activeTooltip) {
      activeTooltip.remove();
      activeTooltip = null;
    }
  }

  document.addEventListener('mouseover', e => {
    const term = e.target.closest('.term, .cmd');
    if (term) showTooltip(term);
  });

  document.addEventListener('mouseout', e => {
    const term = e.target.closest('.term, .cmd');
    if (term) hideTooltip();
  });

  window.applyGlossary = applyGlossary;
  window.applyCmdGlossary = applyCmdGlossary;
  window.applyCallouts = applyCallouts;

  document.addEventListener('DOMContentLoaded', () => {
    const article = document.getElementById('article');
    if (article && article.children.length > 0) {
      applyGlossary(article);
      applyCmdGlossary(article);
      applyCallouts(article);
    }
  });
})();
