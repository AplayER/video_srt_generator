from video_processor import merge_subtitles_with_video
import os


test_video_path = "uploads/Love.Is.Blind.Brazil.S01E01.Pod.of.Love.1080p.NF.WEB-DL.DUAL.DDP5.1.H.264-SMURFeztv.re.mkv"
test_subtitle_paths = ["uploads/Love.Is.Blind.Brazil.S01E01.Pod.of.Love.1080p.NF.WEB-DL.DUAL.DDP5.1.H.264-SMURFeztv.re.srt", "uploads/Love.Is.Blind.Brazil.S01E01.Pod.of.Love.1080p.NF.WEB-DL.DUAL.DDP5.1.H.264-SMURFeztv.re_cn.srt", "uploads/Love.Is.Blind.Brazil.S01E01.Pod.of.Love.1080p.NF.WEB-DL.DUAL.DDP5.1.H.264-SMURFeztv.re_en.srt"]
test_output_folder = "unit_test_output"
print(os.getcwd()) # 打印当前工作目录
output_path = merge_subtitles_with_video(test_video_path, test_subtitle_paths, test_output_folder)

