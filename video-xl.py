import argparse
import re
import time
import os
import glob
import gc
from moviepy.editor import VideoFileClip, concatenate_videoclips
from moviepy.video.fx import loop
from moviepy.audio.fx import audio_loop
from moviepy.video.fx.all import fadein, fadeout
from moviepy.audio.fx.all import audio_fadein, audio_fadeout

TEMP_LOOPED_PATH = "temp_looped.mp4"
TEMP_AUDIO_PATH = "temp_audio.m4a"
PROGRESS_LOG = "progress.log"

def print_banner():
    print(r"""
# ====================================================
# __      _______ _____  ______ ____   __   ___      
# \ \    / /_   _|  __ \|  ____/ __ \  \ \ / / |     
#  \ \  / /  | | | |  | | |__ | |  | |  \ V /| |     
#   \ \/ /   | | | |  | |  __|| |  | |   > < | |     
#    \  /   _| |_| |__| | |___| |__| |  / . \| |____ 
#     \/   |_____|_____/|______\____/  /_/ \_\______|
#                  "Play With Veo 3"
#               Coded By: RevanBlezinsky
# ====================================================
""")

def parse_duration(duration_str):
    if not duration_str:
        return None
    match = re.match(r"([\d\.]+)(h|m|s)?", duration_str.strip().lower())
    if not match:
        raise ValueError("Format durasi tidak valid.")
    value, unit = match.groups()
    value = float(value)
    return value * 3600 if unit == "h" else value * 60 if unit == "m" else value

def clean_cache():
    for file in [TEMP_LOOPED_PATH, TEMP_AUDIO_PATH, PROGRESS_LOG]:
        if os.path.exists(file):
            os.remove(file)
            print(f"\U0001f9f9 Dihapus: {file}")

def auto_detect_input():
    mp4_files = glob.glob("*.mp4")
    if not mp4_files:
        raise FileNotFoundError("Tidak ada file .mp4 ditemukan di direktori ini.")
    print(f"\U0001f4c1 Auto mendeteksi file: {mp4_files[0]}")
    return mp4_files[0]

def guess_output_name(input_path):
    base, ext = os.path.splitext(input_path)
    return f"{base}_extended{ext}"

def blend_multiple_videos(video_files, output_path, fade_duration=1):
    print("\n🎞️  Menggabungkan beberapa video dengan transisi halus...")
    clips = []
    for path in video_files:
        print(f"➕ Menambahkan: {path}")
        clip = VideoFileClip(path).fx(fadein, fade_duration).fx(fadeout, fade_duration)
        clips.append(clip)

    final_clip = concatenate_videoclips(clips, method="compose")
    final_clip.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile=TEMP_AUDIO_PATH,
        remove_temp=True,
        ffmpeg_params=['-movflags', '+faststart', '-pix_fmt', 'yuv420p']
    )

    print(f"\n✅ Video gabungan selesai disimpan di: {output_path}")
    gc.collect()

def extend_video(video_path, output_path, target_duration=None, use_gpu=False, quality='fast', clean_after=False):
    print(f"\n\U0001f527 Mode: {'GPU (HEVC_NVENC)' if use_gpu else 'CPU'} - Quality: {quality}")
    print(f"\U0001f4c2 Memuat video: {video_path}")
    start_time = time.time()

    looped_clip = None
    try:
        if os.path.exists(TEMP_LOOPED_PATH):
            print("⚠️  Cache ditemukan: Menggunakan temp_looped.mp4 untuk proses akhir...")
            looped_clip = VideoFileClip(TEMP_LOOPED_PATH)
        else:
            original_clip = VideoFileClip(video_path)
            if target_duration is None:
                target_duration = original_clip.audio.duration

            print("🔁 Membuat video loop...")
            clip = original_clip.fx(fadein, 1).fx(fadeout, 1)
            looped_clip = loop.loop(clip, duration=target_duration)
            looped_audio = audio_loop.audio_loop(original_clip.audio.fx(audio_fadein, 1).fx(audio_fadeout, 1), duration=target_duration)
            looped_clip = looped_clip.set_audio(looped_audio)

            print("💾 Menyimpan hasil loop ke cache...")
            looped_clip.write_videofile(
                TEMP_LOOPED_PATH,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile=TEMP_AUDIO_PATH,
                remove_temp=False,
                threads=8,
                preset='medium',
                ffmpeg_params=['-movflags', '+faststart', '-pix_fmt', 'yuv420p']
            )
            with open(PROGRESS_LOG, "w") as f:
                f.write("looped_clip_done")

            del looped_clip
            looped_clip = VideoFileClip(TEMP_LOOPED_PATH)

        codec = 'hevc_nvenc' if use_gpu else 'libx264'
        preset = quality if use_gpu else ('medium' if quality == 'fast' else 'slow')

        print(f"🎬 Memulai proses render ke: {output_path}")
        looped_clip.write_videofile(
            output_path,
            codec=codec,
            audio_codec='aac',
            temp_audiofile=TEMP_AUDIO_PATH,
            remove_temp=False,
            bitrate='5000k',
            audio_bitrate='320k',
            threads=8,
            preset=preset,
            ffmpeg_params=['-movflags', '+faststart', '-pix_fmt', 'yuv420p']
        )

        end_time = time.time()
        minutes, seconds = divmod(end_time - start_time, 60)
        print(f"\n✅ Proses selesai dalam {int(minutes)} menit {int(seconds)} detik.")

        if clean_after:
            print("🧹 Membersihkan cache...")
            clean_cache()
        else:
            print("📌 Cache disimpan. Bisa digunakan untuk proses ulang jika perlu.")

    finally:
        if looped_clip:
            looped_clip.close()
        gc.collect()

