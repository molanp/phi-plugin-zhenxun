import Version from './Version.js'
import Data from './Data.js'
import Config from './Config.js'
import YamlReader from './YamlReader.js'
const Path = process.cwd()
const Display_Plugin_Name = 'Phi-Plugin'
const Plugin_Name = 'phi-plugin'
const Plugin_Path = `${Path}/plugins/${Plugin_Name}`
export { Config, Data, Version, Path, Plugin_Name, Plugin_Path, Display_Plugin_Name, YamlReader }
