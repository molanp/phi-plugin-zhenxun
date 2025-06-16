# import plugin from '../../../lib/plugins/plugin.js'
# import Config from '../components/Config.js'
# import send from '../model/send.js'
# import get from '../model/getdata.js'
# import picmodle from '../model/picmodle.js'
# import getFile from '../model/getFile.js'
# import path from 'path'
# import { infoPath } from '../model/path.js'
# import getBanGroup from '../model/getBanGroup.js';
from nonebot_plugin_alconna import Alconna, on_alconna

from ..config import PluginConfig
from ..model.getBanGroup import getBanGroup
from ..model.getdata import getdata
from ..model.path import infoPath
from ..model.picmodle import picmodle
from ..model.send import send

cmdhead = PluginConfig.get("cmdhead")

help = on_alconna(
    Alconna(
        fr"r:{cmdhead}\s+(命令|帮助|菜单|help|说明|功能|指令|使用说明)",
    ),
    priority=5,
    block=True,
)
tkhelp = on_alconna(
    Alconna(
        fr"r:{cmdhead}\s+tok(?:en)?(命令|帮助|菜单|help|说明|功能|指令|使用说明)",
    ),
    priority=5,
    block=True,
)
apihelp = on_alconna(
    Alconna(
        fr"r:{cmdhead}\s+api(命令|帮助|菜单|help|说明|功能|指令|使用说明)",
    ),
    priority=5,
    block=True,
)

@help.handle()
async def _(event):
    if await getBanGroup.get(event, "help"):
        await send.send_with_At(event, "这里被管理员禁止使用这个功能了呐QAQ！")
        return
    await send
# const helpGroup = await getFile.FileReader(path.join(infoPath, 'help.json'))
# const apiHelp = await getFile.FileReader(path.join(infoPath, 'help', 'api.json'))


# export class phihelp extends plugin {
#     async help(e) {

#         if (await getBanGroup.get(e, 'help')) {
#             send.send_with_At(e, '这里被管理员禁止使用这个功能了呐QAQ！')
#             return false
#         }

#         let head = Config.getUserCfg('config', 'cmdhead')
#         head = head.match(RegExp(head))[0]
#         let pluginData = await get.getpluginData(e.user_id)
#         e.reply(await picmodle.help(e, {
#             helpGroup: helpGroup,
#             cmdHead: head || null,
#             isMaster: e.isMaster,
#             background: get.getill(get.illlist[Math.floor((Math.random() * (get.illlist.length - 1)))]),
#             theme: pluginData?.plugin_data?.theme || 'star'
#         }), true)
#         return true
#     }

#     async tkhelp(e) {

#         if (await getBanGroup.get(e, 'tkhelp')) {
#             send.send_with_At(e, '这里被管理员禁止使用这个功能了呐QAQ！')
#             return false
#         }

#         send.send_with_At(e, `sessionToken有关帮助：\n【推荐】：扫码登录TapTap获取token\n指令：/${Config.getUserCfg('config', 'cmdhead')} bind qrcode\n【基础方法】https://www.kdocs.cn/l/catqcMM9UR5Y\n绑定sessionToken指令：\n/${Config.getUserCfg('config', 'cmdhead')} bind <sessionToken>`)
#     }

#     async apihelp(e) {

#         // if (await getBanGroup.get(e, 'apihelp')) {
#         //     send.send_with_At(e, '这里被管理员禁止使用这个功能了呐QAQ！')
#         //     return false
#         // }
#         if (!Config.getUserCfg('config', 'openPhiPluginApi')) {
#             send.send_with_At(e, `这里没有连接查分平台哦！`)
#             return false
#         }

#         let head = Config.getUserCfg('config', 'cmdhead')
#         head = head.match(RegExp(head))[0]
#         let pluginData = await get.getpluginData(e.user_id)
#         e.reply(await picmodle.help(e, {
#             helpGroup: apiHelp,
#             cmdHead: head || null,
#             isMaster: e.isMaster,
#             background: get.getill(get.illlist[Math.floor((Math.random() * (get.illlist.length - 1)))]),
#             theme: pluginData?.plugin_data?.theme || 'star'
#         }), true)
#     }
# }
