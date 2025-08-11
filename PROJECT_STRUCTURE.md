# 📂 RPS Calculator - 專案結構與開發指南

本文件詳細說明專案的檔案與目錄結構，包含前端（Vite + React）與後端（FastAPI + Python），以及完整的開發指導。  
請所有開發人員依據此文件了解各檔案用途，方便分工與維護。

---

## 🎯 專案特色

- **策略模擬**: 支援多種出拳策略（固定、隨機、反應型、統計型）
- **LLM 整合**: 可整合大型語言模型進行預測和決策
- **評估指標**: 提供 MAE、RMSE、Brier Score、相關係數等評估指標
- **現代化架構**: 前後端分離，支援容器化部署
- **即時分析**: 快速模擬和結果視覺化

---

## 📂 根目錄結構

```
rps/
├── backend/                # 後端 FastAPI 程式碼與設定
├── node_modules/            # 前端套件依賴（自動生成，勿修改）
├── package.json             # 前端專案設定與套件依賴
├── package-lock.json        # 前端套件版本鎖定檔
├── postcss.config.js        # 前端 PostCSS 設定（CSS 處理流程）
├── readme                   # 專案說明文件（簡易版）
├── tailwind.config.js       # Tailwind CSS 設定檔
├── vite.config.js           # Vite 開發與打包設定（含 API proxy）
├── index.html               # 前端入口 HTML（掛載 React）
├── README.md                # 完整專案說明
├── PROJECT_STRUCTURE.md     # 本文件
├── QUICK_START.md           # 快速啟動指令
└── test_api.html            # API 測試頁面
```

---

## 🟢 前端程式碼結構

### `src/` 目錄
存放前端 React 原始碼與資源。

```
src/
├── index.jsx                # React 應用程式進入點，掛載到 index.html
├── App.jsx                  # 前端主元件，負責路由與主要頁面結構
├── index.css                # 全域 CSS 樣式設定
├── components/              # React 元件集合
│   └── RPSCalculator.jsx    # 剪刀石頭布主要 UI 與邏輯元件
├── lib/                     # API 呼叫與工具函式
│   └── api.js               # 封裝呼叫後端 API 的函式
└── icon/                    # 靜態圖片資源
    └── doraemon.png         # 哆啦A夢圖片
```

### 主要檔案說明

#### **`index.jsx`**
React 應用程式的進入點，負責將 `<App />` 元件掛載到 `index.html` 的 root 節點。

#### **`App.jsx`**
主應用容器，可在此處設定全域狀態、路由或共同佈局。

#### **`index.css`**
全域 CSS 樣式，包括 TailwindCSS 的基礎設置。

#### **`components/RPSCalculator.jsx`**
核心功能元件，提供剪刀石頭布的前端互動邏輯、結果顯示、以及呼叫後端 API 取得模擬與分析結果。

#### **`lib/api.js`**
前端 API 呼叫模組，封裝 `fetch` 請求，包括：
- `simulate()`：呼叫 `/api/v1/simulate`
- `observerPredict()`：呼叫 `/api/v1/observer/predict`
- `playerAct()`：呼叫 `/api/v1/player/act`
- `evaluate()`：呼叫 `/api/v1/evaluate`

---

## 🔧 後端程式碼結構

### `backend/` 目錄
Python + FastAPI 實作，負責遊戲邏輯、策略模擬、模型呼叫與評估。

```
backend/
├── app/
│   ├── main.py               # FastAPI 主入口，掛載路由與中介層
│   ├── core/
│   │   └── config.py         # 環境變數與全域設定
│   ├── api/
│   │   └── v1/
│   │       ├── routes_simulate.py  # 提供遊戲模擬 API
│   │       ├── routes_observer.py  # 提供觀察者（LLM belief）預測 API
│   │       ├── routes_player.py    # 提供玩家（LLM 決策） API
│   │       └── routes_eval.py      # 提供評估指標計算 API
│   ├── domain/
│   │   ├── strategies.py     # 各種出拳策略實作
│   │   ├── simulator.py      # 模擬對戰流程與勝率計算
│   │   └── metrics.py        # 評估指標計算（MAE、RMSE、Brier、相關係數等）
│   ├── services/
│   │   └── llm.py            # LLM 呼叫封裝（觀察者與玩家邏輯）
│   └── schemas/
│       ├── simulate.py       # 模擬 API 的 request/response 定義
│       ├── observer.py       # 觀察者 API 的 request/response 定義
│       ├── player.py         # 玩家 API 的 request/response 定義
│       └── evaluate.py       # 評估 API 的 request/response 定義
├── requirements.txt          # 後端 Python 套件依賴
├── env.example               # 環境變數範例檔（API Key、模型設定等）
└── Dockerfile                # 後端容器化設定（可選）
```

