# ms_weight_correct

ALMA の Measurement Set (MS) から解析用の npz を作成し、ディスク幾何を用いて WEIGHT のバイアスを推定・補正するためのコード。

* `ms_to_npz.py` — Measurement Set を npz に変換する。`protomidpy` の入力にも使用可能。
* `correct_weight_ms.py` — ディスク幾何（例: 位置角、傾斜、中心）を用いて軸対称性を仮定し重みのバイアスを推定する。
* `compute_bias_weight.py` — 推定したバイアスに基づき MS の WEIGHT（必要なら SIGMA も）を補正する。
* `average_ms.py` - Measurement setをChannel & Time Averageする。データ量を減らしたい時に便利。

---


## Quick Start

自分のmsファイル名、出力ファイル、円盤幾何へ変更すること

```bash
# 1) MS → NPZ 変換（CASAを使う）
casa  -c ms_to_npz.py

npzは`protomidpy`にも使える。

# 2) WEIGHT バイアスの推定（ディスク幾何が必要）
python correct_weight_ms.py

# 3) バイアスの適用（
python compute_bias_weight.py

## Tips
`average_ms.py`を用いて、msをaveragingしてサイズを下げると解析がやりやすい。


