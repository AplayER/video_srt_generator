# video_srt_generator
为视频文件生成字幕，并内嵌到视频文件中

## 第一步
创建虚拟环境
'''
python3 -m venv env
'''

激活虚拟环境
'''
source env/bin/activate
'''

安装依赖项
'''
pip install -r requirements.txt
'''

## 第二步

运行服务

'''
env/bin/python app.py
'''

## 第三步
flask默认端口号为5000，去浏览器打开http://127.0.0.1:5000，就可以看到选择和上传按钮，选择文件之后，点击上传即可，接下来就是等着任务跑完就行了