### 主要檔案說明

#### **`main.py`**
啟動 FastAPI 應用程式，設定跨域（CORS）、健康檢查、掛載 API 路由。

#### **`core/config.py`**
管理專案環境變數（如 API key、允許來源等）。

#### **`api/v1/routes_simulate.py`**
接收策略設定，回傳模擬對戰的勝率（Ground Truth）。

#### **`api/v1/routes_observer.py`**
模擬 LLM 根據策略描述預測勝率與置信度。

#### **`api/v1/routes_player.py`**
模擬 LLM 根據歷史出拳決策下一步行動。

#### **`api/v1/routes_eval.py`**
計算 LLM belief 與 Ground Truth 的各種差異與校準指標。

#### **`domain/strategies.py`**
定義多種出拳策略（固定、隨機、反應型、統計型）。

#### **`domain/simulator.py`**
控制對戰流程，呼叫策略並統計結果。

#### **`domain/metrics.py`**
提供評估方法（MAE、RMSE、Brier score、皮爾森/Kendall 相關係數等）。

#### **`services/llm.py`**
集中管理 LLM API 呼叫邏輯，觀察者與玩家行為在此實作。

#### **`schemas/*.py`**
使用 Pydantic 定義 API 的請求與回應格式，保證資料格式一致性。

---

## 🎮 支援的策略類型

### 1. 固定策略 (Fixed)
- **描述**: 始終出同一種手勢
- **參數**: `param` - 手勢類型 (0=石頭, 1=布, 2=剪刀)
- **使用場景**: 測試對手對固定模式的應對能力

### 2. 隨機策略 (Random)
- **描述**: 完全隨機出拳
- **參數**: 無
- **使用場景**: 作為基準策略，測試其他策略的表現

### 3. 反應型策略 (Reactive)
- **描述**: 根據上一輪結果調整策略
- **參數**: `on_win`, `on_loss`, `on_draw` - 對應情況下的出拳
- **使用場景**: 模擬人類的學習和適應行為

### 4. 統計型策略 (Frequency)
- **描述**: 分析對手歷史出拳頻率，針對最常出現的手勢進行反制
- **參數**: 無
- **使用場景**: 對抗有固定模式的對手

---

## 📊 評估指標說明

系統提供多種評估指標來衡量 LLM 預測的準確性：

### **MAE (Mean Absolute Error)**
- **定義**: 平均絕對誤差
- **用途**: 衡量預測值與真實值的平均偏差
- **範圍**: 0 到 1，越小越好

### **RMSE (Root Mean Square Error)**
- **定義**: 均方根誤差
- **用途**: 對大誤差更敏感，懲罰極端錯誤
- **範圍**: 0 到 1，越小越好

### **Brier Score**
- **定義**: 預測校準指標
- **用途**: 評估概率預測的校準程度
- **範圍**: 0 到 1，越小越好

### **Pearson Correlation**
- **定義**: 皮爾森相關係數
- **用途**: 衡量預測值與真實值的線性相關性
- **範圍**: -1 到 1，越接近 1 越好

### **Kendall Correlation**
- **定義**: 肯德爾相關係數
- **用途**: 衡量預測值與真實值的排序相關性
- **範圍**: -1 到 1，越接近 1 越好

---

## 🔄 資料流概述

### 1. **模擬階段（simulate）**
```
前端選擇策略 → 呼叫 /api/v1/simulate → 後端執行策略對戰模擬 → 回傳勝率矩陣
```

### 2. **觀察者階段（observer）**
```
前端提供策略描述 → 呼叫 /api/v1/observer/predict → 後端 LLM 模型推測勝率 → 回傳預測值與置信度
```

