# import common from '../../../lib/common/common.js'
# import plugin from '../../../lib/plugins/plugin.js'
# import Config from '../components/Config.js';
# import get from '../model/getdata.js'
# import { segment } from "oicq";
# import send from '../model/send.js';
# import PhigrosUser from '../lib/PhigrosUser.js';
# import altas from '../model/picmodle.js'
# import scoreHistory from '../model/class/scoreHistory.js';
# import fCompute from '../model/fCompute.js';
# import getInfo from '../model/getInfo.js';
# import getSave from '../model/getSave.js';
# import { LevelNum } from '../model/constNum.js';
# import getNotes from '../model/getNotes.js';
# import getPic from '../model/getPic.js';
# import getBanGroup from '../model/getBanGroup.js';
# import makeRequest from '../model/makeRequest.js';
# import makeRequestFnc from '../model/makeRequestFnc.js';
# import getSaveFromApi from '../model/getSaveFromApi.js';
import math
import random
import re

from nonebot_plugin_alconna import Alconna, Args, Arparma, on_alconna
from nonebot_plugin_uninfo import Uninfo

from ..config import PluginConfig
from ..model.fCompute import fCompute
from ..model.getBanGroup import getBanGroup
from ..model.getdata import getdata
from ..model.getInfo import getInfo
from ..model.getNotes import getNotes
from ..model.picmodle import picmodle
from ..model.send import send
from ..utils import to_dict

ChallengeModeName = ["白", "绿", "蓝", "红", "金", "彩"]

Level = ["EZ", "HD", "IN", "AT", None]  # 存档的难度映射
cmdhead = re.escape(PluginConfig.get("cmdhead"))

b19 = on_alconna(
    Alconna(rf"re:{cmdhead}\s*(b|rks|pgr|PGR|B|RKS)", Args["nnum", int, 33]),
    block=True,
    priority=5,
)

p30 = on_alconna(
    Alconna(rf"re:{cmdhead}\s*(p|P)", Args["nnum", int, 33]),
    block=True,
    priority=5,
)
arcgrosB19 = on_alconna(
    Alconna(
        rf"re:{cmdhead}\s*(a|arc|啊|阿|批|屁|劈)\s*((b|B)|[比必币])",
        Args["nnum", int, 32],
    ),
    block=True,
    priority=5,
)

lmtAcc = on_alconna(
    Alconna(rf"re:{cmdhead}\s*lmtacc", Args["nnum", float]),
    block=True,
    priority=5,
)

singlescore = on_alconna(
    Alconna(rf"re:{cmdhead}\s*(score|单曲成绩)", Args["song", str]),
    block=True,
    priority=5,
)

suggest = on_alconna(
    Alconna(rf"re:{cmdhead}\s*(suggest|推分(建议)?)", Args["rks", float]),
    block=True,
    priority=5,
)

chap = on_alconna(
    Alconna(rf"re:{cmdhead}\s*chap", Args["song", str, "help"]),
    block=True,
    priority=5,
)


