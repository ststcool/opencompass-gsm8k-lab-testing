#!/usr/bin/env python3
"""逐样本失败分析：把"分数"拆成"真·推理错误"与"判卷格式误伤"。

用法：
    python tools/analyze_failures.py outputs/lab
    python tools/analyze_failures.py outputs/lab --model minimax-m3 --dataset demo_gsm8k

输出：总样本数、失败数、每道错题的 标准答案 / 提取答案 / 模型回答结尾，
便于人工判定失分根因（模型能力 vs 判卷规则 vs 输出截断）。
"""
import argparse
import glob
import json
import os
import sys


def newest_exp_dir(work_dir):
    exps = sorted(glob.glob(os.path.join(work_dir, '2*')))
    if not exps:
        sys.exit(f'未找到实验目录：{work_dir}')
    return exps[-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('work_dir', help='opencompass 的 --work-dir，或其中的某个时间戳目录')
    ap.add_argument('--model', default='minimax-m3')
    ap.add_argument('--dataset', default='demo_gsm8k')
    ap.add_argument('--tail', type=int, default=120, help='展示模型回答结尾的字符数')
    args = ap.parse_args()

    exp = args.work_dir
    if not os.path.basename(exp).startswith('2'):
        exp = newest_exp_dir(exp)
    print(f'实验目录: {exp}')

    preds = json.load(open(os.path.join(exp, 'predictions', args.model, f'{args.dataset}.json')))
    results = json.load(open(os.path.join(exp, 'results', args.model, f'{args.dataset}.json')))
    details = results['details']

    wrong = [d for d in details if d['correct'][0] is not True]
    print(f'总样本: {len(details)}  失败: {len(wrong)}  分数: {results.get("score", "?")}')
    print('=' * 70)
    for d in wrong:
        idx = d['example_abbr'].split('_')[-1]
        pred_full = str(preds[idx]['prediction'])
        print(f"[{d['example_abbr']}] 标准答案={d['answer']}  提取答案={d['pred']}")
        print(f"  模型回答结尾: ...{pred_full[-args.tail:]!r}")
        # 粗分类提示
        if d['pred'] in ('NULL', None) or (d['pred'] and str(d['answer']) not in str(d['pred'])):
            tail = pred_full[-args.tail:]
            if str(d['answer']).strip("[]'") in tail:
                print('  >> 提示: 标准答案出现在回答结尾，疑似【判卷格式误伤】')
        print('-' * 70)


if __name__ == '__main__':
    main()