### 3. **玩家階段（player）**
```
前端提供歷史出拳紀錄 → 呼叫 /api/v1/player/act → 後端 LLM 或策略模型選擇下一手
```

### 4. **評估階段（evaluate）**
```
前端提供 LLM 預測與 Ground Truth → 呼叫 /api/v1/evaluate → 回傳 MAE、RMSE、Brier、相關係數等指標
```

---

## 🛠️ 開發指南

### 添加新策略

1. **在 `backend/app/domain/strategies.py` 中實作新策略類**
   ```python
   class NewStrategy:
       def __init__(self, param1, param2):
           self.param1 = param1
           self.param2 = param2
       
       def next(self, history):
           # 實作策略邏輯
           return move
   ```

2. **在 `backend/app/api/v1/routes_simulate.py` 中註冊新策略**
   ```python
   def build_strategy(spec):
       if spec.kind == "new_strategy": 
           return NewStrategy(spec.param1, spec.param2)
   ```

3. **更新 `backend/app/schemas/simulate.py` 中的策略類型定義**
   ```python
   class StrategySpec(BaseModel):
       kind: Literal["fixed","random","reactive","frequency","new_strategy"]
       param: Optional[int] = None
       param1: Optional[int] = None
       param2: Optional[int] = None
   ```

### 添加新 API 端點

1. **在 `backend/app/schemas/` 中定義請求/回應模型**
   ```python
   class NewAPIRequest(BaseModel):
       field1: str
       field2: int
   
   class NewAPIResponse(BaseModel):
       result: str
       data: dict
   ```

2. **在 `backend/app/api/v1/` 中創建路由文件**
   ```python
   from fastapi import APIRouter
   from ...schemas.new_api import NewAPIRequest, NewAPIResponse
   
   router = APIRouter(prefix="/new", tags=["new"])
   
   @router.post("/endpoint", response_model=NewAPIResponse)
   def new_endpoint(req: NewAPIRequest):
       # 實作邏輯
       return NewAPIResponse(result="success", data={})
   ```

3. **在 `backend/app/main.py` 中註冊路由**
   ```python
   from app.api.v1.routes_new import router as new_router
   app.include_router(new_router, prefix=settings.API_PREFIX)
   ```

4. **在 `src/lib/api.js` 中添加前端調用函數**
   ```javascript
   export async function newAPI(body) {
     const res = await fetch('/api/v1/new/endpoint', {
       method: 'POST', 
       headers: { 'Content-Type': 'application/json' },
       body: JSON.stringify(body),
     });
     if (!res.ok) throw new Error(await res.text());
     return res.json();
   }
   ```

### 代碼風格規範

#### **後端 (Python)**
- 使用 Black 格式化代碼：`black backend/`
- 遵循 PEP 8 規範
- 使用類型提示 (Type Hints)
- 函數和類別要有文檔字串 (docstring)

#### **前端 (JavaScript/JSX)**
- 使用 Prettier 格式化代碼：`npx prettier --write src/`
- 遵循 ESLint 規範
- 使用 ES6+ 語法
- 組件使用函數式寫法

---

## 🧪 測試指南

### 後端測試
```bash
cd backend
pytest
```

### 前端測試
```bash
npm test
```

### API 測試
可以使用專案根目錄的 `test_api.html` 文件進行 API 功能測試。

### 手動測試流程
1. 啟動後端：`uvicorn app.main:app --reload --port 8002`
2. 啟動前端：`npm run dev`
3. 訪問 http://localhost:5173
4. 測試各種策略組合
5. 檢查 API 回應是否正確

---

## 🔧 配置說明

### 環境變數
創建 `.env` 文件並設置以下變數：
```env
# 模型配置
MODEL_PROVIDER=mock
OPENAI_API_KEY=your_openai_api_key_here

# 服務配置
API_PREFIX=/api/v1
CORS_ALLOW_ORIGINS=["*"]
```

### Vite 代理配置
`vite.config.js` 中的代理設定：
```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://127.0.0.1:8002',
      changeOrigin: true,
    },
  },
}
```

---


## commit message 規範
- `feat:` 新功能
- `fix:` 修復錯誤
- `docs:` 文檔更新
- `style:` 代碼格式調整
- `refactor:` 重構
- `test:` 測試相關
- `chore:` 構建過程或輔助工具的變動
