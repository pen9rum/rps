/**
 * Observer 功能演示組件
 * 
 * 功能：
 * - 展示策略選擇和對戰
 * - 整合 LLM 預測功能
 * - 顯示損失函數計算結果
 * - 提供完整的 observer 實驗流程
 */

import React, { useState, useEffect } from 'react';
import { 
  getAllStrategies,
  observerRun
} from '../lib/api.js';

// 簡易折線圖元件（無第三方依賴，使用 SVG）
const LossLineChart = ({ points, width = 720, height = 240, label = 'union loss' }) => {
  // points: Array<{x:number, y:number}>
  const data = Array.isArray(points) ? points : [];
  if (data.length === 0) {
    return (
      <div className="w-full h-40 flex items-center justify-center text-sm text-gray-500">
        無可繪製的資料
      </div>
    );
  }
  const pad = 32;
  const xs = data.map(d => d.x);
  const ys = data.map(d => d.y);
  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);
  const dx = Math.max(1e-9, maxX - minX);
  const dy = Math.max(1e-9, maxY - minY);
  const sx = x => pad + (x - minX) / dx * (width - 2 * pad);
  const sy = y => height - pad - (y - minY) / dy * (height - 2 * pad);
  const dStr = data.map(p => `${sx(p.x)},${sy(p.y)}`).join(' ');
  const gridY = Array.from({ length: 4 }, (_, i) => minY + dy * i / 3);
  return (
    <svg width={width} height={height} className="bg-white rounded border border-gray-200">
      {/* grid */}
      {gridY.map((gy, i) => (
        <line key={i} x1={pad} x2={width - pad} y1={sy(gy)} y2={sy(gy)} stroke="#e5e7eb" strokeWidth="1" />
      ))}
      {/* axes */}
      <line x1={pad} y1={pad} x2={pad} y2={height - pad} stroke="#9ca3af" />
      <line x1={pad} y1={height - pad} x2={width - pad} y2={height - pad} stroke="#9ca3af" />
      {/* polyline */}
      <polyline points={dStr} fill="none" stroke="#2563eb" strokeWidth="2.5" />
      {/* points */}
      {data.map((p, i) => (
        <circle key={i} cx={sx(p.x)} cy={sy(p.y)} r={2.5} fill="#2563eb" />
      ))}
      {/* labels */}
      <text x={pad} y={16} fill="#374151" fontSize="12" fontWeight="600">{label}</text>
      <text x={8} y={pad} fill="#6b7280" fontSize="10">{maxY.toFixed(3)}</text>
      <text x={8} y={height - pad} fill="#6b7280" fontSize="10">{minY.toFixed(3)}</text>
    </svg>
  );
};

