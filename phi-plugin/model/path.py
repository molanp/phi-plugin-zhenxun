from pathlib import Path

# 获取当前文件的绝对路径
current_file_path = Path(__file__).resolve()
pluginRoot = current_file_path.parent

pluginResources = pluginRoot / "resources"

# 曲绘资源、曲目信息路径
infoPath = pluginResources / "info"

# 额外曲目名称信息（开字母用）
DlcInfoPath = infoPath / "DLC"

# 上个版本曲目信息
oldInfoPath = infoPath / "oldInfo"

# 数据路径
dataPath = pluginRoot / "data"

# 用户存档数据路径
savePath = dataPath / "saveData"

# 默认图片路径
imgPath = pluginResources / "html" / "otherimg"

# 用户图片路径
ortherIllPath = pluginResources / "otherill"

# 原画资源
originalIllPath = pluginResources / "original_ill"

# 音频资源
guessMicPath = pluginResources / "splited_music"
