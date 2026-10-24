# PRライフサイクル＆クリーンアップガイド (PR Lifecycle & Cleanup Guide)

本ドキュメントは、Definition of Done (DoD) の確認、Pull Requestの起票、人間との対話的レビュー対応、およびマージ後の安全なクリーンアップ手順の詳細規定である。

---

## 1. Definition of Done (DoD) チェックリスト

Pull Requestを作成する前に、以下の4つの条件をすべて満たしていることを確認する。

1. **ドキュメントの整合性維持**:
   - コード変更に伴い、関連する仕様書（`docs/system/*.md`、`docs/components/*.md`、`AGENTS.md` 等）を必要に応じて更新・同期していること。
2. **テストコードの整合性維持・作成**:
   - 仕様書の受入条件を検証するテストが作成・更新されていること。
3. **ローカル検証・自己修復の通過**:
   - プロジェクト標準のテストおよびLinterがエラーなく全件通過していること（[self-correction.md](self-correction.md) 参照）。
4. **派生課題（Follow-up Issues）の整理**:
   - タスク実施中に判明したスコープ外の課題や新たな技術的負債があれば、起票準備を行うこと。

---

## 2. 差分サマリー抽出と Walkthrough Artifact 生成

巨大な `git diff` をそのままコンテキストに読み込むのを防ぐため、専用スクリプトでサマリーテキストを生成し、Antigravity Artifact として完了報告を作成する。

1. **差分要約の生成**:
   ```bash
   python .agents/skills/workflow/scripts/generate_walkthrough.py
   # 基準ブランチが main 以外の場合:
   # python .agents/skills/workflow/scripts/generate_walkthrough.py --base-branch develop
   ```
   - スクリプトにより `diff_summary_for_agent.txt` が生成される。
   - エージェントはこの要約（変更ファイル一覧と行数統計）を読み込み、最小限のトークンで変更の全容を把握する。

2. **Walkthrough Artifact の作成 (`walkthrough.md`)**:
   - `write_file` を用い、`<appDataDir>\brain\<conversation-id>\walkthrough.md` を作成する。
   - `ArtifactMetadata` には `UserFacing: true`, `RequestFeedback: false`（またはPR作成承認を求める場合は `true`）を指定する。
   - 内容には、変更概要、変更ファイル一覧（diff要約）、テスト・Lint実行エビデンス（PASSログ）、残課題を含める。
   - **チャット上への全文再出力は絶対禁止 (**MUST NOT**)**。チャットには要約と Artifact へのリンクのみを案内する。

---

## 3. Pull Request の起票

1. **作業ブランチのPush**:
   - 安全確認完了後、作業ブランチをリモートにPushする（例: `git push -u origin <branch-name>`）。
   - ※ `git push --force` (`-f`) は絶対禁止 (**MUST NOT**)。
2. **PR本文の生成とIssue連動**:
   - `.agents/skills/workflow/resources/PULL_REQUEST_TEMPLATE.md` の構造に従って本文を作成する。
   - タイトルに `[AI]` 等の接頭辞は付けず、クリーンなConventional Commitsとする (**MUST**)。
   - 本文末尾に `Closes #XXX`（対象GitHub Issue番号）を必ず記載し、マージ時の自動クローズを連携させる (**MUST**)。
   - 本文最下部にテンプレート規定の共通フッター（`<sub>Generated with AI Agent ({{HARNESS_NAME}})</sub>`、ハーネス名を反映）を含める (**MUST**)。
     - **Summary**: 実装内容の簡潔な要約。
     - **Changes**: 変更箇所の詳細と設計判断の理由。
     - **Verification**: 実行したテスト・Lint結果の事実ベース報告。
     - **Follow-ups**: スコープ外の課題や今後のタスク。
3. **PR起票とレビュー依頼**:
   - `gh pr create --title "..." --body-file "..." --label "ai-generated"`（または `github-mcp-server` の `create_pull_request`）を実行し、必ず `--label "ai-generated"` を付与してPRを作成する (**MUST**)。
   - レビュー依頼や対話的な申し送り（Needs Review）は、PR本文に含めず PRコメント（`add_issue_comment`）として別途投稿する。

---

## 4. レビューと修正の対話ルール

1. **指示の起点はローカルチャット**:
   - 人間からの修正指示やフィードバックは、原則として**ローカルチャット（Antigravity）**で受領する。
   - 人間がGitHub上でレビューコメントを付けた場合は、チャットで「GitHubのコメントに対応して」と指示される。
2. **コメントの取得と対応**:
   - `github-mcp-server` の `get_pull_request_comments` 等を用いてコメントを取得・分析する。
   - 修正作業を行い、テスト・Lintを通過させる。
   - `commit_wip.py` でシークレットスキャンを通過させてコミットし、再Pushする。

---

## 5. マージ後クリーンアップ手順

PRが人間によって承認・マージされた後、以下の手順を順次実行する。

1. **PRマージ状態の事前確認 (MCP: `get_pull_request`)**:
   - 対象PRの `merged` が `true`（かつ `state` が `"closed"`）であることを確認する。
   - マージされていない場合は、クリーンアップを行わず人間に確認を求めること。
2. **GitHub Issue のクローズ (MCP: `update_issue`)**:
   - PRがマージされたら、関連するGitHub Issueをクローズ（`state: "closed"`）する。
3. **ブランチクリーンアップ (`cleanup_branch.py`)**:
   - 以下のスクリプトを実行して、ベースブランチへの切り替え、最新化、ローカルおよびリモートの作業ブランチ削除を一括で安全に実行する。
   ```bash
   python .agents/skills/workflow/scripts/cleanup_branch.py -b feature/issue-XXX-description -p YYY --delete-remote
   ```
4. **ローカル base-branch 最新化の事後検証**:
   - `git log -n 1 main` を確認し、ローカルがリモートの最新マージコミットに追従していることを確認して完了報告を行う。
