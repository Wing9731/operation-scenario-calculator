# 營運情境試算工具

以 Python、Streamlit、Pandas 與 Plotly 製作的繁體中文互動式營運儀表板。所有金額以新台幣（NT$）呈現，修改輸入後即時更新財務摘要、比較表格與圖表。

## 功能

- 輸入招生人數、課程價格、固定成本、每人變動成本與其他額外成本
- 分別調整保守、一般、樂觀情境的招生人數與課程價格；成本條件共用基本假設
- 計算營收、成本、營運利潤、利潤率與損益兩平招生人數
- 以互動式圖表比較各情境營收與成本、招生人數與利潤曲線，以及損益兩平點
- 金額與招生人數限制為非負值；營收為零時利潤率顯示「不適用」；每人價格不高於變動成本時提示無法損益兩平
- 在側欄「編輯介面文字」中，可依分類修改儀表板標題、欄位名稱、情境名稱、摘要、表格欄名、圖表文字及說明；儲存後只套用於目前瀏覽工作階段，各訪客設定互不影響

## 專案檔案

- `app.py`：Streamlit 儀表板介面與圖表
- `finance.py`：財務公式及利潤曲線資料整理
- `requirements.txt`：相依套件與相容版本範圍

## 安裝與啟動（Windows PowerShell）

建議使用 Python 3.10 至 3.13。建立獨立環境可避免與電腦中其他 Python 套件版本互相影響：

```powershell
cd "C:\Users\JC USER\Documents\Codex\2026-11-05\referenced-chatgpt-conversation-this-is-an\outputs\營運情境試算工具"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

啟動後在瀏覽器開啟終端機顯示的網址，通常是 <http://localhost:8501>。停止服務時回到 PowerShell 按 `Ctrl+C`。

若 PowerShell 不允許啟用虛擬環境，可略過啟用步驟，直接以虛擬環境中的 Python 安裝和啟動：

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

## 部署成公開網站（Streamlit Community Cloud）

1. 將 `app.py`、`finance.py`、`requirements.txt`、`.streamlit/config.toml` 及本 README 上傳至 GitHub 儲存庫根目錄。不要上傳 `.venv` 或任何密碼、金鑰。
2. 前往 [Streamlit Community Cloud](https://share.streamlit.io/) 並以 GitHub 登入。
3. 選擇 **Create app**，指定 GitHub 儲存庫、`main` 分支與 `app.py`，再部署。
4. 部署完成後，Community Cloud 會提供 `https://<自選名稱>.streamlit.app` 公開網址，可分享給其他人。

Community Cloud 的部署必須能讀取 GitHub 儲存庫；若要讓任何人直接開啟網站，請使用公開儲存庫及公開 App。介面文字編輯設定只存在於當前工作階段，不會被其他訪客覆寫。

## 計算方式

- 總營收 = 招生人數 × 每位學生課程價格
- 總成本 = 固定成本 + 招生人數 × 每人變動成本 + 其他額外成本
- 營運利潤 = 總營收 − 總成本
- 利潤率 = 營運利潤 ÷ 總營收 × 100%；營收為零時不適用
- 損益兩平招生人數 = 向上取整〔（固定成本 + 其他額外成本）÷（每人課程價格 − 每人變動成本）〕

預設情境以一般情境為基準：保守情境招生人數降低 20%、價格降低 5%；樂觀情境招生人數提高 20%、價格提高 5%。情境值可直接修改。
