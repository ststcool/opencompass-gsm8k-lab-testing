# MiniMax-M3 × GSM8K 数学能力评测（OpenCompass 实战）

> 面向测试工程师的大模型评测最小可复现实验：5 分钟跑通一次真实的数学推理评测，
> 并学会把"分数"拆成"模型真实能力"与"评测工装问题"。

## 这个仓库做什么

用 [OpenCompass](https://github.com/open-compass/opencompass) 评测框架，让 MiniMax-M3 做一份
64 道小学数学应用题的试卷（GSM8K 演示子集），自动出题、收卷、判分、出报告。

实测结果（2026-10-18，两次独立运行）：

| 运行 | 分数 | 说明 |
|---|---|---|
| 第 1 次 | 92.19（59/64） | 默认输出上限，1 题被截断 |
| 第 2 次 | 90.62（58/64） | `max_out_len=4096` 修复截断后 |
| 判据修正后估计 | ≈95.3 | 2~3 题"答对了但被判卷规则误伤"（千分位逗号、百分号、自然语言结尾） |

关键发现：**两次考试只有 2 道题是共同做错的（稳定短板），其余错题一半以上是
"判卷格式误伤"——看分数之前，必须先分清被测件问题与测试工装问题。**

## 环境要求

- Linux / macOS，Python ≥ 3.10
- 一个 MiniMax API key（国内站 api.minimaxi.com 申请；国际站 .io 的 key 不通用）
- 能访问 https://hf-mirror.com（HuggingFace 镜像，加载分词器用）

## 快速开始

```bash
# 1. 安装（建议独立虚拟环境）
conda create -n opencompass python=3.12 -y
conda activate opencompass
pip install opencompass==0.5.4

# 2. 设置环境变量
export OPENAI_API_KEY="你的MiniMax key"   # OpenCompass 经 OpenAI 兼容端点调 MiniMax
export HF_ENDPOINT=https://hf-mirror.com  # 国内必须，否则分词器加载会卡住

# 3. 运行评测（在任意目录均可）
opencompass configs/minimax_gsm8k_lab.py --work-dir outputs/lab --debug

# 4. 失败分析（跑完后）
python tools/analyze_failures.py outputs/lab
```

## 产物结构

```
outputs/lab/<时间戳>/
├── configs/        # 本次运行的完整配置快照（复现凭证）
├── predictions/    # 逐样本：原始 prompt + 模型完整回答 + 标准答案 ← 失败分析的金矿
├── results/        # 逐样本判定（提取答案/正误）+ 汇总分数
└── summary/        # 最终报告（txt / csv / md 三种格式）
```

## 换成你自己的模型/数据

- **换模型**：MiniMax 提供 OpenAI 兼容端点，任何 OpenAI 兼容 API 都能用同样方式接入——
  改 `configs/minimax_gsm8k_lab.py` 里的 `path`（模型名）与 `openai_api_base`（端点）两行即可。
- **换数据集**：把 `demo_gsm8k_chat_gen` 换成 OpenCompass 内置的数百个数据集名，
  或用 `--custom-dataset-path your.jsonl` 直接评测你自己的业务数据
  （`.jsonl` 每行 `{"question": "...", "answer": "..."}`，详见官方文档 Custom Dataset）。
- **重复评测**：同一试卷跑多次报"均值 ± 波动"，消除单次随机性
  （本仓库两次运行已差 1.57 分，错题集合只重合 2 道）。

## 常见坑（已在本仓库配置中规避）

| 坑 | 规避方式 |
|---|---|
| huggingface.co 国内直连超时，评测"挂死" | `HF_ENDPOINT=https://hf-mirror.com` |
| MiniMax 国际站/国内站 key 不通用（401） | 国内 key 用 `api.minimaxi.com/v1` |
| 推理模型输出被默认 512 token 上限截断 | 配置中显式 `max_out_len=4096` |
| 配置里用 `os.environ` 取密钥导致快照序列化崩溃 | 用 `key='ENV'`，运行时从环境变量读取 |
| 千分位逗号/百分号被判卷规则误伤 | 判卷前必读 predictions 原文；或要求模型以 `#### 数字` 收尾 |

## 许可

MIT（代码部分）；GSM8K 数据集遵循其原始许可（MIT，OpenAI）。