@b19.handle()
async def _(session: Uninfo, params: Arparma):
    if await getBanGroup.get(b19, session, "b19"):
        await send.sendWithAt(b19, "这里被管理员禁止使用这个功能了呐QAQ！")
        return
    save = await send.getsaveResult(b19, session)
    if not save:
        return
    if err := await save.checkNoInfo():
        await send.sendWithAt(
            b19, "以下曲目无信息，可能导致b19显示错误\n" + "".join(err)
        )
    nnum = params.query("nnum") or 33
    nnum = max(nnum, 33)
    nnum = min(nnum, PluginConfig.get("B19MaxNum"))
    # 因响应器限制，暂时无法实现匹配中间消息(bksong)(取消息不可预料)
    plugin_data = await getNotes.getNotesData(session.user.id)
    if not PluginConfig.get("isGuild"):
        await send.sendWithAt(
            b19, "正在生成图片，请稍等一下哦！\n//·/w\\·\\\\", recallTime=5
        )
    save_b19 = await save.getB19(nnum)
    stats = await save.getStats()
    money = save.gameProgress.money
    gameuser = {
        "avatar": await getdata.idgetsong(save.gameuser.avatar) or "Introduction",
        "ChallengeMode": math.floor(save.saveInfo.summary.challengeModeRank / 100),
        "ChallengeModeRank": save.saveInfo.summary.challengeModeRank % 100,
        "rks": save.saveInfo.summary.rankingScore,
        "data": "".join(
            [
                f"{v}{u} "
                for v, u in zip(money, ["KiB", "MiB", "GiB", "TiB", "PiB"])
                if v
            ]
        ),
        "PlayerId": fCompute.convertRichText(save.saveInfo.PlayerId),
    }
    data = {
        "phi": save_b19["phi"],
        "b19_list": save_b19["b19_list"],
        "Date": save.saveInfo.summary.updatedAt,
        "background": await getInfo.getill(random.choice(getInfo.illlist)),
        "theme": plugin_data.plugin_data.theme,
        "gameuser": gameuser,
        "stats": stats,
    }
    res: list = [await picmodle.b19(to_dict(data))]
    if abs(save_b19.get("com_rks", 0) - save.saveInfo.summary.rankingScore) > 0.1:  # type: ignore
        res.append(
            f"请注意，当前版本可能更改了计算规则\n计算rks: {save_b19['com_rks']}\n"
            f"存档rks:{save.saveInfo.summary.rankingScore}"
        )
    await send.sendWithAt(b19, res)


#     /**P30 */
#     async p30(e) {

#         if (await getBanGroup.get(e, 'p30')) {
#             send.send_with_At(e, '这里被管理员禁止使用这个功能了呐QAQ！')
#             return false
#         }

#         let save = await send.getsave_result(e)
#         if (!save) {
#             return true
#         }

#         let err = save.checkNoInfo()

#         if (err.length) {
#             send.send_with_At(e, "以下曲目无信息，可能导致b19显示错误\n" + err.join('\n'))
#         }


#         let nnum = e.msg.match(/(p|P)[0-9]*/g)[0]

#         nnum = Number(nnum.replace(/(p|P)/g, ''))
#         if (!nnum) {
#             nnum = 33
#         }

#         nnum = Math.max(nnum, 33)
#         nnum = Math.min(nnum, Config.getUserCfg('config', 'B19MaxNum'))

#         let bksong = e.msg.replace(/^.*(p|P)[0-9]*\s*/g, '')

#         if (bksong) {
#             let tem = get.fuzzysongsnick(bksong)[0]
#             if (tem) {
#                 // console.info(tem)
#                 bksong = get.getill(tem, 'blur')
#             } else {
#                 bksong = undefined
#             }
#         }

#         let plugin_data = await getNotes.getNotesData(e.user_id)


#         if (!Config.getUserCfg('config', 'isGuild'))
#             e.reply("正在生成图片，请稍等一下哦！\n//·/w\\·\\\\", false, { recallMsg: 5 })

#         try {
#             await get.buildingRecord(e, new PhigrosUser(save.session))

#             save = await send.getsave_result(e)

#             if (!save) {
#                 return true
#             }

#         } catch (err) {
#             send.send_with_At(e, err)
#             logger.error(err)
#         }

#         let save_b19 = await save.getBestWithLimit(nnum, [{ type: 'acc', value: [100, 100] }])
#         let stats = await save.getStats()


#         let dan = await get.getDan(e.user_id)
#         let money = save.gameProgress.money
#         let gameuser = {
#             avatar: get.idgetavatar(save.gameuser.avatar) || 'Introduction',
#             ChallengeMode: Math.floor(save.saveInfo.summary.challengeModeRank / 100),
#             ChallengeModeRank: save.saveInfo.summary.challengeModeRank % 100,
#             rks: save_b19.com_rks,
#             data: `${money[4] ? `${money[4]}PiB ` : ''}${money[3] ? `${money[3]}TiB ` : ''}${money[2] ? `${money[2]}GiB ` : ''}${money[1] ? `${money[1]}MiB ` : ''}${money[0] ? `${money[0]}KiB ` : ''}`,
#             selfIntro: save.gameuser.selfIntro,
#             backgroundUrl: await fCompute.getBackground(save.gameuser.background),
#             PlayerId: fCompute.convertRichText(save.saveInfo.PlayerId),
#             dan: dan,
#         }

