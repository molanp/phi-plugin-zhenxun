import fCompute from "../fCompute.js"
import getInfo from "../getInfo.js"

export default new class scoreHistory {

    /**
     * 生成成绩记录数组
     * @param {number} acc 
     * @param {number} score 
     * @param {Date} date
     * @param {boolean} fc 
     * @returns []
     */
    create(acc, score, date, fc) {
        return [acc.toFixed(4), score, date, fc]
    }

    /**
     * 扩充信息
     * @param {string} songsid 曲目id
     * @param {EZ|HD|IN|AT|LEGACY} level 难度
     * @param {Array} now 
     * @param {Array} old 
     * @returns {Object}
     */
    extend(songsid, level, now, old) {
        let song = getInfo.idgetsong(songsid) || songsid
        now[0] = Number(now[0])
        now[1] = Number(now[1])
        if (old) {
            old[0] = Number(old[0])
            old[1] = Number(old[1])
        }
        if (getInfo.info(song, true)?.chart[level]?.difficulty) {
            /**有难度信息 */
            return {
                song: song,
                rank: level,
                illustration: getInfo.getill(song),
                Rating: Rating(now[1], now[3]),
                rks_new: fCompute.rks(now[0], getInfo.info(song, true).chart[level].difficulty),
                rks_old: old ? fCompute.rks(old[0], getInfo.info(song, true).chart[level].difficulty) : undefined,
                acc_new: now[0],
                acc_old: old ? old[0] : undefined,
                score_new: now[1],
                score_old: old ? old[1] : undefined,
                date_new: new Date(now[2]),
                date_old: old ? new Date(old[2]) : undefined
            }
        } else {
            /**无难度信息 */
            return {
                song: song,
                rank: level,
                illustration: getInfo.getill(song),
                Rating: Rating(now[1], now[3]),
                acc_new: now[0],
                acc_old: old ? old[0] : undefined,
                score_new: now[1],
                score_old: old ? old[1] : undefined,
                date_new: new Date(now[2]),
                date_old: old ? new Date(old[2]) : undefined
            }
        }
    }

    /**
     * 展开信息
     * @param {Array} data 历史成绩
     */
    open(data) {
        return {
            acc: data[0],
            score: data[1],
            date: new Date(data[2]),
            fc: data[3]
        }
    }

    /**
     * 获取该成绩记录的日期
     * @param {Array} data 成绩记录
     * @returns {Date} 该成绩的日期
     */
    date(data) {
        return new Date(data[2])
    }
}


function Rating(score, fc) {
    if (score >= 1000000)
        return 'phi'
    else if (fc)
        return 'FC'
    else if (score < 700000)
        return 'F'
    else if (score < 820000)
        return 'C'
    else if (score < 880000)
        return 'B'
    else if (score < 920000)
        return 'A'
    else if (score < 960000)
        return 'S'
    else
        return 'V'
}