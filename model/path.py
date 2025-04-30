from zhenxun.configs.path_config import DATA_PATH

from ..config import PATH

# /**插件资源目录 */
pluginResources = PATH / "resources"

# /**曲绘资源、曲目信息路径 */
infoPath = pluginResources / "info"

# /**额外曲目名称信息（开字母用） */
DlcInfoPath = pluginResources / "info" / "DLC"

# /**上个版本曲目信息 */
oldInfoPath = pluginResources / "info" / "oldInfo"

# /**数据路径 */
dataPath = DATA_PATH / "phi-plugin"

# // userPath = `E:/bot/233/Miao-Yunzai/plugins/phi-plugin/data/`

# /**用户娱乐数据路径 */
pluginDataPath = dataPath / "pluginData"

# /**用户存档数据路径 */
savePath = dataPath / "saveData"

# /**用户设置路径 */
configPath = dataPath / "config"

# /**默认图片路径 */
imgPath = pluginResources / "html" / "otherimg"

# /**用户图片路径 */
ortherIllPath = pluginResources / "otherill"

# /**原画资源 */
originalIllPath = pluginResources / "original_ill"

# /**音频资源 */
guessMicPath = pluginResources / "splited_music"

# /**备份路径 */
backupPath = dataPath / "backup"
