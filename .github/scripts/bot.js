// Protocol-level integration test against an isolated Paper server.
const mineflayer = require('mineflayer')
const bot = mineflayer.createBot({ host: '127.0.0.1', port: Number(process.env.MC_PORT || 25565), username: 'CQBot', version: process.env.MC_VERSION || '1.21.4', auth: 'offline' })
const chat = []
const bars = []
const actionBars = []
const welcomeTitle = 'Welcome to ' + (process.env.MC_SERVER_NAME || 'Dawn SMP')
const welcomeComplete = 'Quest complete: ' + welcomeTitle
let books = 0
let responseToken = null
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms))
bot.on('messagestr', m => { console.log('CHAT ' + m); chat.push(m) })
bot.on('bossBarCreated', bar => { console.log('BOSSBAR ' + String(bar.title)); bars.push(bar) })
bot.on('actionBar', message => actionBars.push(String(message)))
bot._client.on('action_bar', packet => actionBars.push(JSON.stringify(packet)))
bot._client.on('open_book', () => { books++; console.log('BOOK OPENED') })
bot._client.on('set_slot', packet => {
  const match = JSON.stringify(packet).match(/\/quests respond ([0-9a-f-]{36})/)
  if (match) responseToken = match[1]
})
bot.on('kicked', r => fail('kicked: ' + JSON.stringify(r)))
bot.on('error', e => fail('error: ' + e))
function fail (why) { console.error('BOT FAILED: ' + why); process.exit(1) }
function check (value, label) { if (!value) fail(label); console.log('OK ' + label) }
async function until (condition, label, ms = 30000) {
  const end = Date.now() + ms
  while (Date.now() < end) { if (condition()) return; await sleep(150) }
  fail('timed out: ' + label)
}
async function message (re, start = 0) { await until(() => chat.slice(start).some(m => re.test(m)), String(re)) }
async function command (text) { const start = chat.length; bot.chat(text); await sleep(350); return start }
function named (name) {
  const entities = Object.values(bot.entities)
  const oldTag = entities.find(e => e.name === 'villager' && JSON.stringify(e.metadata || []).includes(name))
  if (oldTag) return oldTag
  const plate = entities.find(e => e.name === 'text_display' && JSON.stringify(e.metadata || []).includes(name.toUpperCase()) && JSON.stringify(e.metadata || []).includes('LEVEL'))
  return plate && entities.find(e => e.name === 'villager' && Math.abs(e.position.x - plate.position.x) < 0.75 && Math.abs(e.position.z - plate.position.z) < 0.75 && plate.position.y - e.position.y > 1 && plate.position.y - e.position.y < 5)

}
async function converse (npc) {
  if (bot.currentWindow) bot.closeWindow(bot.currentWindow)
  await bot.lookAt(npc.position.offset(0, 1.5, 0))
  await bot.activateEntity(npc)
  await until(() => bot.currentWindow, 'dialogue menu opens')
  await until(() => bot.currentWindow?.slots[22]?.name === 'writable_book', 'dialogue item packets arrive')
  check(bot.currentWindow.slots[22]?.name === 'writable_book', 'dialogue has a readable book card')
  while (bot.currentWindow?.slots[53]?.name === 'arrow') {
    await bot.clickWindow(53, 0, 0); await sleep(400)
  }
  check(bot.currentWindow.slots[40]?.name === 'lime_concrete', 'dialogue has a confirmation button')
  await bot.clickWindow(40, 0, 0)
  await sleep(500)
}
bot.once('spawn', async () => {
  try {
    // Reconnect tests use a player that has already seen the first-join guide.
    if (process.env.RECONNECT_TEST !== 'true') await until(() => chat.some(m => m.includes(welcomeTitle)), 'configured welcome: ' + welcomeTitle)
    await sleep(4500)
    if (process.env.RECONNECT_TEST === 'true') {
      await until(() => bars.length > 0, 'tracker preference restored after restart')
      await command('/quests')
      await until(() => bot.currentWindow, 'saved menu preference after restart')
      await until(() => bot.currentWindow?.slots[46]?.name === 'recovery_compass', 'saved menu item packets arrive')
      check(bot.currentWindow.slots[46]?.name === 'recovery_compass', 'settings controls restored')
      console.log('BOT PASSED: preferences survive a full server restart')
      bot.quit(); await sleep(500); process.exit(0)
    }
    check(bars.length === 0, 'boss bar is off by default')
    await command('/gamemode creative')
    await command('/quests')
    await until(() => books > 0, 'journal defaults to book')
    await command('/cq npc tp stephan')
    await until(() => named('Stephan'), 'Stephan actually spawns', 45000)
    await sleep(1000)
    await bot.activateEntity(named('Stephan'))
    await until(() => responseToken, 'book conversation has a response')
    let start = chat.length
    await command('/quests respond ' + responseToken)
    await until(() => chat.slice(start).some(m => m.includes(welcomeComplete)), welcomeComplete)
    await command('/quests respond ' + responseToken)
    check(chat.filter(m => m.includes(welcomeComplete)).length === 1, 'book rewards cannot be claimed twice')
    await command('/quests mode menu')
    await command('/cq npc tp astra')
    await sleep(4500)
    check(!named('Astra'), 'chapter five villager is hidden in chapter one')
    await command('/cq npc tp stephan')
    await until(() => named('Stephan'), 'Stephan actually spawns', 45000)
    await sleep(1000)
    start = chat.length
    await converse(named('Stephan'))
    await message(/New quest: The Wanderers/, start)
    check(bars.length === 0, 'accepting quests does not silently enable the boss bar')
    await command('/quests track')
    await until(() => bars.some(b => /The Wanderers/.test(String(b.title))), 'opt-in tracker')
    console.log('OK opt-in boss bar')
    await command('/quests directions')
    await until(() => actionBars.some(m => /[↑↗→↘↓↙←↖].*\d+ m/.test(m)), 'direction arrow and meters')
    console.log('OK directions arrow and meters')
    await command('/quests menu')
    await until(() => bot.currentWindow, 'quest menu opens')
    const before = bot.inventory.items().length
    await bot.clickWindow(4, 0, 1)
    await sleep(400)
    check(bot.inventory.items().length === before, 'menu items cannot be taken')
    bot.closeWindow(bot.currentWindow)
    start = chat.length
    await command('/cq scatterworld luma 10000 10000 world 0 0')
    await message(/Scattered 1 NPCs; 0 skipped/, start)
    start = chat.length
    await command('/cq scatterworld luma 64 64 world 384 384')
    await message(/Scattered 1 NPCs; 0 skipped/, start)
    await command('/quests list')
    await message(/The Wanderers/)
    console.log('OK repeat world scattering preserves the active story')
    await command('/gamemode creative')
    async function terrain (dimension, material) {
      await command('/execute in minecraft:' + dimension + ' run tp CQBot 640.5 72 640.5')
      await sleep(2500)
      await command('/fill 630 60 630 650 75 650 air')
      // Nether lava must be enclosed below the test surface: removing only its source must
      // not leave flowing lava beneath the platform and invalidate the subsequent safe case.
      const floorY = dimension === 'the_nether' ? 60 : 63
      await command('/fill 630 ' + floorY + ' 630 650 63 650 ' + material)
      await command('/tp CQBot 640.5 64 640.5')
      await sleep(500)
    }
    if (process.env.SKIP_TERRAIN !== 'true') {
    await terrain('the_end', 'end_stone')
    start = chat.length
    await command('/cq npc place luma')
    await message(/Luma now stands here/, start)
    await command('/setblock 650 63 640 air')
    start = chat.length
    await command('/cq npc place luma')
    await message(/Unsafe spot.*Previous position kept/, start)
    await command('/setblock 650 63 640 end_stone')
    console.log('OK real End placement rejects a void column at ten blocks')
    await terrain('the_nether', 'netherrack')
    await command('/setblock 650 63 640 lava')
    start = chat.length
    await command('/cq npc place luma')
    await message(/Unsafe spot.*Previous position kept/, start)
    await command('/setblock 650 63 640 netherrack')
    start = chat.length
    await command('/cq npc place luma')
    await message(/Luma now stands here/, start)
    await command('/tp CQBot 640.5 128 640.5')
    start = chat.length
    await command('/cq npc place luma')
    await message(/Unsafe spot.*Previous position kept/, start)
    console.log('OK real Nether placement rejects nearby lava and the roof')
    await command('/execute in minecraft:overworld run tp CQBot 0.5 10 0.5')
    await command('/cq npc tp stephan')
    }
    await command('/cq test achievement 3')
    await command('/quests achievements')
    await message(/A Helping Hand/)
    if (process.env.CHAPTER_ONE_END && process.env.STORY_END) {
      await command('/cq player CQBot complete ' + process.env.CHAPTER_ONE_END)
      await command('/cq player CQBot complete ' + process.env.STORY_END)
    }
    await sleep(1000)
    console.log('BOT PASSED')
    bot.quit(); await sleep(750); process.exit(0)
  } catch (error) { fail(error.stack || String(error)) }
})
setTimeout(() => fail('overall timeout'), 240000)
