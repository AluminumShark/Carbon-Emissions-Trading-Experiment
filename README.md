# 🌱 Carbon Emissions Trading Experiment Platform

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11+-3776ab?logo=python&logoColor=white)](https://python.org)
[![oTree](https://img.shields.io/badge/oTree-6.0-00a67d)](https://otree.org)
[![uv](https://img.shields.io/badge/uv-package%20manager-5a67d8)](https://docs.astral.sh/uv/)
[![Ruff](https://img.shields.io/badge/Ruff-linter-d7ff64)](https://docs.astral.sh/ruff/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**碳排放交易實驗平台** | An experimental economics platform for carbon emission policy research

[English](#-english) • [繁體中文](#-繁體中文)

</div>

---

## 🌍 English

An experimental economics platform built on oTree, designed to study the impact of different carbon reduction policies on firm production behavior.

### ✨ Features

| Treatment Group | Description |
|----------------|-------------|
| 🔬 **Control** | Baseline experiment without carbon emission restrictions |
| 💰 **Carbon Tax** | Policy experiment with carbon tax based on emission levels |
| 📈 **Carbon Trading** | Carbon permit market with real-time trading |
| 🎓 **MUDA Practice** | Trading system operation training |

**Core Capabilities:**
- Real-time WebSocket trading system
- Intelligent order matching engine
- Comprehensive data tracking & export
- Flexible YAML configuration
- Modern responsive UI

### 🚀 Quick Start

#### Prerequisites

- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/) package manager (recommended)

#### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/Carbon-Emissions-Trading-Experiment.git
cd Carbon-Emissions-Trading-Experiment

# Install dependencies with uv
uv sync

# Initialize database and start server
uv run otree resetdb
uv run otree devserver
```

Visit `http://localhost:8000` to begin the experiment.

#### Alternative: Traditional pip

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
otree resetdb
otree devserver
```

### ⚙️ Configuration

Edit `configs/experiment_config.yaml` to switch between modes:

```yaml
experiment_mode:
  test_mode_enabled: true  # true = test mode, false = production mode
```

| Setting | Test Mode | Production Mode |
|---------|-----------|-----------------|
| Players per group | 2 | 15 |
| Rounds | 3 | 12 |
| Dominant firms | 1 | 3 |
| Trading time | 60s | 120s |

### 📁 Project Structure

```
Carbon-Emissions-Trading-Experiment/
├── 📁 configs/                 # Configuration files
│   ├── experiment_config.yaml  # Main experiment settings
│   └── config.py               # Config loader
├── 📁 utils/                   # Shared utilities
│   ├── shared_utils.py         # Core utility functions
│   ├── trading_utils.py        # Trading engine
│   └── database_cleaner.py     # Database management
├── 📁 Stage_Control/           # Control group app
├── 📁 Stage_CarbonTax/         # Carbon tax group app
├── 📁 Stage_CarbonTrading/     # Carbon trading group app
├── 📁 Stage_MUDA/              # Practice trading app
├── 📁 Stage_Payment_Info/      # Payment calculation app
├── 📁 Stage_Survey/            # Post-experiment survey
├── 📁 Stage_WaitStart/         # Initial waiting room
├── 📁 docs/                    # Documentation
├── pyproject.toml              # Project configuration
├── settings.py                 # oTree settings
└── requirements.txt            # Dependencies (legacy)
```

### 🛠️ Development

```bash
# Run linter
uv run ruff check .

# Auto-fix lint issues
uv run ruff check . --fix

# Format code
uv run ruff format .
```

### 📚 Documentation

- [System Functions & Logic](docs/系統功能與運作邏輯說明.md)
- [Data Codebook](docs/codebook.md)
- [Database Cleaner Guide](docs/資料庫清理工具.md)

---

## 🌏 繁體中文

基於 oTree 框架開發的經濟學實驗平台，專門用於研究不同碳減排政策對廠商生產行為的影響。

### ✨ 平台特色

| 實驗組別 | 說明 |
|---------|------|
| 🔬 **對照組** | 無碳排放限制的基準實驗 |
| 💰 **碳稅組** | 基於碳排放量徵收稅金的政策實驗 |
| 📈 **碳交易組** | 具備即時交易功能的碳權市場實驗 |
| 🎓 **MUDA 練習組** | 交易系統操作訓練實驗 |

**核心功能：**
- 即時 WebSocket 交易系統
- 智慧訂單撮合引擎
- 完整數據追蹤與匯出
- 彈性 YAML 配置管理
- 現代化響應式介面

### 🚀 快速開始

#### 系統需求

- Python 3.11 或更高版本
- [uv](https://docs.astral.sh/uv/) 套件管理器（推薦）

#### 安裝步驟

```bash
# 複製專案
git clone https://github.com/your-username/Carbon-Emissions-Trading-Experiment.git
cd Carbon-Emissions-Trading-Experiment

# 使用 uv 安裝相依套件
uv sync

# 初始化資料庫並啟動伺服器
uv run otree resetdb
uv run otree devserver
```

啟動後請造訪 `http://localhost:8000` 開始實驗。

#### 替代方案：傳統 pip 安裝

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
otree resetdb
otree devserver
```

### ⚙️ 配置設定

編輯 `configs/experiment_config.yaml` 切換模式：

```yaml
experiment_mode:
  test_mode_enabled: true  # true = 測試模式, false = 正式模式
```

| 設定項目 | 測試模式 | 正式模式 |
|---------|---------|---------|
| 每組人數 | 2 人 | 15 人 |
| 回合數 | 3 回合 | 12 回合 |
| 主導廠商數量 | 1 個 | 3 個 |
| 交易時間 | 60 秒 | 120 秒 |

### 🔬 實驗組別說明

#### 對照組 (Control)
- **流程**：介紹 → 生產決策 → 結果顯示
- **特點**：無碳排放限制，建立純市場機制的基準數據

#### 碳稅組 (Carbon Tax)
- **流程**：介紹 → 生產決策 → 結果顯示
- **特點**：碳稅 = 碳排放量 × 稅率

#### 碳交易組 (Carbon Trading)
- **流程**：介紹 → 碳權交易 → 生產決策 → 結果顯示
- **特點**：參與者先進行碳權交易，生產量受碳權持有量限制

#### MUDA 練習組
- **流程**：介紹 → 交易練習 → 結果顯示
- **特點**：純交易操作練習，用於熟悉交易介面

### 📊 核心機制

#### 生產成本計算
```
總成本 = Σ(邊際成本係數 × i + 隨機擾動), i = 1 to 生產量
```

#### 碳權交易機制
- **訂單類型**：限價買單、限價賣單
- **撮合規則**：價格優先、時間優先
- **即時更新**：WebSocket 技術實現即時市場狀態同步

### 📁 專案架構

```
Carbon-Emissions-Trading-Experiment/
├── 📁 configs/                 # 配置檔案
│   ├── experiment_config.yaml  # 主要實驗設定
│   └── config.py               # 配置載入器
├── 📁 utils/                   # 共用工具模組
│   ├── shared_utils.py         # 核心工具函數
│   ├── trading_utils.py        # 交易引擎
│   └── database_cleaner.py     # 資料庫管理
├── 📁 Stage_Control/           # 對照組應用
├── 📁 Stage_CarbonTax/         # 碳稅組應用
├── 📁 Stage_CarbonTrading/     # 碳交易組應用
├── 📁 Stage_MUDA/              # 練習交易應用
├── 📁 Stage_Payment_Info/      # 報酬計算應用
├── 📁 Stage_Survey/            # 實驗後問卷
├── 📁 Stage_WaitStart/         # 初始等待室
├── 📁 docs/                    # 文檔
├── pyproject.toml              # 專案配置
├── settings.py                 # oTree 設定
└── requirements.txt            # 相依套件（舊版）
```

### 🛠️ 開發指南

```bash
# 執行程式碼檢查
uv run ruff check .

# 自動修正問題
uv run ruff check . --fix

# 格式化程式碼
uv run ruff format .
```

### 🚢 部署

#### 環境變數
```bash
OTREE_ADMIN_PASSWORD=your_password
OTREE_SECRET_KEY=your_secret_key
DATABASE_URL=postgresql://user:pass@host:port/dbname
```

#### Docker 部署
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install uv && uv sync --frozen
CMD ["uv", "run", "otree", "prodserver", "0.0.0.0:8000"]
```

### 📚 相關文檔

- [系統功能與運作邏輯說明](docs/系統功能與運作邏輯說明.md)
- [數據編碼簿](docs/codebook.md)
- [資料庫清理工具說明](docs/資料庫清理工具.md)

### 📄 授權

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案。

### 🤝 技術支援

如有技術問題或研究合作需求，請透過 [GitHub Issues](https://github.com/your-username/Carbon-Emissions-Trading-Experiment/issues) 提出。
