---
pr_id: "{{PR_ID}}"
title: "{{PR_TITLE}}"
closes:
{{CLOSES_LIST}}
target_branch: "{{TARGET_BRANCH}}"
branch: "{{BRANCH_NAME}}"
status: "{{STATUS}}"
created_at: "{{CREATED_DATE}}"
labels:
  - "ai-generated"
---
# PR: {{PR_TITLE}}

- **ステータス**: {{STATUS_DISPLAY}}
- **作成日**: {{CREATED_DATE}}
- **作業ブランチ**: `{{BRANCH_NAME}}`
- **マージ先ブランチ**: `{{TARGET_BRANCH}}`

---

## 解決タスク (Resolved Tasks)
{{RESOLVED_TASKS}}

---

## 1. Summary (概要)
<!-- 実装・修正した内容の全体的な要約を簡潔に記載してください。 -->

## 2. Changes (変更内容の詳細)
<!-- どのコンポーネント・ファイルにどのような変更を加えたかを具体的に記載してください。
また、アーキテクチャ上の設計判断や、なぜそのアプローチをとったか（理由）を含めてください。
仕様書 (docs/specs/system/*.md や docs/specs/components/*.md 等) を更新した場合はその旨も記載してください。 -->

## 3. Verification (検証結果・テストエビデンス)
<!-- ローカルで実行したLinter/テストの結果や、動作確認として確認した指標・ログなどを事実ベースで記載してください。 -->

## 4. Follow-ups (派生課題・今後のタスク)
<!-- 今回のスコープから外した事項や、新たに発見された課題（起票済みのタスクへのリンク等）を記載してください。 -->

---
<sub>Generated with AI Agent ({{HARNESS_NAME}})</sub>
