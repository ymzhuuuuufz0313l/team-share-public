
    const markdown = `# HK1V11 420b 长编码验证体系

> 来源：\\\`E:\\project\\HK1V11\\longcode_ver\\\`  
> 整理时间：2026-07-13

---

## 一、整体架构

420b 长编码验证环境基于 \\`DV_TCON_C\\` 现有 8B/10B 结构重建，通过 \\`CHPI_MODE_420B\\` 宏与普通模式隔离。

![longcode 验证架构](./longcode_verification_architecture.png)

### 环境核心组件

| 组件 | 文件 | 作用 |
|------|------|------|
| Reference Model | \\`long_encoding_ref_model.sv\\` | 413b→420b 编码 / 420b→413b 解码 / G16(X) 加扰解扰 |
| Sequence | \\`isptx_sequence.sv\\` | 构建 LSP / CTRL_F / CTRL_L / Active / V blanking 帧 |
| Driver | \\`isptx_driver.sv\\` | 20-bit packet / 40-bit K-code 发送，MSB-first |
| Transaction | \\`isptx_transaction.sv\\` | 20-bit packet / 40-bit K-code 数据结构 |
| Checker | \\`checker_420b.sv\\` | 20-bit 数据流检查、编码规则检查、跨 lane 长度检查 |

---

## 二、8B/10B vs 420B 对比

![8B/10B vs 420B 架构对比](./8b10b_vs_420b_architecture.png)

| 项目 | 8B/10B | 420B |
|------|--------|------|
| 模式开关 | 无 | \\`define CHPI_MODE_420B\\` |
| 输入粒度 | 8-bit byte | 7-bit group |
| 编码 | 8B/10B table | 413b → 420b tag 替换 |
| K-code 宽度 | 10-bit | 40-bit |
| IDLE | 无独立 IDLE | 10-bit K5~K8 |
| LFSR | 24-bit G24(X) | 16-bit G16(X) |
| LFSR 复位点 | 训练/K-code 边界 | K3 上升沿 |
| 发送方向 | LSB-first | MSB-first |
| 跨 lane 对齐 | 字节对齐 | 70-bit dummy 对齐 |
| DUT 解码 | 8B/10B decode | \\`long_decoding_top\\` / \\`decoder_7b\\` / \\`descramble_7b\\` |
| 输出 | 8-bit data | 24-bit + 2-bit valid |

---

## 三、420b 帧结构

\\`\\`\\`text
Frame:
├─ Config Line (K4 + CTRL_F + IDLE)
├─ V blanking Lines (K1 + CTRL_L + VBK + K2 + IDLE) × N
├─ Active Lines (K1 + CTRL_L + Video + K2 + IDLE) × (VACT - 1)
└─ Last Active Line (K1 + CTRL_L + Video + K4 + CTRL_F)  ← 末尾嵌入帧尾
\\`\\`\\`

### 关键字段

| 字段 | 内容 | 说明 |
|------|------|------|
| LSP | K2 + 0xEA/EB/EC/ED×8 + dummy + K3 | 训练数据，**不加扰** |
| CTRL_F | Config Line 配置数据 | payload，**加扰** |
| CTRL_L | Line 控制数据 | payload，**加扰** |
| Active | RGB 像素数据 | payload，**加扰** |
| VBK | V blanking 数据 | payload，**加扰** |
| IDLE | K5/K6/K7/K8 pattern | **不加扰** |

---

## 四、验证执行阶段

\\`\\`\\`text
Phase 1: Smoke
  └─ 基础 420b 发送、MSB-first、全 0/全 1、tag bypass、scramble on/off

Phase 2: Frame Structure
  └─ LSP、CTRL_F、CTRL_L、Active、last-active、V blanking、IDLE、multiframe

Phase 3: Decode / Descramble / Unlock
  └─ 解码窗口、K3 同步、UTC unlock、link 恢复

Phase 4: Error / Corner
  └─ 7b_01、K-code 错误、UTC header、long frame、checksum、vbk、chpi_regw 等

Phase 5: Multi-lane / Alignment
  └─ 2lane/4lane、70-bit 对齐、R_BAC/AEQ/debugpin/packpos/RGB 功能复跑

Phase 6: Resolution / Refresh / Port Sweep
  └─ 4K/1080p/1440p/2.5K/2.8K/3.4K × 多刷新率 × 多 port_num/CH_SEL

Phase 7: Isolation / Regression
  └─ 420b vs 8B/10B 对比，8B/10B 回归防退化
\\`\\`\\`

---

## 五、Case 命名规则

沿用 8B/10B 风格，统一加 \\`_420b\\` 后缀：

\\`\\`\\`text
t_8b{lane_num}lane_420b_{function}[_{param}]
t_H{HACT}_V{VACT}_FPS{FPS}_PORT_NUM{PORT_NUM}_420b[_{extra_param}]
\\`\\`\\`

### Case 数量分布

| 类别 | 数量 | 说明 |
|------|------|------|
| Smoke | 7 | basic / scramble_off/on / msb_first / all_zero / all_one / tag_bypass |
| Frame Structure | 8 | lsp / ctrl_f / ctrl_l / active / active_last / vblank / idle / multiframe |
| Decode / Unlock | 10 | 解码窗口、K3 同步、UTC/unlock 系列 |
| Error / Corner | 9 | 7b_01、kcode、UTC header、long frame、checksum、vbk、chpi_regw 等 |
| Multi-lane | 9 | 2lane/4lane、70-bit 对齐、R_BAC/AEQ/debugpin/packpos/RGB |
| Resolution Sweep | 8 | 4K/1080p/1440p 等 × 多刷新率/端口 |
| Isolation | 2 | 420b vs 8B/10B、8B/10B regression |
| **合计** | **53** | 按 Phase 1~7 分阶段执行 |

---

## 六、420b 解码链 RTL

\\`\\`\\`text
20-bit 对齐输入流
        │
        ▼
