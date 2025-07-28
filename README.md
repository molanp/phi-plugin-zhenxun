<div align="center">
  <h1>
    <picture>
      <source srcset="./image/fix.avif" type="image/avif" width="80%">
      <source srcset="./image/fix.webp" type="image/webp" width="80%">
      <img src="./image/fix.png" width="80%">
    </picture>
  </h1>

[![Stars](https://img.shields.io/github/stars/molanp/zhenxun_plugin_phi-plugin?style=flat-square&color=yellow&label=Star)](https://github.com/molanp/zhenxun_plugin_phi-plugin/stargazers)

![version](https://img.shields.io/badge/插件版本-0.1.0_beta-9cf?style=flat-square)
![phigros-version](https://img.shields.io/badge/Phigros-3.14.2-9cf?style=flat-square)  
[![zhenxun_bot](https://img.shields.io/badge/zhenxun_bot-latest-9cf?style=flat-square&logo=dependabot)](https://github.com/zhenxun-org/zhenxun_bot)

</div>

<details>
<summary>当前同步版本号</summary>

当前同步的版本

[faccd28f3466f7add05144c71715bd9d5a3efb41](https://github.com/Catrong/phi-plugin/commit/faccd28f3466f7add05144c71715bd9d5a3efb41)

[已落后的变更](https://github.com/Catrong/phi-plugin/compare/faccd28f3466f7add05144c71715bd9d5a3efb41...main)

</details>

## 长期寻求合作者共同开发

## 任务列表

- [x] 移植依赖
- [ ] 移植 `apiSetting`
- [x] 移植 `b19`
- [ ] 移植 `Dan`
- [x] 移植 `guessGame`
  - [x] 移植 `guessIll`
  - [x] 移植 `guessLetter`
  - [x] 移植 `guessTips`
- [x] 移植 `help`
- [x] 移植 `jrrp`
- [ ] 移植 `manage`
- [ ] 移植 `money`
- [ ] 移植 `phisong`
- [ ] 移植 `RankList`
- [x] 移植 `session`
- [ ] 移植 `setting`
- [ ] 移植 `user`
- [ ] 测试功能
- [ ] 整理代码逻辑
- [ ] 优化代码性能

### 介绍

`phi-plugin` 为查询 Phigros 信息的插件，包括 b30、score、userinfo 以及更多 Phigros 相关功能，有相关的建议和问题可以在[Issues](./issues)中提出，欢迎[PR](./pulls)。

具体功能可在安装插件后 通过 `/phi help` 查看详细指令

> **以下 `/phi` 为插件默认前缀，可以在配置文件(`/data/config.yaml`)中修改**
>
> 用户输入时，前缀和命令中间的空格**不是必需的**
>
> 括号内斜杠分隔的命令表示别名

## 📚 插件功能

#### **以下为用户功能**

| **功能名称**                                                          | **功能说明**                                                                                                    |
| :-------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------- |
| `/phi帮助`                                                            | 获取帮助                                                                                                        |
| `/phi (bind\|绑定)xxx`                                                | 绑定 sessionToken                                                                                               |
| `/phi (unbind\|解绑)`                                                 | 删除 sessionToken 和存档记录                                                                                    |
| `/phi clean`                                                          | 删除所有记录                                                                                                    |
| `/phi (update\|更新存档)`                                             | 更新存档                                                                                                        |
| `/phi (rks\|pgr\|b30)`                                                | 查询 rks，会提供得出的 b30 结果                                                                                 |
| `杠批比三零`                                                          | 同上                                                                                                            |
| `/phi info(1\|2)?`                                                    | 查询个人统计信息                                                                                                |
| `/phi lmtacc [0-100]`                                                 | 计算限制最低 ACC 后的 RKS                                                                                       |
| `/phi (lvsco(re)\|scolv) <定数范围> <难度>`                           | 获取区间成绩                                                                                                    |
| `/phi chap <章节名称\|help>`                                          | 获取章节成绩                                                                                                    |
| `/phi list <定数范围> <EZ\|HD\|IN\|AT> <NEW\|C\|B\|A\|S\|V\|FC\|PHI>` | 获取区间每首曲目的成绩                                                                                          |
| `/phi best1(+)`                                                       | 查询文字版 b30（或更多），最高 b99                                                                              |
| `/phi (score\|单曲成绩)xxx`                                           | 获取单曲成绩及这首歌的推分建议                                                                                  |
| `/phi (suggest\|推分)`                                                | 获取可以让 RKS+0.01 的曲目及其所需 ACC                                                                          |
| `/phi (ranklist\|排行榜)`                                             | 获取 RKS 排行榜                                                                                                 |
| `/phi data`                                                           | 获取用户 data 数量                                                                                              |
| `/phi (guess\|猜曲绘)`                                                | 猜曲绘，回答无特殊命令，直接回复，如果不是曲名就不会说话，如果是不正确的曲名会回复。#ans 结束                   |
| `/phi (ltr\|开字母)`                                                  | 根据字母猜曲名，`/phi 出` `/phi open`... 开指定的字母，`/phi 第n个` `/phi nX.xxx` 进行回答，`/phi ans` 获取答案 |
| `/phi (tipgame\|提示猜曲)`                                            | 根据提示猜曲名，#tip 获得下一条提示，#ans 获取答案，回答直接回复                                                |
| `/phi (song\|曲) xxx`                                                 | 查询 phigros 中某一曲目的图鉴，支持设定别名                                                                     |
| `/phi (table\|定数表) <定数>`                                         | 查询 phigros 定数表（B 站[@yuhao7370](space.bilibili.com/275661582)）                                           |
| `/phi new`                                                            | 查询更新的曲目                                                                                                  |
| `/phi tips`                                                           | 随机 tips                                                                                                       |
| `/phi jrrp`                                                           | 今日人品                                                                                                        |
| `/phi nick xxx`                                                       | 查询某一曲目的别名                                                                                              |
| `/phi (rand\|随机) [定数] [难度]`                                     | 根据条件随机曲目，条件支持难度、定数，难度可以多选，定数以-作为分隔                                             |
| `/phi randclg [课题总值] [难度] ([曲目定数范围])`                     | 随机课题 eg: /rand 40 (IN 13-15)                                                                                |
| `/phi (曲绘\|ill\|Ill) xxx`                                           | 查询 phigros 中某一曲目的曲绘                                                                                   |
| `/phi (search\|查询\|检索) <条件 值>`                                 | 检索曲库中的曲目，支持 BPM 定数 物量，条件 bpm dif cmb，值可以为区间，以 - 间隔                                 |
| `/phi (theme\|主题) [0-2]`                                            | 切换绘图主题，仅对 b30, update, randclg, sign, task 生效                                                        |
| `/phi sign/签到`                                                      | 签到获取 Notes                                                                                                  |
| `/phi task/我的任务`                                                  | 查看自己的任务                                                                                                  |
| `/phi retask/刷新任务`                                                | 刷新任务，需要花费 20Notes                                                                                      |
| `/phi (send\|送\|转) <目标> <数量>`                                   | 送给目标 Note，支持@或 QQ 号                                                                                    |

#### **以下为管理功能**

| 功能名称                               | 功能说明                                                                                             |
| :------------------------------------- | :--------------------------------------------------------------------------------------------------- |
| `/phi backup (back)?`                  | 备份存档文件，+ back 发送该备份文件，自动保存在 /phi-plugin/backup/ 目录下                           |
| `/phi restore`                         | 从备份中还原，不会丢失已有数据，需要将文件放在 /phi-plugin/backup/ 目录下                            |
| `/phi(设置别名\|setnick) xxx ---> xxx` | 设置某一歌曲的别名，格式为 原名(或已有别名) ---> 别名（会自动过滤--->两边的空格）                    |
| `/phi(删除别名\|delnick) xxx`          | 删除某一歌曲的别名                                                                                   |
| `/phi(强制\|qz)?(更新\|gx)`            | 更新本插件                                                                                           |
| `/phi repu`                            | 重启 puppeteer                                                                                       |
| `/phi 下载曲绘\|downill`               | 下载曲绘到本地                                                                                       |
| `/phi get <名次>`                      | 获取排行榜上某一名次的 sessionToken                                                                  |
| `/phi del <sessionToken>`              | 禁用某一 sessionToken                                                                                |
| `/phi allow <sessionToken>`            | 恢复某一 sessionToken                                                                                |
| `/phi (set\|设置)<功能><值>`           | 修改设置，建议先/phi set 查看功能名称，没有空格                                                      |
| `/phi ban <功能>`                      | 禁用某一类功能，详见 [功能参数说明](/phi-ban-%E5%8A%9F%E8%83%BD%E5%8F%82%E6%95%B0%E8%AF%B4%E6%98%8E) |

<details open>  
<summary>功能参数说明</summary>

#### `/phi ban` 功能参数说明

| 参数      | 功能                         | 影响指令                                                    |
| :-------- | :--------------------------- | :---------------------------------------------------------- |
| 全部      | 全部功能                     | 所有                                                        |
| help      | 帮助功能                     | /help /tkhelp                                               |
| bind      | 绑定功能                     | /bind /unbind                                               |
| b19       | 图片查分功能                 | /pgr /update /info /list /pb30 /score /lvsco /chap /suggest |
| wb19      | 文字查分功能                 | /data /best                                                 |
| song      | 图鉴功能                     | /song /ill /search /alias /rand /randclg /table             |
| ranklist  | 排行榜功能，不会禁用用户排名 | /ranklist /godlist                                          |
| fnc       | 小功能                       | /com /tips /lmtacc /new                                     |
| tipgame   | tip 猜歌                     | /tipgame                                                    |
| guessgame | 猜歌                         | /guess                                                      |
| ltrgame   | 猜字母                       | /letter /ltr                                                |
| sign      | 娱乐功能                     | /sign /send /task /retask /jrrp                             |
| setting   | 系统设置                     | /theme                                                      |
| dan       | 段位认证相关                 | /dan /danupdate                                             |

</details>

---

### 部分功能预览

| **Best30 效果图**<br><picture><source srcset="https://github.com/user-attachments/assets/470946e9-60ae-49ab-b901-0158039061b3" type="image/avif" width="80%" /><img src="https://github.com/user-attachments/assets/470946e9-60ae-49ab-b901-0158039061b3" width="80%" /></picture> | **单曲成绩效果图**<br><picture><source srcset="" type="image/avif" width="40%" /><img src="" width="40%"></picture><br><br>**单曲成绩效果图（Legacy）**<br><picture><source srcset="" type="image/avif" width="40%" /><img src="" width="40%"></picture><br><br>**单曲图鉴效果图**<br><picture><source srcset="" type="image/avif" width="40%" /><img src="" width="40%"></picture> |
| :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: |
|                                        **范围成绩效果图**<br><picture><source srcset="" type="image/avif" /><img src=""></picture><br> <br><br>**个人信息效果图**<br><picture><source srcset="" type="image/avif" /><img src=""></picture>                                         |                                                                                                                          **个人信息效果图（Legacy）**<br><picture><source srcset="" type="image/avif" width="60%" /><img src="" width="60%"></picture><br>                                                                                                                          |

---

## 💕 感谢

- [phi-plugin](https://github.com/Catrong/phi-plugin) 适用于 Yunzai-Bot V3 的 phigros 辅助插件，支持查询分数信息等功能，以及猜曲目等小游戏
- [@Windows10555](https://github.com/Windows10555) 图片后期处理
