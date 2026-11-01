# APSS Virtual Research Studio

亞太安全與戰略研究獨立工作室｜虛擬研究室（公開展示及公開新聞線索蒐集原型）

網站：<https://apss-netizen.github.io/apss-virtual-research-studio/>

## v0.4（2026-11-01）

- 保留原有四項 MR 公開 RSS 線索蒐集、GitHub Actions 定時執行及靜態發布。
- 四席位公開資料板：每席可檢視來源成功數／總數、來源失敗數、待核實線索數及蒐集時間。點擊席位可篩選下方來源清單。
- A／B／C 全部保持「待判」：**尚未介接 AI 模型或人工審核程序，不能把新聞數當成已確認事件等級**。
- 原創 Canvas 立體投影場景：四位研究員、橘貓、邊境牧羊犬、咖啡與休息區。動畫可以啟用、停用或降低動態；與資料蒐集完全分離。
- 來源線索提供原始連結及公開發布時間，並標示「未證實／待人工核實」。
- 正式 ChatGPT 四項 MR 的排程、通知、A／B 警示及研究進度**沒有介接**，不可以把 RSS 來源抓取成功當作正式監測完成。

## 研究文件

目前文件直接置於 repository 根目錄（對應現有儲存庫結構）：

- [系統架構草案 v1.0](./APSS-Architecture-v1.0.md)
- [v0.4 開發清單](./V0.4-Implementation-Backlog.md)
- [事件資料格式範例](./event-record.example.json)

## 部署

已有 `.github/workflows/apss-collector.yml` 及 `scripts/collect_sources.py` 時，只需更新根目錄的 `index.html` 和本 `README.md`。

工作流程的原有 `push` 條件包含 `index.html`。成功執行後，會重新取得公開新聞線索並部署 GitHub Pages；若個別來源異常，仍應查看各席位錯誤紀錄。

### 不要上傳的資料

API 金鑰、私人研究筆記、未公開草稿與個人資料，均不能放進公開 GitHub Pages。
