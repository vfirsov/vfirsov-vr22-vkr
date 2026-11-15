import assert from 'node:assert/strict'
import { spawn } from 'node:child_process'
import { once } from 'node:events'
import { createServer } from 'node:http'
import { setTimeout as delay } from 'node:timers/promises'
import test from 'node:test'

// Run against the production build. A mutable upstream proves per-request SSR.
test('catalog renders upstream data at runtime and handles outages', async (t) => {
  let name = 'Первый чай из API'
  let unavailable = false
  let calls = 0
  const api = createServer((req, res) => {
    assert.equal(req.url, '/api/catalog')
    calls++
    res.setHeader('Content-Type', 'application/json')
    res.statusCode = unavailable ? 503 : 200
    res.end(JSON.stringify(unavailable ? { error: 'offline' } : {
      items: [{ id: 1, slug: 'test', name, category: 'Зелёный чай', origin: 'Китай', description: 'Свежий чай.', price: 690, weightGrams: 50, inStock: true }],
      total: 1, currency: 'RUB',
    }))
  })
  api.listen(0, '127.0.0.1')
  await once(api, 'listening')
  t.after(() => { api.closeAllConnections(); api.close() })

  const portProbe = createServer()
  portProbe.listen(0, '127.0.0.1')
  await once(portProbe, 'listening')
  const port = portProbe.address().port
  await new Promise(resolve => portProbe.close(resolve))
  const origin = `http://127.0.0.1:${port}`
  const child = spawn(process.execPath, ['.output/server/index.mjs'], {
    cwd: new URL('../', import.meta.url),
    env: { ...process.env, NODE_ENV: 'production', HOST: '127.0.0.1', PORT: String(port), NUXT_PUBLIC_API_BASE_URL: `http://127.0.0.1:${api.address().port}` },
    stdio: ['ignore', 'pipe', 'pipe'],
  })
  let logs = ''
  child.stdout.on('data', d => { logs += d })
  child.stderr.on('data', d => { logs += d })
  t.after(async () => {
    const exited = once(child, 'exit')
    child.kill('SIGTERM')
    await exited
  })
  let ready = false
  for (let i = 0; i < 100; i++) {
    try { ready = (await fetch(`${origin}/healthz`)).ok } catch {}
    if (ready) break
    if (child.exitCode !== null) assert.fail(logs)
    await delay(50)
  }
  assert.ok(ready, logs)
  const htmlBody = html => html.replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi, '')
  const first = await fetch(`${origin}/catalog`)
  assert.equal(first.status, 200)
  assert.equal(first.headers.get('cache-control'), 'no-store')
  assert.match(htmlBody(await first.text()), /<h2[^>]*>Первый чай из API<\/h2>/)
  assert.equal(calls, 1)

  name = 'Обновлённый чай без пересборки'
  const second = await fetch(`${origin}/catalog`)
  const html = htmlBody(await second.text())
  assert.match(html, /<h2[^>]*>Обновлённый чай без пересборки<\/h2>/)
  assert.doesNotMatch(html, /Первый чай из API/)
  assert.equal(calls, 2)

  unavailable = true
  const failure = await fetch(`${origin}/catalog`)
  assert.equal(failure.status, 503)
  assert.match(htmlBody(await failure.text()), /Коллекция временно недоступна/)
  assert.equal(calls, 3)
  // The Nuxt server no longer proxies the API: the route is gone from its origin.
  assert.equal((await fetch(`${origin}/api/catalog`)).status, 404)
  assert.equal((await fetch(`${origin}/missing-page`)).status, 404)
})
