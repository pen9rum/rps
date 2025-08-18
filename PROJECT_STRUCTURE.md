# RPS Belief Evaluation System - 專案結構文檔

## 📁 專案概覽

這是一個用於評估 LLM 信念的石頭剪刀布實驗系統，包含 FastAPI 後端和 React 前端。

## 🏗️ 整體架構

```
rps/
├── backend/                 # FastAPI 後端
│   ├── app/
│   │   ├── main.py         # 應用程式入口點
│   │   ├── core/           # 核心配置
│   │   ├── api/            # API 路由層
│   │   ├── domain/         # 業務邏輯層
│   │   ├── services/       # 外部服務整合
│   │   └── schemas/        # 資料模型定義
│   ├── requirements.txt    # Python 依賴
│   ├── Dockerfile         # Docker 配置
│   └── env.example        # 環境變數範例
├── src/                    # React 前端
│   ├── components/         # React 組件
│   ├── lib/               # 工具函數
│   └── icon/              # 靜態資源
├── vite.config.js         # Vite 配置
├── package.json           # Node.js 依賴
└── index.html             # HTML 入口
```

## 🔧 後端架構 (backend/)

### 核心模組

#### `app/main.py` - 應用程式入口點
- **功能**: FastAPI 應用程式設定和路由註冊
- **主要職責**:
  - 設定 CORS 中間件
  - 註冊所有 API 路由
  - 提供健康檢查端點
- **API 端點**:
  - `GET /health` - 健康檢查
  - 整合所有子路由模組

#### `app/core/config.py` - 配置管理
- **功能**: 應用程式配置和環境變數管理
- **主要職責**:
  - 載入環境變數
  - 定義 API 配置
  - 管理 LLM 服務設定
- **配置項目**:
  - `API_PREFIX`: API 路徑前綴
  - `CORS_ALLOW_ORIGINS`: CORS 設定
  - `MODEL_PROVIDER`: LLM 服務提供商
  - `OPENAI_API_KEY`: OpenAI API 金鑰

### API 層 (`app/api/v1/`)

#### `routes_simulate.py` - 模擬路由
- **功能**: 策略模擬 API
- **端點**: `POST /api/v1/simulate`
- **功能**: 執行策略對戰模擬

#### `routes_observer.py` - 觀察者路由
- **功能**: 觀察者預測 API
- **端點**: `POST /api/v1/observer/predict`
- **功能**: 使用 LLM 預測策略對戰結果

#### `routes_strategies.py` - 策略計算路由
- **功能**: 策略相關計算 API
- **端點**:
  - `GET /api/v1/strategies/all` - 獲取所有策略
  - `POST /api/v1/strategies/matchup` - 計算策略對戰
  - `POST /api/v1/strategies/matrix` - 計算策略矩陣

#### `routes_player.py` - 玩家路由
- **功能**: 玩家行動 API
- **端點**: `POST /api/v1/player/act`
- **功能**: 決定玩家下一步行動

#### `routes_eval.py` - 評估路由
- **功能**: 評估指標 API
- **端點**: `POST /api/v1/evaluate`
- **功能**: 計算各種評估指標

### 業務邏輯層 (`app/domain/`)

#### `strategies.py` - 策略定義和計算
- **功能**: 石頭剪刀布策略的核心邏輯
- **主要內容**:
  - 靜態策略定義 (A-P)
  - 動態策略定義 (X/Y/Z)
  - 策略對戰計算
  - 動態策略迭代收斂
- **核心函數**:
  - `calculate_matchup()`: 計算對戰結果
  - `resolve_dist()`: 解析動態策略
  - `iterate_dists()`: 迭代計算穩態
  - `get_all_strategies()`: 獲取策略列表

#### `simulator.py` - 遊戲模擬器
- **功能**: 執行遊戲模擬
- **主要職責**:
  - 單回合遊戲邏輯
  - 多回合模擬
  - 統計計算
- **核心函數**:
  - `play_round()`: 執行單回合
  - `simulate()`: 模擬多回合

#### `metrics.py` - 評估指標
- **功能**: 計算各種評估指標
- **主要指標**:
  - MAE (平均絕對誤差)
  - RMSE (均方根誤差)
  - Brier Score
  - 相關係數

### 服務層 (`app/services/`)

#### `llm.py` - LLM 服務整合
- **功能**: 整合外部 LLM 服務
- **主要職責**:
  - OpenAI API 整合
  - 策略預測
  - 備用預測邏輯
- **核心功能**:
  - `estimate_payoff()`: 主要預測函數
  - `call_openai_for_prediction()`: OpenAI API 調用
  - `analyze_strategy()`: 策略分析
  - `fallback_prediction()`: 備用預測

### 資料模型層 (`app/schemas/`)

#### `simulate.py` - 模擬相關模型
- **功能**: 定義 API 請求和回應格式
- **主要模型**:
  - `SimulateRequest/Response`: 模擬請求/回應
  - `StrategyMatchupRequest/Response`: 策略對戰
  - `StrategyMatrixRequest/Response`: 策略矩陣
  - `AllStrategiesResponse`: 策略列表