#         let data = {
#             phi: save_b19.phi,
#             b19_list: save_b19.b19_list,
#             PlayerId: gameuser.PlayerId,
#             Rks: save_b19.com_rks.toFixed(4),
#             Date: save.saveInfo.summary.updatedAt,
#             ChallengeMode: Math.floor(save.saveInfo.summary.challengeModeRank / 100),
#             ChallengeModeRank: save.saveInfo.summary.challengeModeRank % 100,
#             dan: await get.getDan(e.user_id),
#             background: bksong || getInfo.getill(getInfo.illlist[Number((Math.random() * (getInfo.illlist.length - 1)).toFixed(0))], 'blur'),
#             theme: plugin_data?.plugin_data?.theme || 'star',
#             gameuser,
#             nnum,
#             stats,
#             spInfo: "All Perfect Only Mode",
#         }

#         let res = [await altas.b19(e, data)]
#         if (Math.abs(save_b19.com_rks - save.saveInfo.summary.rankingScore) > 0.1) {
#             res.push(`计算rks: ${save_b19.com_rks}\n存档rks: ${save.saveInfo.summary.rankingScore}`)
#         }
#         send.send_with_At(e, res)
#     }

#     /**arc版查分图 */
#     async arcgrosB19(e) {

#         if (await getBanGroup.get(e, 'arcgrosB19')) {
#             send.send_with_At(e, '这里被管理员禁止使用这个功能了呐QAQ！')
#             return false
#         }

#         let save = await send.getsave_result(e)
#         if (!save) {
#             return true
#         }


#         let err = save.checkNoInfo()

#         if (err.length) {
#             send.send_with_At(e, "以下曲目无信息，可能导致b19显示错误\n" + err.join('\n'))
#         }


#         let nnum = e.msg.match(/(b|B)[0-9]*/g)
#         nnum = nnum ? Number(nnum[0].replace(/(b|B)/g, '')) - 1 : 32
#         if (!nnum) { nnum = 32 }

#         nnum = Math.max(nnum, 30)
#         nnum = Math.min(nnum, Config.getUserCfg('config', 'B19MaxNum'))

#         let save_b19 = await save.getB19(nnum)

#         let money = save.gameProgress.money
#         let gameuser = {
#             avatar: get.idgetavatar(save.gameuser.avatar) || 'Introduction',
#             ChallengeMode: Math.floor(save.saveInfo.summary.challengeModeRank / 100),
#             ChallengeModeRank: save.saveInfo.summary.challengeModeRank % 100,
#             rks: save.saveInfo.summary.rankingScore,
#             data: `${money[4] ? `${money[4]}PiB ` : ''}${money[3] ? `${money[3]}TiB ` : ''}${money[2] ? `${money[2]}GiB ` : ''}${money[1] ? `${money[1]}MiB ` : ''}${money[0] ? `${money[0]}KiB ` : ''}`,
#             selfIntro: save.gameuser.selfIntro,
#             backgroundUrl: await fCompute.getBackground(save.gameuser.background),
#             PlayerId: save.saveInfo.PlayerId,
#         }

#         let plugin_data = await getNotes.getNotesData(e.user_id)

#         let data = {
#             phi: save_b19.phi,
#             b19_list: save_b19.b19_list,
#             gameuser,
#             PlayerId: fCompute.convertRichText(save.saveInfo.PlayerId),
#             Rks: Number(save.saveInfo.summary.rankingScore).toFixed(4),
#             Date: save.saveInfo.summary.updatedAt,
#             ChallengeMode: Math.floor(save.saveInfo.summary.challengeModeRank / 100),
#             ChallengeModeRank: save.saveInfo.summary.challengeModeRank % 100,
#             dan: await get.getDan(e.user_id),
#             background: getInfo.getill(getInfo.illlist[Number((Math.random() * (getInfo.illlist.length - 1)).toFixed(0))], 'blur'),
#             theme: plugin_data?.plugin_data?.theme || 'star',
#             nnum: nnum,
#         }