def interactive_input():
    mode_choice = input("📽️ Mode (1 = Extend Video, 2 = Blend Video): ").strip()

    if mode_choice == '2':
        output_path = input("💾 Masukkan path file video output: ").strip()
        return 'blend', None, output_path, None, None, None
    else:
        input_path = input("📂 Masukkan path file video input: ").strip()
        output_path = input("💾 Masukkan path file video output: ").strip()
        duration_input = input("⏱️ Durasi target (misal: 5h, 30m, 90s) [enter untuk default]: ").strip()
        mode = input("🎥 Gunakan GPU acceleration? (y/n): ").strip().lower()
        quality = input("⚙️ Kualitas encode (fast/high): ").strip().lower()
        clean = input("🧹 Bersihkan cache setelah selesai? (y/n): ").strip().lower()

        use_gpu = mode == 'y'
        quality = 'fast' if quality not in ['high', 'slow'] else 'slow'
        duration = parse_duration(duration_input) if duration_input else None
        clean_after = clean == 'y'

        return 'extend', input_path, output_path, duration, use_gpu, clean_after

if __name__ == "__main__":
    print_banner()
    parser = argparse.ArgumentParser(description="Perpanjang atau gabungkan video dengan dukungan resume & cache.")
    parser.add_argument('-i', '--input', help='Path video input')
    parser.add_argument('-o', '--output', help='Path video output')
    parser.add_argument('-d', '--duration', help='Durasi target (misal: 18000, 5h, 30m)')
    parser.add_argument('--gpu', action='store_true', help='Gunakan GPU (NVENC)')
    parser.add_argument('--quality', choices=['fast', 'high'], default='fast', help='Kualitas encode')
    parser.add_argument('--clean', action='store_true', help='Bersihkan cache setelah selesai')
    parser.add_argument('--blend', action='store_true', help='Gabungkan beberapa file .mp4 dengan fade in/out')

    args = parser.parse_args()

    if args.blend:
        video_files = sorted(glob.glob("*.mp4"))
        if len(video_files) < 2:
            print("❌ Dibutuhkan minimal 2 file .mp4 di folder ini untuk mode blend.")
        else:
            output_path = args.output if args.output else "output_blended.mp4"
            blend_multiple_videos(video_files, output_path)
    else:
        if not args.input or not args.output:
            mode_selected, input_path, output_path, duration, use_gpu, clean_after = interactive_input()
            if mode_selected == 'blend':
                video_files = sorted(glob.glob("*.mp4"))
                if len(video_files) < 2:
                    print("❌ Dibutuhkan minimal 2 file .mp4 di folder ini untuk mode blend.")
                else:
                    blend_multiple_videos(video_files, output_path)
                exit()
            quality = 'fast'
        else:
            input_path = args.input
            output_path = args.output
            duration = parse_duration(args.duration) if args.duration else None
            use_gpu = args.gpu
            quality = 'slow' if args.quality == 'high' else 'fast'
            clean_after = args.clean

        extend_video(input_path, output_path, duration, use_gpu, quality, clean_after)