┌───────────────────┐
│   decoder_7b      │  420b → 413b 解码
│                   │  提取 tag、还原全 0/全 1、重组数据
│                   │  输出 7/14/21-bit 有效数据
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  descramble_7b    │  7-bit LFSR G16(X) 解扰
│                   │  K3 上升沿复位
│                   │  scramble_en=0 时旁路
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ long_decoding_top │  42-bit 缓存
│                   │  按 8/16/24-bit 切分打包输出
└───────────────────┘
\\`\\`\\`

### 关键信号

| 信号 | 说明 |
|------|------|
| \\`decode_en\\` | 解码窗口使能；K1/K4 开，K2/K3 关 |
| \\`tag_value\\` | 6-bit 标签，用于全 0/全 1 替换 |
| \\`dout_21b_valid\\` | 有效位宽：01=7bit / 10=14bit / 11=21bit |
| \\`scramble_en_k3\\` | K3 锁存的解扰使能 |
| \\`dout_24b\\` / \\`dout_valid\\` | 最终 24-bit 输出及有效指示 |

---

## 七、编码规则要点

1. **413b → 420b 编码**
   - 413 bit 分成 59 组，每组 7 bit
   - 找一个未出现的 6-bit 样式作为 tag
   - 全 0 / 全 1 组替换为 \\`tag + 1-bit 类型指示符\\`

2. **加扰规则**
   - payload（CTRL_F / CTRL_L / RGB / VBK）**加扰**
   - LSP 训练数据**不加扰**
   - IDLE K5~K8 **不加扰**

3. **发送顺序**
   - 420b 模式：**MSB-first**（bit6 → bit0）
   - 普通 8B/10B 模式：LSB-first

4. **跨 lane 70-bit 对齐**
   - 各 lane 编码后长度一致
   - 统一按最大 lane 的 dummy 长度填充
   - 保证 K-code 插入点在各 lane 对齐

---

## 八、关键待确认问题

| 问题 | 优先级 |
|------|--------|
| \\`long_encoding_ref_model\\` encode/decode 位序一致性 | 高 |
| \\`isptx_driver\\` 420b 发送方向与 MSB-first 对齐 | 高 |
| \\`checker_420b\\` 20-bit chunk 组装方向与 driver 对齐 | 高 |
| CTRL_F checksum 是否需要发送 | 中 |
| LSP 重复次数是否满足 ≥1us | 中 |
| IDLE 长度精确换算（htotal-hact） | 中 |
| UTC 错误检测责任模块确认 | 中 |
| 跨 lane raw 长度是否需 70 整数倍 | 低 |
| V blanking 行数是否含 setting_line | 低 |

---

## 九、后续工作

- [ ] 修复 reference model 与 driver 的 MSB-first / 从左到右实现
- [ ] 将 \\`t_8b1lane_420b_basic\\` 同步到 \\`DV_TCON_C/top/tests/\\`
- [ ] 按 Phase 1~7 逐步扩展 420b case
- [ ] 在 420b case 中关闭 C model 相关 checker
- [ ] 确认 CTRL_F checksum、LSP 时长、UTC 责任模块等 Spec 差异点
- [ ] 普通 8B/10B 模式回归，确保未引入副作用
`;

    document.getElementById('article').innerHTML = marked.parse(markdown);

    // Custom image lightbox with wheel zoom and drag pan
    const lightbox = document.getElementById('lightbox');
    const lightboxImg = document.getElementById('lightbox-img');
    const lightboxClose = document.getElementById('lightbox-close');

    let scale = 1;
    let translateX = 0;
    let translateY = 0;
    let isDragging = false;
    let startX = 0;
    let startY = 0;
    let initialTranslateX = 0;
    let initialTranslateY = 0;

    function updateTransform() {
      lightboxImg.style.transform = `translate(${translateX}px, ${translateY}px) scale(${scale})`;
    }

    function resetTransform() {
      scale = 1;
      translateX = 0;
      translateY = 0;
      updateTransform();
    }

    function openLightbox(src) {
      lightboxImg.src = src;
      resetTransform();
      lightbox.classList.add('active');
      document.body.style.overflow = 'hidden';
    }

    function closeLightbox() {
      lightbox.classList.remove('active');
      document.body.style.overflow = '';
      setTimeout(() => { lightboxImg.src = ''; }, 250);
    }

    document.querySelectorAll('.article img').forEach(img => {
      img.addEventListener('click', () => openLightbox(img.src));
    });

    lightboxClose.addEventListener('click', (e) => {
      e.stopPropagation();
      closeLightbox();
    });

    lightbox.addEventListener('click', (e) => {
      if (e.target === lightbox) closeLightbox();
    });

    lightbox.addEventListener('wheel', (e) => {
      e.preventDefault();
      const delta = e.deltaY > 0 ? -0.15 : 0.15;
      scale = Math.min(Math.max(0.5, scale + delta), 5);
      updateTransform();
    }, { passive: false });

    lightboxImg.addEventListener('mousedown', (e) => {
      e.preventDefault();
      isDragging = true;
      lightboxImg.classList.add('grabbing');
      startX = e.clientX;
      startY = e.clientY;
      initialTranslateX = translateX;
      initialTranslateY = translateY;
    });

    window.addEventListener('mousemove', (e) => {
      if (!isDragging) return;
      translateX = initialTranslateX + (e.clientX - startX);
      translateY = initialTranslateY + (e.clientY - startY);
      updateTransform();
    });

    window.addEventListener('mouseup', () => {
      isDragging = false;
      lightboxImg.classList.remove('grabbing');
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') closeLightbox();
    });
  