#         send.send_with_At(e, await altas.arcgros_b19(e, data))
#     }

#     /**限制最低acc后的rks */
#     async lmtAcc(e) {
#         if (await getBanGroup.get(e, 'lmtAcc')) {
#             send.send_with_At(e, '这里被管理员禁止使用这个功能了呐QAQ！')
#             return false
#         }

#         let save = await send.getsave_result(e)
#         if (!save) {
#             return false
#         }

#         let err = save.checkNoInfo()

#         if (err.length) {
#             send.send_with_At(e, "以下曲目无信息，可能导致b19显示错误\n" + err.join('\n'))
#         }


#         let acc = Number(e.msg.replace(/^.*lmtacc\s*/g, ''))

#         if (!acc || acc < 0 || acc > 100) {
#             send.send_with_At(e, `我听不懂 ${e.msg.replace(/^.*lmtacc\s*/g, '')} 是多少喵！请指定一个0-100的数字喵！\n格式：/${Config.getUserCfg('config', 'cmdhead')} lmtAcc <0-100>`)
#             return false
#         }


#         let nnum = 33

#         let plugin_data = await get.getpluginData(e.user_id)


#         if (!Config.getUserCfg('config', 'isGuild'))
#             e.reply("正在生成图片，请稍等一下哦！\n//·/w\\·\\\\", false, { recallMsg: 5 })

#         let save_b19 = await save.getBestWithLimit(nnum, [{ type: 'acc', value: [acc, 100] }])
#         let stats = await save.getStats()


#         let dan = await get.getDan(e.user_id)
#         let money = save.gameProgress.money
#         let gameuser = {
#             avatar: get.idgetavatar(save.gameuser.avatar) || 'Introduction',
#             ChallengeMode: Math.floor(save.saveInfo.summary.challengeModeRank / 100),
#             ChallengeModeRank: save.saveInfo.summary.challengeModeRank % 100,
#             rks: save_b19.com_rks,
#             data: `${money[4] ? `${money[4]}PiB ` : ''}${money[3] ? `${money[3]}TiB ` : ''}${money[2] ? `${money[2]}GiB ` : ''}${money[1] ? `${money[1]}MiB ` : ''}${money[0] ? `${money[0]}KiB ` : ''}`,
#             selfIntro: save.gameuser.selfIntro,
#             backgroundUrl: await fCompute.getBackground(save.gameuser.background),
#             PlayerId: fCompute.convertRichText(save.saveInfo.PlayerId),
#             dan: dan,
#         }

#         let data = {
#             phi: save_b19.phi,
#             b19_list: save_b19.b19_list,
#             PlayerId: gameuser.PlayerId,
#             Rks: save_b19.com_rks.toFixed(4),
#             Date: save.saveInfo.summary.updatedAt,
#             ChallengeMode: Math.floor(save.saveInfo.summary.challengeModeRank / 100),
#             ChallengeModeRank: save.saveInfo.summary.challengeModeRank % 100,
#             dan: await get.getDan(e.user_id),
#             background: getInfo.getill(getInfo.illlist[Number((Math.random() * (getInfo.illlist.length - 1)).toFixed(0))], 'blur'),
#             theme: plugin_data?.plugin_data?.theme || 'star',
#             gameuser,
#             nnum,
#             stats,
#             spInfo: `ACC is limited to ${acc}%`,
#         }

#         let res = [await altas.b19(e, data)]
#         if (Math.abs(save_b19.com_rks - save.saveInfo.summary.rankingScore) > 0.1) {
#             res.push(`计算rks: ${save_b19.com_rks}\n存档rks: ${save.saveInfo.summary.rankingScore}`)
#         }
#         send.send_with_At(e, res)

#     }


#     async singlescore(e) {

#         if (await getBanGroup.get(e, 'singlescore')) {
#             send.send_with_At(e, '这里被管理员禁止使用这个功能了呐QAQ！')
#             return false
#         }

#         const save = await send.getsave_result(e)

#         if (!save) {
#             return true
#         }

#         let picversion = Number(e.msg.match(/(score|单曲成绩)[1-2]?/g)[0].replace(/(score|单曲成绩)/g, '')) || 1


