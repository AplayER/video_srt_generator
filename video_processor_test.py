import unittest
import os
from video_processor import merge_subtitles_with_video

class TestVideoProcessor(unittest.TestCase):

    def setUp(self):
        self.video_path = "uploads/Love.Is.Blind.Brazil.S01E01.Pod.of.Love.1080p.NF.WEB-DL.DUAL.DDP5.1.H.264-SMURFeztv.re.mkv"
        self.subtitle_paths = ["uploads/Love.Is.Blind.Brazil.S01E01.Pod.of.Love.1080p.NF.WEB-DL.DUAL.DDP5.1.H.264-SMURFeztv.re.srt", "uploads/Love.Is.Blind.Brazil.S01E01.Pod.of.Love.1080p.NF.WEB-DL.DUAL.DDP5.1.H.264-SMURFeztv.re_cn.srt", "uploads/Love.Is.Blind.Brazil.S01E01.Pod.of.Love.1080p.NF.WEB-DL.DUAL.DDP5.1.H.264-SMURFeztv.re_sn.srt"]
        self.output_folder = "unit_test_output"

        # # 创建测试文件和文件夹
        # os.makedirs(self.output_folder, exist_ok=True)
        # with open(self.video_path, 'w') as f:
        #     f.write("dummy video content")
        # for subtitle_path in self.subtitle_paths:
        #     with open(subtitle_path, 'w') as f:
        #         f.write("1\n00:00:00,000 --> 00:00:01,000\nTest subtitle\n")


    def test_merge_subtitles_with_video(self):
        output_path = merge_subtitles_with_video(self.video_path, self.subtitle_paths, self.output_folder)
        self.assertTrue(os.path.exists(output_path))
        self.assertTrue(output_path.endswith('.mkv'))

if __name__ == '__main__':
    unittest.main()