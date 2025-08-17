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

      {/* 逐輪結果 */}
      {runResult && (
        <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded">
          <h3 className="text-lg font-semibold mb-3">🧠 逐輪預測與實際結果</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="text-left">
                  <th className="p-2">回合</th>
                  <th className="p-2">預測 勝/敗/平</th>
                  <th className="p-2">信心</th>
                  <th className="p-2">實際結果</th>
                  <th className="p-2">出拳(1/2)</th>
                </tr>
              </thead>
              <tbody>
                {runResult.per_round.map((r) => (
                  <tr key={r.round} className="odd:bg-white even:bg-blue-100/40">
                    <td className="p-2">{r.round}</td>
                    <td className="p-2">{(r.win*100).toFixed(1)}% / {(r.loss*100).toFixed(1)}% / {(r.draw*100).toFixed(1)}%</td>
                    <td className="p-2">{(r.confidence*100).toFixed(0)}%</td>
                    <td className="p-2">
                      {r.result === 1 ? '勝' : r.result === -1 ? '敗' : '平'}
                    </td>
                    <td className="p-2">{r.move1} / {r.move2}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* 彙總統計 */}
      {runResult && (
        <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded">
          <h3 className="text-lg font-semibold mb-2">📊 彙總統計</h3>
          <div className="grid grid-cols-2 md:grid-cols-6 gap-4 text-sm">
            <div>勝場: {runResult.summary.win}</div>
            <div>敗場: {runResult.summary.loss}</div>
            <div>平局: {runResult.summary.draw}</div>
            <div>勝率: {(runResult.summary.win_rate*100).toFixed(1)}%</div>
            <div>敗率: {(runResult.summary.loss_rate*100).toFixed(1)}%</div>
            <div>平率: {(runResult.summary.draw_rate*100).toFixed(1)}%</div>
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