#         let song = e.msg.replace(/[#/](.*?)(score|单曲成绩)[1-2]?(\s*)/g, '')

#         if (!song) {
#             send.send_with_At(e, `请指定曲名哦！\n格式：/${Config.getUserCfg('config', 'cmdhead')} score <曲名>`)
#             return true
#         }

#         if (!(get.fuzzysongsnick(song)[0])) {
#             send.send_with_At(e, `未找到 ${song} 的有关信息哦！`)
#             return true
#         }
#         song = get.fuzzysongsnick(song)
#         song = song[0]

#         let Record = save.gameRecord
#         let ans = Record[getInfo.SongGetId(song)]

#         if (!ans) {
#             send.send_with_At(e, `我不知道你关于[${song}]的成绩哦！可以试试更新成绩哦！\n格式：/${Config.getUserCfg('config', 'cmdhead')} update`)
#             return true
#         }

#         const dan = await get.getDan(e.user_id)

#         /**获取历史成绩 */

#         let HistoryData = null;
#         if (Config.getUserCfg('config', 'openPhiPluginApi')) {
#             try {
#                 HistoryData = await getSaveFromApi.getSongHistory(e, getInfo.SongGetId(song))
#             } catch (err) {
#                 logger.warn(`[phi-plugin] API ERR`, err)
#                 HistoryData = await getSave.getHistory(e.user_id)
#                 if (HistoryData) {
#                     HistoryData = HistoryData[get.SongGetId(song)]
#                 }
#             }
#         } else {
#             HistoryData = await getSave.getHistory(e.user_id)
#             if (HistoryData) {
#                 HistoryData = HistoryData[get.SongGetId(song)]
#             }
#         }


#         let history = []

#         if (HistoryData) {
#             for (let i in HistoryData) {
#                 for (let j in HistoryData[i]) {
#                     const tem = scoreHistory.extend(get.SongGetId(song), i, HistoryData[i][j])
#                     tem.date_new = fCompute.date_to_string(tem.date_new)
#                     history.push(tem)
#                 }
#             }
#         }

#         history.sort((a, b) => new Date(b.date_new) - new Date(a.date_new))

#         history.splice(16)


#         let data = {
#             songName: song,
#             PlayerId: save.saveInfo.PlayerId,
#             avatar: get.idgetavatar(save.saveInfo.summary.avatar),
#             Rks: Number(save.saveInfo.summary.rankingScore).toFixed(2),
#             Date: save.saveInfo.summary.updatedAt,
#             ChallengeMode: Math.floor(save.saveInfo.summary.challengeModeRank / 100),
#             ChallengeModeRank: save.saveInfo.summary.challengeModeRank % 100,
#             scoreData: {},
#             CLGMOD: dan?.Dan,
#             EX: dan?.EX,
#             history: history,
#         }


#         data.illustration = getInfo.getill(song)
#         let songsinfo = getInfo.info(song, true);

#         switch (picversion) {
#             case 2: {
#                 for (let i in ans) {
#                     if (ans[i]) {
#                         ans[i].acc = ans[i].acc.toFixed(2)
#                         ans[i].rks = ans[i].rks.toFixed(2)
#                         data[Level[i]] = {
#                             ...ans[i],
#                             suggest: save.getSuggest(getInfo.SongGetId(song), i, 4, songsinfo['chart'][Level[i]]['difficulty']),
#                         }
#                     } else {
#                         data[Level[i]] = {
#                             Rating: 'NEW'
#                         }
#                     }
#                     data[Level[i]].difficulty = Number(songsinfo['chart'][Level[i]]['difficulty']).toFixed(1)
#                 }
#                 send.send_with_At(e, await altas.score(e, data, 2))
#                 break;
#             }
#             default: {
#                 for (let i in Level) {
#                     if (!songsinfo.chart[Level[i]]) break
#                     data.scoreData[Level[i]] = {}
#                     data.scoreData[Level[i]].difficulty = songsinfo['chart'][Level[i]]['difficulty']
#                 }
#                 // console.info(ans)
#                 for (let i in ans) {
#                     if (!songsinfo['chart'][Level[i]]) break
#                     if (ans[i]) {
#                         ans[i].acc = ans[i].acc.toFixed(4)
#                         ans[i].rks = ans[i].rks.toFixed(4)
#                         data.scoreData[Level[i]] = {
#                             ...ans[i],
#                             suggest: save.getSuggest(getInfo.SongGetId(song), i, 4, songsinfo['chart'][Level[i]]['difficulty']),
#                         }
#                     } else {
#                         data.scoreData[Level[i]] = {
#                             Rating: 'NEW',
#                         }
#                     }
#                 }
#                 data.Rks = Number(save.saveInfo.summary.rankingScore).toFixed(4)
#                 send.send_with_At(e, await altas.score(e, data, 1))
#                 break;
#             }
#         }
#         return true

