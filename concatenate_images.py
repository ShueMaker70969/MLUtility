import os
import argparse
from PIL import Image

'''
画像を繋げるコード。二つディレクトリを入力として指定、そして出力ディレクトリを指定するとそこに繋げられた
画像が生成される。ディレクトリ二つに存在する画像ペアの順番が一致していることを前提としたコードなのでそれには注意。
'''

def load_and_sort_images(folder):
    # 画像ファイルだけ抽出し、名前順ソート
    files = [f for f in os.listdir(folder) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
    files.sort()
    return files

def concat_images(img1_path, img2_path):
    img1 = Image.open(img1_path).convert("RGB")
    img2 = Image.open(img2_path).convert("RGB")

    # 高さを統一する必要があればここでリサイズも可能
    # 今回はそのまま結合

    w1, h1 = img1.size
    w2, h2 = img2.size

    new_img = Image.new("RGB", (w1 + w2, max(h1, h2)))
    new_img.paste(img1, (0, 0))
    new_img.paste(img2, (w1, 0))

    return new_img

def main(args):
    folder_left = args.folder_left     # Diffuse
    folder_right = args.folder_right   # Normal
    out_dir = args.output

    os.makedirs(out_dir, exist_ok=True)

    left_files = load_and_sort_images(folder_left)
    right_files = load_and_sort_images(folder_right)

    # ペア数は小さい方に合わせる
    count = min(len(left_files), len(right_files))

    print(f"Found {len(left_files)} left images, {len(right_files)} right images")
    print(f"Processing {count} pairs...")

    for i in range(count):
        left_path = os.path.join(folder_left, left_files[i])
        right_path = os.path.join(folder_right, right_files[i])

        combined = concat_images(left_path, right_path)

        # 出力名 0000001.png 形式
        out_name = f"{i+1:07d}.png"
        combined.save(os.path.join(out_dir, out_name))

        print(f"Saved: {out_name}")

    print("Done!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder_left", required=True, help="Left image folder (Diffuse)")
    parser.add_argument("--folder_right", required=True, help="Right image folder (Normal)")
    parser.add_argument("--output", required=True, help="Output folder")
    args = parser.parse_args()

    main(args)
