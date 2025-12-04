import os
import random
import shutil
import argparse


def split_dataset(
    input_dirs,
    output_root,
    train_ratio=0.8,
    val_ratio=0.1,
    test_ratio=0.1,
    seed=42,
    move=False,
):
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6, \
        "train + val + test ratios must sum to 1.0"

    os.makedirs(output_root, exist_ok=True)

    # 各フォルダ内のファイル一覧（辞書順ソート）
    files_by_dir = {}
    for d in input_dirs:
        all_files = [
            fn for fn in os.listdir(d)
            if os.path.isfile(os.path.join(d, fn))
        ]
        all_files.sort()  # Lexicographical order
        files_by_dir[d] = all_files
        print(f"{d}: {len(all_files)} files")

    # 各フォルダのファイル数が違う場合は、最小に合わせる
    lengths = [len(fns) for fns in files_by_dir.values()]
    n = min(lengths)
    if len(set(lengths)) != 1:
        print("WARNING: 入力フォルダでファイル数が異なります。")
        print("         最小のファイル数に合わせて先頭 n 件だけを使用します。")
        print("         counts:", dict(zip(input_dirs, lengths)))
        print(f"         使用されるサンプル数: {n}")

    if n == 0:
        raise ValueError("使用可能なファイルがありません。")

    # サンプルインデックス [0, 1, ..., n-1] を train/val/test に分割
    indices = list(range(n))
    random.seed(seed)
    random.shuffle(indices)

    n_train = int(n * train_ratio)
    n_val = int(n * val_ratio)
    n_test = n - n_train - n_val

    train_idx = set(indices[:n_train])
    val_idx = set(indices[n_train:n_train + n_val])
    test_idx = set(indices[n_train + n_val:])

    def split_of(idx: int) -> str:
        if idx in train_idx:
            return "train"
        if idx in val_idx:
            return "val"
        return "test"

    print("Total samples used:", n)
    print(f"train: {len(train_idx)}, val: {len(val_idx)}, test: {len(test_idx)}")

    # 出力フォルダ準備
    for d in input_dirs:
        category = os.path.basename(os.path.normpath(d))
        for split in ["train", "val", "test"]:
            out_dir = os.path.join(output_root, split, category)
            os.makedirs(out_dir, exist_ok=True)

    # コピー or 移動
    op = shutil.move if move else shutil.copy2

    # 各フォルダごとに、対応するインデックスのファイルを split ごとに配置
    for d in input_dirs:
        category = os.path.basename(os.path.normpath(d))
        fns = files_by_dir[d]
        for idx in range(n):
            split = split_of(idx)
            fn = fns[idx]
            src = os.path.join(d, fn)
            dst = os.path.join(output_root, split, category, fn)
            op(src, dst)

    print("Done!")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Split multiple folders into train/val/test, pairing files by lexicographical order."
    )

    parser.add_argument(
        "-i", "--inputs",
        nargs="+",
        required=True,
        help="入力フォルダ（2つ以上、絶対パスでも相対パスでも可）",
    )
    parser.add_argument(
        "-o", "--output",
        required=True,
        help="出力ルートフォルダ（train/val/test 以下にフォルダごとに配置）",
    )
    parser.add_argument(
        "--train_ratio",
        type=float,
        default=0.8,
        help="Train ratio (default: 0.8)",
    )
    parser.add_argument(
        "--val_ratio",
        type=float,
        default=0.1,
        help="Validation ratio (default: 0.1)",
    )
    parser.add_argument(
        "--test_ratio",
        type=float,
        default=0.1,
        help="Test ratio (default: 0.1)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="シャッフル用のランダムシード",
    )
    parser.add_argument(
        "--move",
        action="store_true",
        help="コピーではなく move したい場合に指定",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if len(args.inputs) < 2:
        raise ValueError("入力フォルダは 2 つ以上指定してください (--inputs)")

    split_dataset(
        args.inputs,
        args.output,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        test_ratio=args.test_ratio,
        seed=args.seed,
        move=args.move,
    )
