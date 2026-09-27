# 输出、状态与核验契约 v1

## 目录与正文

默认项目包含 index.md、glossary.json、revisions.json、learner-profile.json；每讲 lecture-01/ 下有 notes.md、assets/、manifest.json、coverage.json、section-annotations.json、sources/。大视频放用户认可的缓存位置，保留索引。用户显式路径/格式优先；不默认写私人 vault。

正文顺序：来源/讲次/版本/语言/已处理区间/影响完整性的缺失 → 前置与简短导航 → 各语义章节 → 要点和术语 → 必要纠错/未解决问题/来源。不要强制空栏目。每章稳定标记，标题后即放 annotations.display 对应的三行（Markdown 行末加两个空格以保留换行）；正文、图片与推导随后。index 同步三个简短字段。

```markdown
<!-- section: s01 -->
<a id="s01"></a>
## 方程与系数矩阵（02:28–03:17）

> **学习衔接：** 学习记录不足，待确认。
> **章节重点：** 重点——本段核心表示（编者判断）。
> **阅读建议：** 待确认：尚无个人基础。

先引入此图的对象。

![系数矩阵](assets/frame-0001.png)

图注给来源及时间，紧邻解释。短公式嵌入段落，长矩阵独立展示。
```

默认单栏，宽屏可并排短注，窄屏仍上下排列。短公式用 Unicode 或目标环境支持的行内数学；Markdown/Obsidian 通常用单美元，矩阵、多行推导等用双美元展示。完整 LaTeX，公式不放代码/反引号；这份参考中的代码块只是模板，不是最终渲染。核对括号、上下标、量词、溢出及图文距离。不要为行内占比强塞长式。

## JSON 约定

所有根对象含 `schema_version: 1`。UTF-8 JSON，不允许 NaN/Infinity。时间用有限秒数，区间满足 0 ≤ start_s < end_s。ID 为项目内稳定非空字符串。文件路径相对所属 lecture；引用项目文件可在正文用 ../，但 artifact/assets 路径不得逃出 lecture。所有下列字段必需，标明可空的除外。完整可运行最小示例见 [minimal-project.json](minimal-project.json)：键为相对文件路径，值为文件内容，复制时将字符串文件写为文本、其余写 JSON。

- **manifest.json**：course_id、lecture_id、target_language（zh/en）、requested_format（markdown/docx/pdf/html）、artifact_path、source_video_id、processing_range（start_s/end_s）、sources、assets、unresolved_items（允许 []）、document_sha256（最终文件字节 SHA-256）、review_status（unprocessed/drafted/checked）。
  - source：id/kind/ref/version/attribution/license/verification，verification=checked 仅指已按实际范围核对；可用其他具体状态表示未核对。记录 source 的核对范围说明。视频 ID 须在 sources 中。
  - asset：path/source_id，以及视频 requested_time_s/timestamp_basis=requested_seek_time 或课件 page（从 1 起）。可另加 source_time_s 和 timeline_offset_s，明确片段与原片时间映射；不把请求时刻当精确解码时间。
  - 尚未处理整讲时正文显式说明全讲剩余范围；processing_range 只代表此次范围。来源缺口、声音未核对等写 unresolved_items。
- **coverage.json**：processing_range、segments。segment：id/start_s/end_s/disposition/section_id/evidence/reason。evidence 为非空来源定位数组，reason 非空。included 的 section_id 必须存在；其他可 null。disposition 固定为 included / omitted_noninstructional / omitted_assignment / unresolved。主段按时间排序，完整划分处理区间，不重叠、不留缺口；并行板书和声音可写在同段 evidence 中。unresolved 发警告，不能算核对完成。
- **glossary.json**：course_id、entries。entry：source_term/domain/concept/target_language/rendering/keep_original（布尔）/evidence（定位数组）/user_override（布尔）。唯一键是前四项组合，不对 source_term 单独全局替换。
- **revisions.json**：entries。每项 at（ISO 日期时间或无法确定时 null）、correction、affected_files、checked_scope、unchecked_scope、backup_paths；后三类范围、路径为数组。记录实际范围，不把未检查的讲次标成同步。
- **learner-profile.json**：profile_id/revision（非负整数）/learning_goal（字符串或 null）/source_scope（用户给定来源清单）/evidence_records。
  - evidence：id/source_ref/observed_at（日期或 null）/domain/concept/depth/assertion/origin。origin 示例 user_self_report、observed_performance、study_record、generated_material、prior_inference。可加 readable:false（来源不能重读时警告）、supersedes（旧记录 ID）。不编造日期，不把 generated_material 自动升级为学习活动。