#     }

#     /**推分建议，建议的是RKS+0.01的所需值 */
#     async suggest(e) {

#         if (await getBanGroup.get(e, 'suggest')) {
#             send.send_with_At(e, '这里被管理员禁止使用这个功能了呐QAQ！')
#             return false
#         }

#         const save = await send.getsave_result(e)

#         if (!save) {
#             return true
#         }

#         /**处理范围要求 */
#         let { range, isask, scoreAsk } = fCompute.match_request(e.msg)

#         /**取出信息 */
#         let Record = save.gameRecord

#         /**计算 */
#         let data = []

#         for (let id in Record) {
#             let song = get.idgetsong(id)
#             if (!song) {
#                 logger.warn('[phi-plugin]', id, '曲目无信息')
#                 continue
#             }
#             let info = get.info(song, true)
#             let record = Record[id]
#             for (let lv in [0, 1, 2, 3]) {
#                 if (!info.chart[Level[lv]]) continue
#                 let difficulty = info.chart[Level[lv]].difficulty
#                 if (range[0] <= difficulty && difficulty <= range[1] && isask[lv]) {
#                     if ((!record[lv] && !scoreAsk.NEW)) continue
#                     if (record[lv] && !scoreAsk[record[lv].Rating.toUpperCase()]) continue
#                     if (!record[lv]) {
#                         record[lv] = {}
#                     }
#                     record[lv].suggest = save.getSuggest(id, lv, 4, difficulty)
#                     if (record[lv].suggest.includes('无')) {
#                         continue
#                     }
#                     data.push({ ...record[lv], ...info, illustration: get.getill(get.idgetsong(id), 'low'), difficulty: difficulty, rank: Level[lv] })
#                 }
#             }
#         }

#         if (data.length > Config.getUserCfg('config', 'listScoreMaxNum')) {
#             send.send_with_At(e, `谱面数量过多(${data.length})大于设置的最大值(${Config.getUserCfg('config', 'listScoreMaxNum')})，只显示前${Config.getUserCfg('config', 'listScoreMaxNum')}条！`)
#         }

#         data.splice(Config.getUserCfg('config', 'listScoreMaxNum'))

#         data = data.sort(cmpsugg())

#         let plugin_data = get.getpluginData(e.user_id)

#         send.send_with_At(e, await altas.list(e, {
#             head_title: "推分建议",
#             song: data,
#             background: get.getill(getInfo.illlist[fCompute.randBetween(0, getInfo.illlist.length - 1)]),
#             theme: plugin_data?.plugin_data?.theme || 'star',
#             PlayerId: save.saveInfo.PlayerId,
#             Rks: Number(save.saveInfo.summary.rankingScore).toFixed(4),
#             Date: save.saveInfo.summary.updatedAt,
#             ChallengeMode: Math.floor(save.saveInfo.summary.challengeModeRank / 100),
#             ChallengeModeRank: save.saveInfo.summary.challengeModeRank % 100,
#             dan: await get.getDan(e.user_id)
#         }))

#     }

#     /**查询章节成绩 */
#     async chap(e) {

#         if (await getBanGroup.get(e, 'chap')) {
#             send.send_with_At(e, '这里被管理员禁止使用这个功能了呐QAQ！')
#             return false
#         }
#         let msg = e.msg.replace(/^[#/].*chap\s*/, '').toUpperCase()
#         if (msg == 'HELP' || !msg) {
#             send.send_with_At(e, getPic.getimg('chapHelp'))
#             return true
#         }

