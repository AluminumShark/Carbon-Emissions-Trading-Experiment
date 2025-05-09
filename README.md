# oTree 碳市場與對照實驗專案

> 本專案基於 **oTree — An open‑source platform for laboratory, online, and field experiments** (Chen, Schonger & Wickens, 2016) 所打造，適用於線上或實驗室環境中探討碳排放政策與市場互動的行為反應。請於任何學術或公開發表時引用該文獻，詳見「引用文獻」章節。

---

## 1. 實驗概觀

| App                      |  處理組別  |  核心機制                              |  檔案夾                    |
| ------------------------ | ------ | ---------------------------------- | ----------------------- |
| **Stage\_CarbonTrading** |  碳權交易組 |  玩家先於即時雙向盤買賣碳權，再決定生產量；生產量受持有碳權數量限制 |  `Stage_CarbonTrading/` |
| **Stage\_CarbonTax**     |  碳稅組   |  玩家直接決定生產量，但須依排碳量繳納固定稅率            |  `Stage_CarbonTax/`     |
| **Stage\_Control**       |  對照組   |  玩家自由決定生產量，無碳權／碳稅限制                |  `Stage_Control/`       |
| **Stage\_MUDA**          |  純交易組  |  移除產業背景與環境變數，僅進行物品買賣               |  `Stage_MUDA/`          |

每個 App 皆包含下列元素：

* `models.py` — 定義常數、玩家與群組欄位及計分方式。
* `pages.py` — 實驗流程與頁面互動（若採單檔結構則與 models 合併）。
* `templates/` — Bootstrap 5 ＋ FontAwesome 風格的 HTML 頁面。

---

## 2. 快速開始

### 2.1 前置需求

* Python ≥ 3.9（建議 3.11）
* PostgreSQL（正式環境建議）或 SQLite（測試）
* `pip`, `virtualenv` / `venv`

### 2.2 安裝步驟

```bash
# 1. 取得原始碼
$ git clone <YOUR_REPO_URL> carbon-experiment && cd carbon-experiment

# 2. 建立並啟動虛擬環境
$ python -m venv venv
$ source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安裝相依套件
$ pip install --upgrade pip wheel
$ pip install otree>=5.10  # 或使用 requirements.txt

# 4. 啟動開發伺服器
$ otree devserver
```

預設網址：[http://localhost:8000](http://localhost:8000)
管理後台：[http://localhost:8000/admin](http://localhost:8000/admin)
若為首次使用請執行 `otree resetdb` 以建立資料庫。

---

## 3. 生產部署建議

### 3.1 環境變數

| 變數                                | 功能                          |
| --------------------------------- | --------------------------- |
| `OTREE_PRODUCTION=1`              |  啟用生產模式（停用自動 reload、啟用安全設定） |
| `OTREE_AUTH_LEVEL=STUDY`          |  限制登入網址，僅受試者憑連結／房間代號進入      |
| `ADMIN_PASSWORD=<your‑strong‑pw>` |  後台管理密碼                     |
| `DATABASE_URL=postgres://…`       |  PostgreSQL 連線字串            |
| `OTREE_SESSION_CONFIGS`           |  （進階）於環境層覆寫 session config  |

### 3.2 Docker 部署

```dockerfile
FROM otreeorg/otree:latest
COPY . /app
RUN pip install -r /app/requirements.txt  # 若有
CMD ["otree", "prodserver", "0.0.0.0:80"]
```

```bash
# docker-compose.yml 範例
services:
  web:
    build: .
    ports: ["8000:80"]
    environment:
      - OTREE_PRODUCTION=1
      - ADMIN_PASSWORD=${ADMIN_PASSWORD}
      - DATABASE_URL=${DATABASE_URL}
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER=postgres
      POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      POSTGRES_DB=otree
```

* **Railway / Render / Fly.io** — 可直接以 Docker 或 Heroku buildpack 部署。
* **Heroku**（付費方案） — 加入 `.runtime.txt` 指定 Python 版本並啟用 `heroku-postgresql` 附加元件。

### 3.3 靜態檔案

oTree 5 內建 WhiteNoise；若使用 Docker 或 Render 可直接在同一容器服務靜態檔案。

### 3.4 大規模實驗

* 增加 Gunicorn worker：`OTREE_NUM_WORKERS=4`
* 使用多地區 edge proxy（Cloudflare Tunnel / Nginx）減少延遲
* 透過 `ROOMS` 配置分批進入，避免單一房間過載

---

## 4. 資料輸出

結束實驗後可於管理後台下載 csv/Excel，或以 `otree export_data` 指令批次匯出。各 App 的玩家／群組欄位即為主要分析變數。

---

## 5. 引用文獻 (Citation)

> Chen, D. L., Schonger, M., & Wickens, C. (2016). *oTree—An open‑source platform for laboratory, online, and field experiments.* **Journal of Behavioral and Experimental Finance, 9**, 88–97. [https://doi.org/10.1016/j.jbef.2015.12.001](https://doi.org/10.1016/j.jbef.2015.12.001)

若需 BibTeX：

```bibtex
@article{chen2016otree,
  title   = {oTree—An open-source platform for laboratory, online, and field experiments},
  author  = {Chen, Daniel L. and Schonger, Martin and Wickens, Chris},
  journal = {Journal of Behavioral and Experimental Finance},
  volume  = {9},
  pages   = {88--97},
  year    = {2016},
  issn    = {2214-6350},
  doi     = {10.1016/j.jbef.2015.12.001}
}
```

---

## 6. 授權與致謝 (License & Acknowledgment)

本專案部分功能基於 [oTree 開源平台](https://www.otree.org/) 所建構，遵循其授權條款（MIT License）。oTree 的原始開發者包括 Daniel L. Chen、Martin Schonger 與 Christopher Wickens，並已在以下文獻中發表：

> Chen, D. L., Schonger, M., & Wickens, C. (2016). *oTree—An open-source platform for laboratory, online, and field experiments.* **Journal of Behavioral and Experimental Finance, 9**, 88–97. [https://doi.org/10.1016/j.jbef.2015.12.001](https://doi.org/10.1016/j.jbef.2015.12.001)

請於使用本專案進行實驗並公開發表時，務必引用上述文獻，亦請尊重原始開發者之著作權與授權聲明。更多授權細節請參見專案內附之 [`LICENSE`](./LICENSE) 檔案。

---