#### `observer.py` - 觀察者相關模型
- **功能**: 觀察者預測的資料模型
- **主要模型**:
  - `ObserverPredictReq/Resp`: 預測請求/回應

#### `player.py` - 玩家相關模型
- **功能**: 玩家行動的資料模型
- **主要模型**:
  - `PlayerActReq/Resp`: 行動請求/回應

#### `evaluate.py` - 評估相關模型
- **功能**: 評估指標的資料模型
- **主要模型**:
  - `EvaluateRequest/Response`: 評估請求/回應

## 🎨 前端架構 (src/)

### 核心組件

#### `App.jsx` - 主應用程式組件
- **功能**: React 應用程式根組件
- **主要職責**: 路由管理和整體佈局

#### `components/RPSCalculator.jsx` - 主要計算器組件
- **功能**: 石頭剪刀布計算器的主要介面
- **主要職責**:
  - 策略選擇和顯示
  - 對戰結果計算
  - 矩陣視覺化
  - 損失函數計算
- **狀態管理**:
  - 策略選擇狀態
  - 計算結果狀態
  - 顯示模式狀態

### 工具模組

#### `lib/api.js` - API 客戶端
- **功能**: 與後端 API 的統一介面
- **主要函數**:
  - `simulate()`: 策略模擬
  - `observerPredict()`: 觀察者預測
  - `calculateStrategyMatchup()`: 策略對戰
  - `calculateStrategyMatrix()`: 策略矩陣
  - `getAllStrategies()`: 獲取策略列表
- **錯誤處理**: 統一的錯誤處理和回應解析

### 靜態資源

#### `icon/doraemon.png` - 圖示資源
- **功能**: 應用程式圖示

## 🔄 資料流程

### 1. 策略計算流程
```
前端選擇策略 → API 請求 → 後端驗證 → 策略計算 → 返回結果 → 前端顯示
```

### 2. LLM 預測流程
```
策略描述 → OpenAI API → 預測結果 → 信心度評估 → 返回前端
```

### 3. 矩陣計算流程
```
選擇預測策略 → 計算完整矩陣 → 計算損失函數 → 視覺化顯示
```

## 🚀 運行方式

### 後端啟動
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### 前端啟動
```bash
npm run dev
```

### 環境配置
```bash
# 複製環境變數範例
cp backend/env.example backend/.env

# 設定 OpenAI API 金鑰
echo "OPENAI_API_KEY=your_api_key_here" >> backend/.env
```

## 📊 API 端點總覽

| 方法 | 端點 | 功能 | 描述 |
|------|------|------|------|
| GET | `/health` | 健康檢查 | 檢查服務狀態 |
| POST | `/api/v1/simulate` | 策略模擬 | 執行策略對戰模擬 |
| POST | `/api/v1/observer/predict` | 觀察者預測 | LLM 預測對戰結果 |
| POST | `/api/v1/strategies/matchup` | 策略對戰 | 計算兩個策略的對戰結果 |
| POST | `/api/v1/strategies/matrix` | 策略矩陣 | 計算完整的策略矩陣 |
| GET | `/api/v1/strategies/all` | 策略列表 | 獲取所有可用策略 |
| POST | `/api/v1/player/act` | 玩家行動 | 決定玩家下一步行動 |
| POST | `/api/v1/evaluate` | 評估指標 | 計算評估指標 |

## 🔧 技術棧

### 後端
- **FastAPI**: Web 框架
- **Pydantic**: 資料驗證
- **OpenAI**: LLM 服務
- **NumPy**: 數值計算

### 前端
- **React**: UI 框架
- **Vite**: 建構工具
- **Tailwind CSS**: 樣式框架

### 開發工具
- **Docker**: 容器化
- **ESLint**: 程式碼檢查
- **Prettier**: 程式碼格式化

## 📝 開發指南

### 添加新策略
1. 在 `backend/app/domain/strategies.py` 中添加策略定義
2. 更新 `BASE_STRATEGIES` 或 `DYNAMIC_STRATEGIES`
3. 測試策略計算邏輯

### 添加新 API 端點
1. 在 `app/api/v1/` 中創建新的路由檔案
2. 在 `app/schemas/` 中定義資料模型
3. 在 `app/main.py` 中註冊路由
4. 在 `src/lib/api.js` 中添加前端調用函數

### 整合新的 LLM 服務
1. 在 `app/services/llm.py` 中添加新的服務函數
2. 更新配置管理
3. 添加錯誤處理和備用邏輯

## 🧪 測試

### API 測試
```bash
# 健康檢查
curl http://localhost:8000/health

# 策略對戰
curl -X POST http://localhost:8000/api/v1/strategies/matchup \
  -H "Content-Type: application/json" \
  -d '{"strategy1": "A", "strategy2": "B"}'
```

### 前端測試
```bash
# 啟動開發伺服器
npm run dev

# 訪問應用程式
open http://localhost:5173
```

## 📚 參考資料

- [FastAPI 文檔](https://fastapi.tiangolo.com/)
- [React 文檔](https://react.dev/)
- [OpenAI API 文檔](https://platform.openai.com/docs)
- [石頭剪刀布策略理論](https://en.wikipedia.org/wiki/Rock_paper_scissors)
