"""Small wholly synthetic valid v1 project; no private learner data."""
import hashlib
import json
from pathlib import Path


def write_json(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def make_project(base):
    root = Path(base) / 'lecture-01'
    root.mkdir(parents=True)
    display = {'learning': '待确认：无学习记录。', 'importance': '重点：本段核心定义。', 'advice': '待确认：尚无个人基础。'}
    text = '# 合成测试\n\n<!-- section: s01 -->\n<a id="s01"></a>\n## 定义\n\n' + '\n'.join('> ' + v for v in display.values()) + '\n\n定义的解释。\n'
    (root / 'notes.md').write_text(text, encoding='utf-8')
    (base / 'index.md').write_text('- [定义](lecture-01/notes.md#s01) — ' + ' | '.join(display.values()) + '\n', encoding='utf-8')
    span = {'start_s': 0, 'end_s': 10}
    write_json(root / 'manifest.json', {'schema_version': 1, 'course_id': 'synthetic', 'lecture_id': 'l01', 'target_language': 'zh', 'requested_format': 'markdown', 'artifact_path': 'notes.md', 'source_video_id': 'v1', 'processing_range': span, 'sources': [{'id': 'v1', 'kind': 'synthetic_video', 'ref': 'synthetic://test', 'version': '1', 'attribution': 'self-created', 'license': 'test fixture', 'verification': 'checked'}], 'assets': [], 'unresolved_items': [], 'document_sha256': hashlib.sha256(text.encode()).hexdigest(), 'review_status': 'checked'})
    write_json(root / 'coverage.json', {'schema_version': 1, 'processing_range': span, 'segments': [{'id': 'c1', 'start_s': 0, 'end_s': 10, 'disposition': 'included', 'section_id': 's01', 'evidence': ['synthetic://test'], 'reason': '完整合成定义段'}]})
    write_json(base / 'learner-profile.json', {'schema_version': 1, 'profile_id': 'synthetic-empty', 'revision': 0, 'learning_goal': None, 'source_scope': [], 'evidence_records': []})
    write_json(base / 'glossary.json', {'schema_version': 1, 'course_id': 'synthetic', 'entries': []})
    write_json(base / 'revisions.json', {'schema_version': 1, 'entries': []})
    write_json(root / 'section-annotations.json', {'schema_version': 1, 'profile_id': 'synthetic-empty', 'profile_revision': 0, 'sections': [{'section_id': 's01', 'concepts': [{'domain': 'linear algebra', 'concept': 'linear combination', 'depth': 'definition', 'learning_status': 'unknown', 'mastery_basis': 'not_assessed', 'evidence_ids': [], 'rationale': '无记录不代表未学'}], 'importance': {'level': 'key', 'reasons': [{'basis_type': 'editorial_assessment', 'text': '本段核心定义', 'source_ref': 'synthetic://test'}]}, 'reading_advice': {'level': 'undetermined', 'reason': '个人基础未知'}, 'display': display}]})
    return root
