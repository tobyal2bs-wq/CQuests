// A test player for CI: joins, reads the welcome guide, talks to Stephan, accepts a quest,
// checks the boss bar tracker, then completes chapters to trigger the achievements.
const mineflayer = require('mineflayer')

const bot = mineflayer.createBot({ host: '127.0.0.1', port: 25565, username: 'CQBot', version: process.env.MC_VERSION, auth: 'offline' })
const chat = []
const bars = []
const sleep = (ms) => new Promise((r) => setTimeout(r, ms))

bot.on('messagestr', (m) => { console.log('CHAT ' + m); chat.push(m) })
bot.on('bossBarCreated', (bar) => { const t = String(bar.title); console.log('BOSSBAR ' + t); bars.push(bar) })
bot.on('bossBarUpdated', (bar) => console.log('BOSSBAR ' + String(bar.title)))
bot.on('kicked', (r) => fail('kicked: ' + JSON.stringify(r)))
bot.on('error', (e) => fail('error: ' + e))

function fail (why) { console.log('BOT FAILED: ' + why); process.exit(1) }

async function waitFor (re, ms) {
  const end = Date.now() + ms
  while (Date.now() < end) {
    if (chat.some((m) => re.test(m))) return
    await sleep(250)
  }
  fail('never saw ' + re)
}

function stephan () {
  const npcs = Object.values(bot.entities).filter((e) => e !== bot.entity && (e.name === 'villager' || e.name === 'mannequin'))
  const named = npcs.find((e) => /Stephan/.test(JSON.stringify(e.metadata || [])))
  return named || bot.nearestEntity((e) => e.name === 'villager')
}

bot.once('spawn', async () => {
  await waitFor(/Welcome to Dawn SMP/, 30000)
  console.log('OK welcome guide')
  await sleep(4000) // the test script ops the bot when it joins
  bot.chat('/cq npc tp stephan')
  await sleep(4000)
  const npc = stephan()
  if (!npc) fail('no villager near Stephan\'s spot')
  await bot.lookAt(npc.position.offset(0, 1.5, 0))
  await bot.activateEntity(npc)
  await waitFor(/Quest complete: Welcome to Dawn SMP/, 20000)
  console.log('OK welcome quest done by talking to Stephan')
  await waitFor(/Click the villager again/, 30000)
  await bot.activateEntity(npc)
  await waitFor(/New quest: The Wanderers/, 15000)
  console.log('OK accepted The Wanderers')
  await sleep(1500)
  if (!bars.some((b) => /The Wanderers/.test(String(b.title)))) fail('no boss bar for the tracked quest')
  console.log('OK boss bar tracker')
  bot.chat('/cq player CQBot complete story_dave')
  await sleep(3000)
  bot.chat('/cq player CQBot complete story_aldric')
  await sleep(5000)
  console.log('BOT PASSED')
  bot.quit()
  await sleep(1000)
  process.exit(0)
})

setTimeout(() => fail('timed out'), 180000)
