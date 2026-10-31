APSS Virtual Research Studio v0.2 — 公開來源蒐集試行版

這個版本新增真正會在 GitHub Actions 執行的公開 RSS 標題蒐集程式。
它不是完整 AI Agent，也不是正式 APSS MR（Monitoring Report）排程。
嚴禁將成功蒐集新聞標題視為完成查證、策略研析、通知或報告。

檔案：
- index.html：辦公室網頁，顯示真正蒐集的新聞線索及擷取狀態
- scripts/collect_sources.py：執行 RSS 蒐集、錯誤紀錄與資料輸出
- .github/workflows/apss-collector.yml：手動／每日 08:30（臺灣時間）觸發蒐集並部署頁面

上傳與執行：
1. 在 GitHub 原儲存庫 Code → Add file → Upload files。把本資料夾裡 index.html、scripts 資料夾、.github 資料夾拖曳到上傳區（保留目錄層級），Commit changes。
2. Settings → Pages → Build and deployment → Source 改成 GitHub Actions。
3. Actions → APSS 公開來源蒐集與頁面發布（試行） → Run workflow。
4. Actions 出現 Success 後，打開 https://apss-netizen.github.io/apss-virtual-research-studio/
5. 如果 Action 顯示找不到檔案，請確認 scripts/collect_sources.py 及 .github/workflows/apss-collector.yml 的完整路徑。不要上傳 ZIP 作為可執行專案。
6. 舊的 index.html 在根目錄，請直接替換。建議另外備份既有 v0.1.2 版本。

本版本不需要 API 金鑰，不串接 ChatGPT 四項 MR，也不會自動寫成正式研究報告。
包含 Google 新聞搜尋 RSS（非官方保證長期支援），以及中央社、BBC RSS 等公開來源。
若來源無法存取，執行 JSON 會留下來源失敗紀錄。
RSS 標題可能帶偏誤、重複、不完整、錯誤；需要回到原文、官方資料及交叉來源查證。
公開 GitHub Pages 不能存放機密、API 金鑰、未公開報告或個人敏感資訊。

如使用 GitHub 預設的 Deploy from a branch 設定，本版的 Actions 蒐集成果不能自動發布：
務必將 Pages Source 改成 GitHub Actions 才能由工作流程完成更新。
