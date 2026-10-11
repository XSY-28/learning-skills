import { readFileSync } from 'node:fs'
import { readFile } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'

const catalog = JSON.parse(readFileSync(new URL('./catalog.json', import.meta.url), 'utf8'))
const providerName = 'learning-skills'
// DSH's public bundled-provider priority; project and user providers rank before it.
const bundledSkillRank = 600
const candidates = catalog.map(({ name, description }) => {
  const directory = new URL(`../skills/${name}/`, import.meta.url)
  const entry = new URL('SKILL.md', directory)
  return {
    name,
    description,
    path: fileURLToPath(entry),
    invocation: { modelInvocable: true, userInvocable: true },
    provider: providerName,
    source: 'bundled',
    resourceBase: { kind: 'directory', path: fileURLToPath(directory) },
    rank: bundledSkillRank,
    locator: entry,
  }
})

const provider = {
  name: providerName,
  async list(options = {}) {
    options.signal?.throwIfAborted()
    return candidates
  },
  async get(candidate, options = {}) {
    options.signal?.throwIfAborted()
    const entry = candidates.find(({ name }) => name === candidate.name)
    if (!entry) return undefined
    const text = await readFile(entry.locator, { encoding: 'utf8', signal: options.signal })
    const { rank, locator, ...summary } = entry
    return {
      ...summary,
      content: text.replace(/^---\r?\n[\s\S]*?\r?\n---(?:\r?\n|$)/, ''),
    }
  },
}

export const name = 'learning-skills'
export const inject = ['skills']

export function apply(ctx) {
  ctx.skills.registerProvider(() => provider)
}
