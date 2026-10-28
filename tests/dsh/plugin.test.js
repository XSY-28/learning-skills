import assert from 'node:assert/strict'
import { execFileSync } from 'node:child_process'
import { mkdtemp, readFile, realpath, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'
import test from 'node:test'
import { Context } from '@deepseek-ai/cordis'
import SkillRegistry, { renderSkillContent } from '@deepseek-ai/dsh-skill'
import * as plugin from '../../dsh/index.js'

const root = fileURLToPath(new URL('../../', import.meta.url))
const names = ['course-to-notes', 'evolutionary-understanding', 'explain-for-understanding', 'obsidian-lecture-writing']
const customizedName = 'explain-for-understanding'

async function mount(t, module = plugin) {
  const ctx = new Context()
  ctx.plugin(SkillRegistry)
  const fiber = ctx.plugin(module)
  await new Promise(resolve => setImmediate(resolve))
  t.after(() => ctx.fiber.dispose())
  return { ctx, fiber }
}

async function checkSkills(ctx, packageRoot) {
  const catalog = await ctx.skills.list()
  assert.deepEqual(catalog.map(skill => skill.name), names)
  for (const name of names) {
    const skill = await ctx.skills.get(name)
    const directory = await realpath(join(packageRoot, 'skills', name))
    assert.equal(resolve(skill.resourceBase.path), resolve(directory))
    assert.equal(skill.path, join(directory, 'SKILL.md'))
    assert.equal(skill.invocation.modelInvocable, true)
    assert.equal(skill.invocation.userInvocable, true)
    const source = await readFile(join(directory, 'SKILL.md'), 'utf8')
    assert.equal(skill.content, source.replace(/^---\r?\n[\s\S]*?\r?\n---(?:\r?\n|$)/, ''))
    const rendered = renderSkillContent(skill)
    assert.ok(rendered.includes(directory))
    assert.ok(rendered.includes(skill.content))
    for (const match of skill.content.matchAll(/\]\((references\/[^)]+)\)/g)) {
      assert.ok((await readFile(join(directory, match[1]))).length > 0)
    }
  }
}

test('real DSH registry discovers, loads and renders all four skills and resources', async t => {
  const { ctx } = await mount(t)
  await checkSkills(ctx, root)
  assert.equal(await ctx.skills.get('unknown-skill'), undefined)
})

test('disabling the plugin removes its skills and remounting restores them', async t => {
  const { ctx, fiber } = await mount(t)
  assert.equal((await ctx.skills.list()).length, names.length)
  await fiber.dispose()
  assert.deepEqual(await ctx.skills.list(), [])
  ctx.plugin(plugin)
  await new Promise(resolve => setImmediate(resolve))
  assert.equal((await ctx.skills.list()).length, names.length)
})

test('a runtime customization overrides a bundled skill without hiding other skills', async t => {
  const { ctx } = await mount(t)
  const customization = ctx.plugin({
    inject: ['skills'],
    apply(ctx) {
      ctx.skills.register({ name: customizedName, description: 'Custom explanation skill', source: 'runtime', content: 'Custom instructions' })
    },
  })
  await new Promise(resolve => setImmediate(resolve))
  assert.equal((await ctx.skills.get(customizedName)).content, 'Custom instructions')
  assert.equal((await ctx.skills.list()).length, names.length)
  await customization.dispose()
  assert.equal((await ctx.skills.get(customizedName)).provider, 'learning-skills')
})

test('the packed artifact works after relocation and contains its referenced course helper', async t => {
  const temp = await mkdtemp(join(tmpdir(), 'learning-skills-pack-'))
  t.after(() => rm(temp, { recursive: true, force: true }))
  const [pack] = JSON.parse(execFileSync('npm', ['pack', '--ignore-scripts', '--json', '--pack-destination', temp, '--cache', join(temp, 'npm-cache')], { cwd: root, encoding: 'utf8' }))
  assert.ok(pack.files.every(file => !/(node_modules|__pycache__|\.pyc$|^tests\/|^scripts\/|^task_plan)/.test(file.path)))
  execFileSync('tar', ['-xzf', join(temp, pack.filename), '-C', temp])
  const packageRoot = join(temp, 'package')
  const manifest = JSON.parse(await readFile(join(packageRoot, 'package.json'), 'utf8'))
  assert.equal(manifest.dsh.bundle.patch, './cordis.patch.yml')
  assert.ok((await readFile(join(packageRoot, manifest.dsh.bundle.patch), 'utf8')).includes('name: dsh-learning-skills'))
  for (const key of ['preinstall', 'install', 'postinstall', 'prepare']) assert.equal(manifest.scripts?.[key], undefined)
  const relocated = await import(pathToFileURL(join(packageRoot, 'dsh/index.js')).href)
  const { ctx } = await mount(t, relocated)
  await checkSkills(ctx, packageRoot)
  const course = await ctx.skills.get('course-to-notes')
  const helper = join(course.resourceBase.path, 'scripts', 'parse_captions.py')
  assert.match(execFileSync('python3', [helper, '--help'], { encoding: 'utf8' }), /--source-id/)
})
