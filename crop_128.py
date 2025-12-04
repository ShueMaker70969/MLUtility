import argparse
import os
from pathlib import Path

from PIL import Image
from tqdm import tqdm  # ← 追加


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp"}


def find_images(root: Path):
    """root 以下の全ての画像ファイル Path を再帰的に列挙"""
    root = root.resolve()
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
            yield path


def compute_crop_box(w: int, h: int, size: int, position: str):
    """画像サイズ (w, h) とクロップ位置から crop box を計算"""
    if w < size or h < size:
        return None  # 小さすぎるのでクロップ不可

    if position == "center":
        left = (w - size) // 2
        top = (h - size) // 2
    elif position == "topleft":
        left, top = 0, 0
    elif position == "topright":
        left, top = w - size, 0
    elif position == "bottomleft":
        left, top = 0, h - size
    elif position == "bottomright":
        left, top = w - size, h - size
    else:
        raise ValueError(f"Unknown position: {position}")

    return (left, top, left + size, top + size)


def crop_images_inplace(root_dir: str, size: int = 128, position: str = "center"):
    root_path = Path(root_dir).resolve()
    if not root_path.is_dir():
        raise NotADirectoryError(f"指定されたパスはフォルダではありません: {root_path}")

    images = list(find_images(root_path))
    num_images = len(images)

    print("=== クロップ対象の情報 ===")
    print(f"ルートフォルダ: {root_path}")
    print(f"検出された画像枚数: {num_images}")
    print(f"クロップサイズ: {size}x{size}")
    print(f"クロップ位置: {position}")
    print("※ すべての画像は上書きされます。元には戻せません。")
    print("=========================")

    if num_images == 0:
        print("画像が見つからなかったため、処理を終了します。")
        return

    ans = input("本当にクロップを実行しますか？ (y/N): ").strip().lower()
    if ans != "y":
        print("キャンセルされました。何も変更していません。")
        return

    skipped_small = 0
    processed = 0

    # tqdm progress bar
    for img_path in tqdm(images, desc="Cropping", ncols=80):
        try:
            with Image.open(img_path) as img:
                w, h = img.size
                box = compute_crop_box(w, h, size, position)
                if box is None:
                    skipped_small += 1
                    continue

                cropped = img.crop(box)
                cropped.save(img_path)
                processed += 1
        except Exception as e:
            print(f"[ERROR] {img_path} の処理中にエラー: {e}")

    print("=== 処理完了 ===")
    print(f"クロップした画像枚数: {processed}")
    print(f"サイズ不足でスキップした枚数: {skipped_small}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="指定フォルダ以下の全画像を 128x128 にクロップして上書きするツール"
    )

    parser.add_argument(
        "-r", "--root",
        required=True,
        help="処理対象のルートフォルダ（絶対パス推奨）"
    )
    parser.add_argument(
        "-s", "--size",
        type=int,
        default=128,
        help="クロップサイズ（正方形）。デフォルト: 128"
    )
    parser.add_argument(
        "-p", "--position",
        choices=["center", "topleft", "topright", "bottomleft", "bottomright"],
        default="center",
        help="クロップ位置（center/topleft/topright/bottomleft/bottomright）。デフォルト: center"
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    crop_images_inplace(args.root, size=args.size, position=args.position)
