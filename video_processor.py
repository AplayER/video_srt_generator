import os
import subprocess
from googletrans import Translator
import whisper
from pydub import AudioSegment
import pysrt
import ffmpeg
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from faster_whisper import WhisperModel

openai_whisper_model = whisper.load_model("large-v3", device="cpu")  # 加载 Whisper 模型


def extract_audio(video_path):
    audio_path = video_path.rsplit('.', 1)[0] + '.wav'
    command = [
        "ffmpeg", "-i", video_path, "-vn", "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "2", audio_path, "-y"
    ]
    subprocess.run(command, check=True)
    print(f"音频文件已保存: {audio_path}")

    return audio_path

def generate_subtitles(audio_path,model=openai_whisper_model):
    """ 使用 Whisper 生成字幕 """
    audio_2_text_time = datetime.now()
    print(f"语言转文字开始时间: {audio_2_text_time}")
    result = model.transcribe(audio_path, verbose=True)
    subtitle_path = audio_path.rsplit('.', 1)[0] + '.srt'
    
    print(f"语言转文字执行时间: {datetime.now() - audio_2_text_time}")
    print(f"字幕文件已保存: {subtitle_path}")


    subs = pysrt.SubRipFile()
    text_2_srt_time = datetime.now()
    print(f"将转录结果格式化为字幕文件开始时间: {text_2_srt_time}")

    # 将转录结果格式化为字幕文件
    start_time = 0
    for idx, segment in enumerate(result["segments"]):
        start_time_ms = int(segment["start"] * 1000)
        end_time_ms = int(segment["end"] * 1000)
        text = segment["text"]

        sub = pysrt.SubRipItem(
            index=idx + 1,
            start=pysrt.SubRipTime(milliseconds=start_time_ms),
            end=pysrt.SubRipTime(milliseconds=end_time_ms),
            text=text
        )
        subs.append(sub)
    print(f"将转录结果格式化为字幕文件执行时间: {datetime.now() - text_2_srt_time}")
    subs.save(subtitle_path)
    print(f"字幕文件已保存: {subtitle_path}")
    os.remove(audio_path)
    print(f"音频文件已删除: {audio_path}")
    return subtitle_path

# fast_model = WhisperModel("large-v3", device="cpu", compute_type="int8")  # 如果没有 GPU, 可以改为 device="cpu"

# def generate_subtitles_with_faster_whisper(audio_path,model=fast_model):
#     """ 使用 Whisper 生成字幕 """
#     segments,_ = model.transcribe(audio_path)
#     subtitle_path = audio_path.rsplit('.', 1)[0] + '.srt'

#     subs = pysrt.SubRipFile()

#     # 将转录结果格式化为字幕文件
#     start_time = 0
#     for idx, segment in enumerate(segments):
#         start_time_ms = int(segment.start * 1000)
#         end_time_ms = int(segment.end * 1000)
#         text = segment.text.strip()

#         sub = pysrt.SubRipItem(
#             index=idx + 1,
#             start=pysrt.SubRipTime(milliseconds=start_time_ms),
#             end=pysrt.SubRipTime(milliseconds=end_time_ms),
#             text=text
#         )
#         subs.append(sub)

#     subs.save(subtitle_path)
#     print(f"字幕文件已保存: {subtitle_path}")
#     os.remove(audio_path)
#     print(f"音频文件已删除: {audio_path}")
#     return subtitle_path



