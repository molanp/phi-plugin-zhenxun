# zhenxun_plugin_phi-plugin
适用于 zhenxun_bot 的 phigros 辅助插件，支持查询分数信息等功能，以及猜曲目等小游戏

<details>
<summary>当前同步版本号</summary>
2025-05-06T14:52:11.000Z

[8660e28b65110b5fc30fe86e2a6cdee89d773a94](https://github.com/Catrong/phi-plugin/commit/8660e28b65110b5fc30fe86e2a6cdee89d773a94)

[已落后的变更](https://github.com/Catrong/phi-plugin/compare/8660e28b65110b5fc30fe86e2a6cdee89d773a94...main)
</details>

# 插件正在火热开发中...

## 📚 插件功能

#### **以下为用户功能**

| **功能名称** | **功能说明**
| :- | :-
| `phi 帮助` | 获取帮助
| `phi (bind\|绑定)xxx` | 绑定sessionToken
| `phi (unbind\|解绑)` | 删除sessionToken和存档记录
| `phi clean` | 删除所有记录
| `phi (update\|更新存档)` | 更新存档
| `phi (rks\|pgr\|b30)` | 查询rks，会提供得出的b30结果
| `杠批比三零` | 同上
| `phi info(1\|2)?` | 查询个人统计信息
| `phi lmtacc [0-100]` | 计算限制最低 ACC 后的 RKS
| `phi (lvsco(re)\|scolv) <定数范围> <难度>` | 获取区间成绩
| `phi chap <章节名称\|help>` | 获取章节成绩
| `phi list <定数范围> <EZ\|HD\|IN\|AT> <NEW\|C\|B\|A\|S\|V\|FC\|PHI>` | 获取区间每首曲目的成绩
| `phi best1(+)` | 查询文字版b30（或更多），最高b99
| `phi (score\|单曲成绩)xxx` | 获取单曲成绩及这首歌的推分建议
| `phi (suggest\|推分)` | 获取可以让RKS+0.01的曲目及其所需ACC
| `phi (ranklist\|排行榜)` | 获取 RKS 排行榜
| `phi data` | 获取用户data数量
| `phi (guess\|猜曲绘)` | 猜曲绘，回答无特殊命令，直接回复，如果不是曲名就不会说话，如果是不正确的曲名会回复。#ans 结束
| `phi (ltr\|开字母)` | 根据字母猜曲名，#出/#open... 开指定的字母，#第n个/#nX.xxx 进行回答，#ans 获取答案
| `phi (tipgame\|提示猜曲)` | 根据提示猜曲名，#tip获得下一条提示，#ans 获取答案，回答直接回复
| `phi (song\|曲) xxx` | 查询phigros中某一曲目的图鉴，支持设定别名
| `phi (table\|定数表) <定数>` | 查询phigros定数表（B站[@yuhao7370](space.bilibili.com/275661582)）
| `phi new` | 查询更新的曲目
| `phi tips` | 随机tips
| `phi jrrp` | 今日人品
| `phi alias xxx` | 查询某一曲目的别名
| `phi (rand\|随机) [定数] [难度]` | 根据条件随机曲目，条件支持难度、定数，难度可以多选，定数以-作为分隔
| `phi randclg [课题总值] [难度] ([曲目定数范围])` | 随机课题 eg: /rand 40 (IN 13-15)
| `phi (曲绘\|ill\|Ill) xxx` | 查询phigros中某一曲目的曲绘
| `phi (search\|查询\|检索) <条件 值>` | 检索曲库中的曲目，支持BPM 定数 物量，条件 bpm dif cmb，值可以为区间，以 - 间隔
| `phi (theme\|主题) [0-2]` | 切换绘图主题，仅对 b30, update, randclg, sign, task 生效
| `sign/签到` | 签到获取Notes
| `task/我的任务` | 查看自己的任务
| `retask/刷新任务` | 刷新任务，需要花费20Notes
| `phi (send\|送\|转) <目标> <数量>` | 送给目标Note，支持@或QQ号

#### **以下为管理功能**

| 功能名称 | 功能说明
| :- | :-
| `phi backup (back)?` | 备份存档文件，+ back 发送该备份文件，自动保存在 /phi-plugin/backup/ 目录下
| `phi restore` | 从备份中还原，不会丢失已有数据，需要将文件放在 /phi-plugin/backup/ 目录下
| `phi(设置别名\|setnick) xxx ---> xxx` | 设置某一歌曲的别名，格式为 原名(或已有别名) ---> 别名（会自动过滤--->两边的空格）
| `phi(删除别名\|delnick) xxx` | 删除某一歌曲的别名
| `phi(强制\|qz)?(更新\|gx)` | 更新本插件
| `phi repu` | 重启puppeteer
| `#下载曲绘\|down ill` | 下载曲绘到本地
| `phi get <名次>` | 获取排行榜上某一名次的sessionToken
| `phi del <sessionToken>` | 禁用某一sessionToken
| `phi allow <sessionToken>` | 恢复某一sessionToken
| `phi (set\|设置)<功能><值>` | 修改设置，建议先/phi set查看功能名称，没有空格
| `phi ban <功能>` | 禁用某一类功能，详见 [功能参数说明](phi-ban-%E5%8A%9F%E8%83%BD%E5%8F%82%E6%95%B0%E8%AF%B4%E6%98%8E)

<details open>  
<summary>功能参数说明</summary>

#### `phi ban` 功能参数说明以下#均可用/代替，命令头可自定义

#### **以下为用户功能**

| **功能名称** | **功能说明**
| :- | :-
| `phi帮助` | 获取帮助
| `phi (bind\|绑定)xxx` | 绑定sessionToken
| `phi (unbind\|解绑)` | 删除sessionToken和存档记录
| `phi clean` | 删除所有记录
| `phi (update\|更新存档)` | 更新存档
| `phi (rks\|pgr\|b30)` | 查询rks，会提供得出的b30结果
| `杠批比三零` | 同上
| `phi info(1\|2)?` | 查询个人统计信息
| `phi lmtacc [0-100]` | 计算限制最低 ACC 后的 RKS
| `phi (lvsco(re)\|scolv) <定数范围> <难度>` | 获取区间成绩
| `phi chap <章节名称\|help>` | 获取章节成绩
| `phi list <定数范围> <EZ\|HD\|IN\|AT> <NEW\|C\|B\|A\|S\|V\|FC\|PHI>` | 获取区间每首曲目的成绩
| `phi best1(+)` | 查询文字版b30（或更多），最高b99
| `phi (score\|单曲成绩)xxx` | 获取单曲成绩及这首歌的推分建议
| `phi (suggest\|推分)` | 获取可以让RKS+0.01的曲目及其所需ACC
| `phi (ranklist\|排行榜)` | 获取 RKS 排行榜
| `phi data` | 获取用户data数量
| `phi (guess\|猜曲绘)` | 猜曲绘，回答无特殊命令，直接回复，如果不是曲名就不会说话，如果是不正确的曲名会回复。#ans 结束
| `phi (ltr\|开字母)` | 根据字母猜曲名，#出/#open... 开指定的字母，#第n个/#nX.xxx 进行回答，#ans 获取答案
| `phi (tipgame\|提示猜曲)` | 根据提示猜曲名，#tip获得下一条提示，#ans 获取答案，回答直接回复
| `phi (song\|曲) xxx` | 查询phigros中某一曲目的图鉴，支持设定别名
| `#phi (comment\|cmt\|评论\|评价) <曲名> <难度?>(换行)<内容>` | 评论曲目，难度默认为IN
| `#phi recmt <评论ID>` | 查看并确认是否删评，仅发送者和主人权限，需要二次确认
| `phi (table\|定数表) <定数>` | 查询phigros定数表（B站[@yuhao7370](space.bilibili.com/275661582)）
| `phi new` | 查询更新的曲目
| `phi tips` | 随机tips
| `phi jrrp` | 今日人品
| `phi nick xxx` | 查询某一曲目的别名
| `phi (rand\|随机) [定数] [难度]` | 根据条件随机曲目，条件支持难度、定数，难度可以多选，定数以-作为分隔
| `phi randclg [课题总值] [难度] ([曲目定数范围])` | 随机课题 eg: /rand 40 (IN 13-15)
| `phi (曲绘\|ill\|Ill) xxx` | 查询phigros中某一曲目的曲绘
| `phi (search\|查询\|检索) <条件 值>` | 检索曲库中的曲目，支持BPM 定数 物量，条件 bpm dif cmb，值可以为区间，以 - 间隔
| `phi (theme\|主题) [0-2]` | 切换绘图主题，仅对 b30, update, randclg, sign, task 生效

#### **以下为管理功能**

| 功能名称 | 功能说明
| :- | :-
| `phi(设置别名\|setnick) xxx ---> xxx` | 设置某一歌曲的别名，格式为 原名(或已有别名) ---> 别名（会自动过滤--->两边的空格）
| `phi(删除别名\|delnick) xxx` | 删除某一歌曲的别名
| `phi(强制\|qz)?(更新\|gx)` | 更新本插件
| `#下载曲绘\|down ill` | 下载曲绘到本地
| `phi get <名次>` | 获取排行榜上某一名次的sessionToken
| `phi del <sessionToken>` | 禁用某一sessionToken
| `phi allow <sessionToken>` | 恢复某一sessionToken
| `phi ban <功能>` | 禁用某一类功能，详见 [功能参数说明](phi-ban-%E5%8A%9F%E8%83%BD%E5%8F%82%E6%95%B0%E8%AF%B4%E6%98%8E)

<details open>  
<summary>功能参数说明</summary>

#### `phi ban` 功能参数说明

| 参数 | 功能 | 影响指令
| :- | :- | :-
| 全部 | 全部功能 | 所有
| help | 帮助功能 | /help /tkhelp
| bind | 绑定功能 | /bind /unbind
| b19 | 图片查分功能 | /pgr /update /info /list /pb30 /score /lvsco /chap /suggest
| wb19 | 文字查分功能 | /data /best
| song | 图鉴功能 | /song /ill /search /alias /rand /randclg /table /cmt /recmt
| ranklist | 排行榜功能，不会禁用用户排名 | /ranklist /godlist
| fnc | 小功能 | /com /tips /lmtacc /new
| tipgame | tip猜歌 | /tipgame
| guessgame | 猜歌 | /guess
| ltrgame | 猜字母 | /letter /ltr
| sign | 娱乐功能 | /sign /send /task /retask /jrrp
| setting | 系统设置 | /theme
| dan | 段位认证相关 | /dan /danupdate
</details>


## 💕 感谢
- [phi-plugin](https://github.com/Catrong/phi-plugin) 适用于 Yunzai-Bot V3 的 phigros 辅助插件，支持查询分数信息等功能，以及猜曲目等小游戏