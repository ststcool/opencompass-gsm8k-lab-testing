# MiniMax-M3 × GSM8K 演示集评测配置（自包含，可直接运行）
#
# 用法：
#   export OPENAI_API_KEY="你的MiniMax key"
#   export HF_ENDPOINT=https://hf-mirror.com
#   opencompass configs/minimax_gsm8k_lab.py --work-dir outputs/lab --debug
#
# 说明：
# - MiniMax 提供 OpenAI 兼容端点，因此走 OpenCompass 的 OpenAISDK；
#   key='ENV' 表示运行时从 OPENAI_API_KEY 环境变量读取，密钥不落盘。
# - 国内申请的 key 必须用国内站端点 api.minimaxi.com（国际站 api.minimax.io 不通用）。
# - max_out_len=4096：不设时默认 512 token，推理型模型的长输出会被静默截断。
from mmengine.config import read_base

from opencompass.models import OpenAISDK

with read_base():
    from opencompass.configs.datasets.demo.demo_gsm8k_chat_gen import \
        gsm8k_datasets

datasets = gsm8k_datasets

models = [
    dict(
        type=OpenAISDK,
        abbr='minimax-m3',          # 产物目录名 / 报告里的模型名
        path='MiniMax-M3',          # 请求 API 时的模型名
        key='ENV',                  # 运行时从 OPENAI_API_KEY 读取
        openai_api_base='https://api.minimaxi.com/v1',  # 国内站端点
        max_seq_len=1000000,
        max_out_len=4096,           # 修复：默认 512 会截断推理模型输出
        query_per_second=1,
        retry=10,
        max_workers=8,
    )
]
