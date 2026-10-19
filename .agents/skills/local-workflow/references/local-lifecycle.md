# ローカルタスク・ライフサイクルガイド (Local Task Lifecycle Guide)

本ドキュメントは、GitHub Issue / PR やリモートリポジトリ連携を使用しない、ローカル環境完結型開発におけるタスク管理・レビュー承認・マージ・完了移動の詳細手順規定である。

---

## 1. タスク管理と作業ブランチの開始

1. **タスクの命名規則**:
   - タスク識別子は、3桁の連番またはカテゴリプレフィックスを推奨（例: `001-setup-auth`, `002-add-user-model`, `task-fix-parser`）。
   - **タイトル規約**: タイトルに `[AI]` や絵文字等の接頭辞（Prefix）は付けず、クリーンな日本語タイトルとする (**MUST**)。
2. **スクリプトによる自動初期化**:
   - 以下のスクリプトを実行すると、`docs/tasks/` および `docs/tasks/completed/` が自動作成され、Frontmatter（`labels: ["ai-generated"]`）と共通フッターを含んだタスク文書の生成と作業ブランチの作成・チェックアウトが一括で実行される。
   ```bash
   python .agents/skills/local-workflow/scripts/start_task_branch.py -t 001-setup-auth --title "認証機能の基盤構築"
   ```
3. **タスク文書（`docs/tasks/<task>.md`）の編集**:
   - 生成されたタスク文書内の Goal（受入条件）、Context（仕様リンク）、Technical Details（制約）、Verification（検証手順）を明確化してから実装を開始する。
   - 文書最下部の共通フッター（`<sub>※ 本ドキュメントは AI Agent (Antigravity) により自律生成されました。</sub>`）を維持すること。

---

## 2. 実装とWIPコミット（セーブポイント）

- 作業ブランチ上での自律的なWIPコミットは許可される。
- 機密情報（APIキー、トークン、秘密鍵）の混入を100%機械的に防ぐため、必ず専用スクリプトを使用すること。
```bash
python .agents/skills/local-workflow/scripts/commit_wip.py -m "作業内容の説明" -t 001-setup-auth
```

---

## 3. Walkthrough Artifact 生成と人間へのマージ承認要請

実装および自律テスト（[self-correction.md](self-correction.md)）が全件通過した後、エージェントは直ちにマージを行わず、**必ず人間に成果物の確認・マージ承認を求める**。

1. **差分サマリーの抽出 (Token Economy)**:
   ```bash
   python .agents/skills/local-workflow/scripts/generate_walkthrough.py
   ```
   - 生成された `diff_summary_for_agent.txt` を読み込み、変更ファイルと行数を把握する。
2. **Walkthrough Artifact の作成 (`walkthrough.md`)**:
   - `write_to_file` を用い、`<appDataDir>\brain\<conversation-id>\walkthrough.md` を作成する。
   - `ArtifactMetadata` には `UserFacing: true`, `RequestFeedback: true` を指定し、UI上に「Proceed」ボタンを表示させてマージ承認を要請する。
   - 内容には、概要、変更内容（設計判断を含む）、検証結果（全件パスの事実）、派生課題を含める。
   - チャット上では長大な全文を再要約せず、サマリーと Artifact へのリンクのみを案内する。

---

## 4. 人間承認後のローカルマージ (`merge_branch.py`)

人間がチャット上で「マージして」「OK」「進めて」と承認を出した後、以下のスクリプトを実行して安全にローカルマージを行う。

```bash
python .agents/skills/local-workflow/scripts/merge_branch.py -b task/001-setup-auth
```

- スクリプトにより以下が安全に実行される：
  1. 未コミット変更のチェック
  2. ベースブランチ（`main`）への切り替え
  3. `git merge task/001-setup-auth` の実行
  4. マージ済み作業ブランチの削除
  5. 一時差分ファイルの削除
  6. `git log -n 1 main` によるマージコミットの検証出力

---

## 5. タスク完了処理 (`complete_task.py`)

マージ完了後、タスク文書のステータス更新と保管移動を行う。

```bash
python .agents/skills/local-workflow/scripts/complete_task.py -t 001-setup-auth.md
```

- スクリプトにより以下が自動実行される：
  1. `docs/tasks/001-setup-auth.md` 内のステータスを `🟢 完了`、完了日を当日の日付に更新。
  2. ファイルを `docs/tasks/completed/001-setup-auth.md` に移動。
  3. `docs/tasks/README.md` 内のリンクを `completed/` 配下へ書き換え、アイコンを更新。
4. 人間に「タスク完了およびマージが正常に完了しました」と最終報告を行う。