def translate_subtitles(subtitle_path):
    translator = Translator()
    translated_subtitle_path_cn = subtitle_path.rsplit('.', 1)[0] + '_cn.srt'
    translated_subtitle_path_en = subtitle_path.rsplit('.', 1)[0] + '_en.srt'
    
    with open(subtitle_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    with open(translated_subtitle_path_cn, 'w', encoding='utf-8') as file_cn, \
         open(translated_subtitle_path_en, 'w', encoding='utf-8') as file_en:
        for line in lines:
            if line.strip() and not line.strip().isdigit() and '-->' not in line:
                translation_cn = translator.translate(line, dest='zh-cn').text
                translation_en = translator.translate(line, dest='en').text
                file_cn.write(translation_cn + '\n')
                file_en.write(translation_en + '\n')
            else:
                file_cn.write(line)
                file_en.write(line)
    
    return translated_subtitle_path_cn, translated_subtitle_path_en

import asyncio

async def batch_rpc_translate(lines, lang):
    """批量翻译文本列表"""
    translator = Translator()
    translations = await translator.translate(lines, dest=lang)
    return [t.text for t in translations]  # 提取翻译后的文本

def batch_translate_subtitles(subtitle_path, batch_size=20):
    translator = Translator()
    translated_subtitle_path_cn = subtitle_path.rsplit('.', 1)[0] + '_cn.srt'
    translated_subtitle_path_en = subtitle_path.rsplit('.', 1)[0] + '_en.srt'
    
    with open(subtitle_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # 提取需要翻译的文本（去掉时间戳、空行等）
    text_lines = [line.strip() for line in lines if line.strip() and not line.strip().isdigit() and '-->' not in line]
    
    print(f"提取需要翻译的文本 {text_lines}")
    # 分批次进行翻译
    def process_batch(start):
        batch = text_lines[start: start + batch_size]
        return batch_rpc_translate(batch, 'zh-cn'), batch_rpc_translate(batch, 'en')

    translated_cn, translated_en = [], []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(process_batch, i) for i in range(0, len(text_lines), batch_size)]
        for future in futures:
            cn_batch, en_batch = future.result()
            translated_cn.extend(asyncio.run(cn_batch))
            translated_en.extend(asyncio.run(en_batch))

    # 将翻译结果写回文件
    with open(translated_subtitle_path_cn, 'w', encoding='utf-8') as file_cn, \
         open(translated_subtitle_path_en, 'w', encoding='utf-8') as file_en:
        
        index = 0
        for line in lines:
            if line.strip() and not line.strip().isdigit() and '-->' not in line:
                file_cn.write(translated_cn[index] + '\n')
                file_en.write(translated_en[index] + '\n')
                index += 1
            else:
                file_cn.write(line)
                file_en.write(line)
    
    return translated_subtitle_path_cn, translated_subtitle_path_en

def merge_subtitles_with_video(video_path, subtitles, output_folder):
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

    output_path =  os.path.splitext(os.path.basename(video_path))[0] + '_' + current_time + '_output.mkv'

    output_path = os.path.join(output_folder, output_path)
    print(f"输出文件: {output_path}")
    """
    使用 ffmpeg 将多个字幕封装到 MKV 视频中（软字幕，可切换）
    
    :param video_path: 输入视频路径
    :param subtitles: 字幕文件列表 (SRT 或 ASS)
    :param output_path: 输出文件路径 (MKV 格式)
    """
    # 构建 ffmpeg 命令
    input_streams = [ffmpeg.input(video_path)]
    map_args = ['-map', '0:v', '-map', '0:a']  # 映射视频和音频
    metadata_args = {}  # 用于字幕的元数据（命名）


    # 添加字幕流
    for i, subtitle in enumerate(subtitles):
        input_streams.append(ffmpeg.input(subtitle))
        map_args.extend(['-map', str(i + 1)])
        subtitle_name = 'Original'
        if '_cn' in subtitle:
            subtitle_name = 'Chinese'
        if '_en' in subtitle:
            subtitle_name = 'English'
        metadata_args[f'metadata:s:s:{i}'] = f'title={subtitle_name}'

    

    # 执行 ffmpeg 命令
    ffmpeg.output(
        *input_streams, output_path,
        **{'c:v': 'copy', 'c:a': 'copy', 'c:s': 'srt', **metadata_args}  # 复制视频/音频，字幕设为 SRT
    ).global_args(*map_args).run()
    
    return output_path

def process_video(video_path, output_folder):
    start_time = time.time()  # 记录开始时间
    print(f"输入文件: {video_path}")

    audio_path = extract_audio(video_path)
    extract_audio_time = time.time()
    print(f"提取音频执行时间: {extract_audio_time - start_time:.4f} 秒")
    subtitle_path = generate_subtitles(audio_path)
    generate_subtitles_time = time.time()

    print(f"音频转文字执行时间: {time.time() - extract_audio_time:.4f} 秒")

    translated_subtitle_paths = batch_translate_subtitles(subtitle_path,1000)
    translate_subtitles_time = time.time()

    print(f"字幕翻译执行时间: {time.time() - generate_subtitles_time:.4f} 秒")

    output_path = merge_subtitles_with_video(video_path, [subtitle_path] + list(translated_subtitle_paths), output_folder)
    
    # os.remove(subtitle_path)
    # for t in translated_subtitle_paths:
    #     os.remove(t)
    print(f"字幕文件已删除: {subtitle_path}, {translated_subtitle_paths}")
    print(f"文件合并执行时间: {time.time() - translate_subtitles_time:.4f} 秒")
    print(f"输出文件已完成: {output_path}")

    return output_path
