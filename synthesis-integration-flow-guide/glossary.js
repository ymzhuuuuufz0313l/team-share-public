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
    'FSDB': 'Fast Signal DataBase，Verdi 工具常用的高效压缩波形文件格式。',
    'toggle rate': '信号在单位时间内发生 0/1 翻转的平均次数，是评估动态功耗的重要指标。',
    'set_dont_touch_network': '将指定网络及其下游触发器整体设为不可优化对象，作用范围比 set_dont_touch 更广。',
    'asynchronous clocks': '频率或相位无固定关系的时钟，跨此类时钟域的路径通常设为 false path。'
  };

  const skipTags = new Set(['PRE', 'CODE', 'A', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'SCRIPT', 'STYLE', 'TERM-TOOLTIP']);
  const terms = Object.keys(glossary).sort((a, b) => b.length - a.length);

  function applyGlossary(root) {
    if (!root) return;
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
      acceptNode(node) {
        let el = node.parentElement;
        while (el && el !== root) {
          if (skipTags.has(el.tagName) || el.classList.contains('term')) {
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
      for (const term of terms) {
        if (text.includes(term)) {
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
        for (const term of terms) {
          const idx = text.indexOf(term, lastIndex);
          if (idx !== -1 && idx < earliestIndex) {
            earliestIndex = idx;
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
        span.className = 'term';
        span.dataset.def = glossary[earliestTerm];
        span.textContent = earliestTerm;
        frag.appendChild(span);
        lastIndex = earliestIndex + earliestTerm.length;
      }
      textNode.parentNode.replaceChild(frag, textNode);
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
    const term = e.target.closest('.term');
    if (term) showTooltip(term);
  });

  document.addEventListener('mouseout', e => {
    const term = e.target.closest('.term');
    if (term) hideTooltip();
  });

  window.applyGlossary = applyGlossary;

  document.addEventListener('DOMContentLoaded', () => {
    const article = document.getElementById('article');
    if (article && article.children.length > 0) {
      applyGlossary(article);
    }
  });
})();