- **section-annotations.json**：profile_id/profile_revision/sections。每节 section_id/concepts/importance/reading_advice/display。
  - concept：domain/concept/depth/learning_status/mastery_basis/evidence_ids/rationale。learning_status = studied / exposure_only / explicitly_unlearned / unknown；非 unknown 必须引用存在的证据。mastery_basis = not_assessed / self_reported / performance_supported，后两项须分别引用 user_self_report / observed_performance 类型证据。类型相符并不证明证据支持该概念，仍需模型核对。
  - importance：level（key/regular/undetermined）、非空 reasons；每个 reason 含 basis_type（teacher_emphasis/course_dependency/learning_goal/editorial_assessment）、text、source_ref。待判断也写缺少什么依据。
  - reading_advice：level（read_carefully/targeted_review/quick_review/undetermined）、reason。
  - display：learning/importance/advice 三个非空的目标语言字符串，用于章首和目录的一致性检查；通常用简短依据 ID，详情在 concepts。

目录 Markdown 每章一行 `- [标题](lecture-01/notes.md#s01) — learning文本 | importance文本 | advice文本`。锚点用明确 `<a id="s01"></a>`，正文标记 comment 紧邻标题之前，方便稳定引用。普通附录/要点无需假装语义章节。不要用未标记的标题隐藏教学章节。校验器识别显式 inline link 与 anchor；参考式链接另行检查，自动标题 slug 各阅读器不同，推荐显式锚点。

## 指定格式与二进制映射

- Word 调用实际可用的 documents 技能与 workspace dependency loader，用真正 docx、内嵌图片及原生公式或高质量公式图；不只改后缀、不悄悄退回 Markdown。读取对应工具的最新说明。
- HTML 用已实际运行的数学渲染器；PDF 用现有导出工具，不另造全格式导出引擎。
- docx/pdf/html 附 artifact-map.json：schema_version、artifact_sha256、sections，每节 section_id/locator/display。docx locator 的 paragraph_index 是 word/document.xml 全部 w:p 的零基索引（含表格段落）；标题后紧随三段标签。PDF 用已核实页码，HTML 用稳定 ID。display 等于 annotations，映射哈希绑定最终产物。
- 校验器对 docx 读取 ZIP/XML 并检查标记段落；PDF 仅检查签名；HTML 仅映射。必须实际打开或渲染最终文件，核对目录、章首、图片、公式、每页布局。包结构与中间稿通过不等于最终格式通过。不能渲染时分别报告“已生成”和“视觉未验证”。

## 续作与修订保护

生成前读取已有 manifest 的哈希，与现有 artifact 比较。相同说明未检测到字节变化；不同则认为可能含手动修改，禁止无条件重建覆盖。无旧哈希也不能假定可覆盖。先以唯一版本名备份正文与关联状态（保持相对图片可用），再输出 notes.revision-N.md 等修订副本或对确认的范围局部修改。保留用户批注、原始证据，不自动消除冲突。

术语更正：修订课程 glossary 的具体语境/概念条目，检索本课相关段落、公式解释和问答并逐个核对；不跨课程批量替换。学习更正：追加证据、revision 加一，更新受影响章首/目录/annotations；目标变化只重评理由和建议，不改学习历史。完成后更新实际文稿哈希、revisions 的检查范围；未处理讲次保持原 profile_revision 以触发过期警告。

## CLI 与完成边界

```sh
python3 scripts/validate_output.py LECTURE_DIR --report NEW_REPORT_JSON
```

读取讲次及其父级课程状态；不修改课程文件，不覆盖已有报告。输出 schema_version/errors/warnings；结构错误非零，只有警告可零退出但不能称“全部核对完成”。检查文件、字段、有限时间、覆盖缺口/重叠、ID、图片、内部引用、学习证据类型和目录/章首标记；revision、文稿哈希变化及未解决事项警告。坏类型与坏 JSON 变为诊断。

工具没有验证语义匹配、重点真伪、推导正确、截图文字、学习掌握或外部链接可访问性。除了脚本，还必须按素材人工/模型核对并在验收记录写实际输入、输出、检查结果与限制。
