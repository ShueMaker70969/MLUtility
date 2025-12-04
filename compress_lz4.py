import argparse
import os
import tarfile
import tempfile
import shutil
import sys

try:
    import lz4.frame as lz4f
    HAS_LZ4 = True
except ImportError:
    HAS_LZ4 = False


def compress_folder_to_tar_lz4(input_folder, output_path=None):
    if not HAS_LZ4:
        print("ERROR: lz4 がインストールされていません。")
        print("      pip install lz4  を実行してください。")
        sys.exit(1)

    input_folder = os.path.abspath(input_folder)
    if not os.path.isdir(input_folder):
        raise NotADirectoryError(f"フォルダが存在しません: {input_folder}")

    folder_name = os.path.basename(os.path.normpath(input_folder))

    # 出力ファイル名がなければ自動生成
    if output_path is None:
        parent = os.path.dirname(input_folder)
        output_path = os.path.join(parent, f"{folder_name}.tar.lz4")

    output_path = os.path.abspath(output_path)

    print(f"入力フォルダ : {input_folder}")
    print(f"出力ファイル : {output_path}")

    # 一時 tar 作成
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_tar = os.path.join(tmpdir, f"{folder_name}.tar")
        print(f"一時 TAR を作成中: {tmp_tar}")

        # tar 作成
        with tarfile.open(tmp_tar, "w") as tar:
            tar.add(input_folder, arcname=folder_name)

        # lz4 圧縮
        print(f"LZ4 圧縮中...")
        with open(tmp_tar, "rb") as f_in, lz4f.open(output_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

    print("完了しました！")
    return output_path


def parse_args():
    parser = argparse.ArgumentParser(
        description="指定フォルダを .tar.lz4 に圧縮するシンプルツール"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="圧縮したいフォルダの絶対パス（相対パスでもOK）"
    )
    parser.add_argument(
        "--output",
        help=".tar.lz4 の出力先（省略すると自動生成）"
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    compress_folder_to_tar_lz4(args.input, args.output)