const ObserverDemo = () => {
  // 狀態管理
  const [strategies, setStrategies] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // 真實策略
  const [trueStrategy1, setTrueStrategy1] = useState('A');
  const [trueStrategy2, setTrueStrategy2] = useState('B');
  
  // 模型與回合設定
  const [model, setModel] = useState('deepseek'); // 'deepseek' | '4o-mini'
  const [rounds, setRounds] = useState(30);
  const [kWindow, setKWindow] = useState(''); // 可空

  // 觀察結果
  const [runResult, setRunResult] = useState(null);

  // 載入策略列表
  useEffect(() => {
    const loadStrategies = async () => {
      try {
        const result = await getAllStrategies();
        setStrategies(result.strategies);
      } catch (err) {
        setError('載入策略失敗: ' + err.message);
      }
    };
    loadStrategies();
  }, []);

  // 開始觀察
  const handleRun = async () => {
    setLoading(true);
    setError(null);
    setRunResult(null);
    try {
      const payload = {
        true_strategy1: trueStrategy1,
        true_strategy2: trueStrategy2,
        rounds: Number(rounds) || 1,
        model,
      };
      if (kWindow !== '') payload.k_window = Number(kWindow);
      const result = await observerRun(payload);
      setRunResult(result);
    } catch (err) {
      setError('開始觀察失敗: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const strategyOptions = Object.entries(strategies).map(([code, name]) => (
    <option key={code} value={code}>{code}: {name}</option>
  ));

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white shadow-lg rounded-lg">
      <h1 className="text-3xl font-bold text-center mb-6 text-gray-800">
        🧠 Observer 實驗系統
      </h1>
      
      {error && (
        <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      {/* 模型與回合設定 */}
      <div className="mb-6 p-4 bg-gray-50 rounded">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
          <div>
            <label className="block text-sm font-medium mb-2">模型</label>
            <select
              className="w-full p-2 border rounded"
              value={model}
              onChange={(e) => setModel(e.target.value)}
            >
              <option value="deepseek">DeepSeek (OpenRouter)</option>
              <option value="4o-mini">GPT-4o mini (OpenAI)</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">最高輪次 R</label>
            <input
              type="number"
              min="1"
              className="w-full p-2 border rounded"
              value={rounds}
              onChange={(e) => setRounds(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">k 視窗（可選）</label>
            <input
              type="number"
              min="1"
              className="w-full p-2 border rounded"
              value={kWindow}
              onChange={(e) => setKWindow(e.target.value)}
              placeholder="留空代表不限"
            />
          </div>
        </div>
        <div className="text-xs text-gray-500 mt-2">
          未配置金鑰時將自動使用備用邏輯。
        </div>
      </div>

      {/* 真實策略選擇區域 */}
      <div className="mb-8 p-6 bg-gray-50 rounded-lg">
        <h2 className="text-xl font-semibold mb-4">真實策略選擇</h2>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">真實策略 1</label>
            <select
              className="w-full p-2 border rounded"
              value={trueStrategy1}
              onChange={(e) => setTrueStrategy1(e.target.value)}
            >
              {strategyOptions}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">真實策略 2</label>
            <select
              className="w-full p-2 border rounded"
              value={trueStrategy2}
              onChange={(e) => setTrueStrategy2(e.target.value)}
            >
              {strategyOptions}
            </select>
          </div>
        </div>
      </div>

      {/* 操作按鈕 */}
      <div className="mb-8 flex flex-wrap gap-4">
        <button
          onClick={handleRun}
          disabled={loading}
          className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? '執行中...' : '🟢 開始觀察'}
        </button>
      </div>

      {/* 彙總統計（更新：最終猜測與趨勢） */}
      {runResult && (
        <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded">
          <h3 className="text-lg font-semibold mb-2">📊 彙總統計</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div>最終猜測：S1 → {runResult.final_guess?.s1 || '—'}，S2 → {runResult.final_guess?.s2 || '—'}</div>
            <div>當前 loss：{runResult.trend?.last != null ? runResult.trend.last.toFixed(4) : '—'}</div>
            <div>歷史最小：{runResult.trend?.min != null ? runResult.trend.min.toFixed(4) : '—'}</div>
          </div>
          {/* 新增：loss 折線圖 */}
          <div className="mt-4">
            {(() => {
              const pts = (runResult.per_round || [])
                .filter(r => r.union_loss != null)
                .map(r => ({ x: r.round, y: r.union_loss }));
              return <LossLineChart points={pts} />;
            })()}
          </div>
        </div>
      )}

      {/* 逐輪結果（更新：顯示辨識與 union loss） */}
      {runResult && (
        <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded">
          <h3 className="text-lg font-semibold mb-3">🧠 逐輪預測與實際結果</h3>
          {runResult.trend && (
            <div className="mb-3 text-sm text-gray-700">
              <span className="mr-4">當前 loss: {runResult.trend.last?.toFixed?.(4)}</span>
              <span className="mr-4">近5均值: {runResult.trend.avg_5?.toFixed?.(4)}</span>
              <span>歷史最小: {runResult.trend.min?.toFixed?.(4)}</span>
            </div>
          )}
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="text-left">
                  <th className="p-2">回合</th>
                  <th className="p-2">S1 猜測</th>
                  <th className="p-2">S2 猜測</th>
                  <th className="p-2">union loss</th>
                  <th className="p-2">Δ</th>
                  <th className="p-2">勝負</th>
                  <th className="p-2">出拳(1/2)</th>
                </tr>
              </thead>
              <tbody>
                {runResult.per_round.map((r) => (
                  <tr key={r.round} className="odd:bg-white even:bg-blue-100/40">
                    <td className="p-2">{r.round}</td>
                    <td className="p-2">{r.guess_s1 ? `${r.guess_s1.top1} (${((r.guess_s1.probs?.[r.guess_s1.top1]||0)*100).toFixed(0)}%)` : '—'}</td>
                    <td className="p-2">{r.guess_s2 ? `${r.guess_s2.top1} (${((r.guess_s2.probs?.[r.guess_s2.top1]||0)*100).toFixed(0)}%)` : '—'}</td>
                    <td className="p-2">{r.union_loss != null ? r.union_loss.toFixed(4) : '—'}</td>
                    <td className="p-2">{r.delta != null ? r.delta.toFixed(4) : '—'}</td>
                    <td className="p-2">{r.result === 1 ? '勝' : r.result === -1 ? '敗' : '平'}</td>
                    <td className="p-2">{r.move1} / {r.move2}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      

      {/* 矩陣結果預覽 */}
      {false && <div />}

      {/* 使用說明 */}
      <div className="mt-8 p-4 bg-gray-100 rounded">
        <h3 className="font-semibold mb-2">📖 使用說明</h3>
        <div className="text-sm text-gray-700 space-y-1">
          <div>1. 選擇真實策略 A/B</div>
          <div>2. 選擇模型與最高輪次 R（可選 k 視窗）</div>
          <div>3. 按「開始觀察」執行，畫面會顯示逐輪預測與實際結果，以及彙總統計</div>
        </div>
      </div>
    </div>
  );
};

export default ObserverDemo;