#         let save = await send.getsave_result(e)
#         if (!save) {
#             return false
#         }

#         let chap = fCompute.fuzzySearch(msg, getInfo.chapNick)[0]?.value

#         if (!chap && msg != 'ALL') {
#             send.send_with_At(e, `未找到${msg}章节QAQ！可以使用 /${Config.getUserCfg('config', 'cmdhead')} chap help 来查询支持的名称嗷！`)
#             return false
#         }

#         let song_box = {}

#         /**统计各评分出现次数 */
#         let count = {
#             tot: 0,
#             phi: 0,
#             FC: 0,
#             V: 0,
#             S: 0,
#             A: 0,
#             B: 0,
#             C: 0,
#             F: 0,
#             NEW: 0
#         }

#         /**统计各难度出现次数 */
#         let rank = {
#             EZ: 0,
#             HD: 0,
#             IN: 0,
#             AT: 0
#         }

#         /**统计各难度ACC和 */
#         let rankAcc = {
#             EZ: 0,
#             HD: 0,
#             IN: 0,
#             AT: 0
#         }

#         for (let song in getInfo.ori_info) {
#             if (getInfo.ori_info[song].chapter == chap || msg == 'ALL') {
#                 song_box[song] = { illustration: getInfo.getill(song, 'low'), chart: {} }
#                 let id = getInfo.idssong[song]
#                 /**曲目成绩对象 */
#                 let songRecord = save.getSongsRecord(id)
#                 let info = getInfo.info(song, true)
#                 for (let level in info.chart) {
#                     let i = LevelNum[level]
#                     /**跳过旧谱 */
#                     if (!level) continue
#                     let Record = songRecord[i]
#                     song_box[song].chart[level] = {
#                         difficulty: info.chart[level].difficulty,
#                         Rating: Record?.Rating || 'NEW',
#                         suggest: save.getSuggest(id, i, 4, info.chart[level].difficulty)
#                     }
#                     if (Record) {
#                         song_box[song].chart[level].score = Record.score
#                         song_box[song].chart[level].acc = Record.acc.toFixed(4)
#                         song_box[song].chart[level].rks = Record.rks.toFixed(4)
#                         song_box[song].chart[level].fc = Record.fc
#                     }
#                     ++count.tot
#                     if (Record?.Rating) {
#                         ++count[Record.Rating]
#                         rankAcc[level] += Number(Record.acc || 0)
#                     } else {
#                         ++count.NEW
#                     }
#                     ++rank[level]
#                 }
#             }
#         }

#         let progress = {}
#         for (let level in rank) {
#             if (rank[level]) {
#                 progress[level] = rankAcc[level] / rank[level]
#             }
#         }

#         send.send_with_At(e, await altas.chap(e, {
#             player: { id: save.saveInfo.PlayerId },
#             count,
#             song_box,
#             progress,
#             num: rank.EZ,
#             chapName: msg == 'ALL' ? 'AllSong' : chap,
#             chapIll: getInfo.getChapIll(msg == 'ALL' ? 'AllSong' : chap),
#         }))

#     }
# }

# function cmp() {
#     return function (a, b) {
#         return b.rks - a.rks
#     }
# }

# function cmpsugg() {
#     return function (a, b) {
#         function com(difficulty, suggest) {
#             return difficulty + Math.min(suggest - 98, 1) * Math.min(suggest - 98, 1) * difficulty * 0.089
#         }
#         let s_a = Number(a.suggest.replace("%", ''))
#         let s_b = Number(b.suggest.replace("%", ''))
#         return com(a.difficulty, s_a) - com(b.difficulty, s_b)
#         // return (Number(a.suggest.replace("%", '')) - a.rks) - (Number(b.suggest.replace("%", '')) - b.rks)
#     }
# }


# function comRecord(a, b) {
#     return Number(a.acc).toFixed(4) == Number(b.acc).toFixed(4) && Number(a.score) == Number(b.score) && Number(a.rks) == Number(b.rks)
# }
