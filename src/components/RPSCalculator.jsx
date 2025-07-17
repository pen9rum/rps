// src/components/RPSCalculator.jsx
import React, { useState, useMemo } from 'react';
import doraemonIcon from '../icon/doraemon.png';

const RPSCalculator = () => {
  // --- 静态策略 A–P ---
  const baseStrategies = {
    A: { name: 'A (纯剪刀)', rock: 0,   paper: 0,   scissors: 1   },
    B: { name: 'B (纯石头)', rock: 1,   paper: 0,   scissors: 0   },
    C: { name: 'C (纯布)',   rock: 0,   paper: 1,   scissors: 0   },
    D: { name: 'D (随机)',   rock: 0.333, paper: 0.333, scissors: 0.334 },
    E: { name: 'E (石头+布)', rock: 0.5, paper: 0.5,   scissors: 0   },
    F: { name: 'F (石头+剪刀)', rock: 0.5, paper: 0,     scissors: 0.5 },
    G: { name: 'G (布+剪刀)',   rock: 0,   paper: 0.5,   scissors: 0.5 },
    H: { name: 'H (偏爱石头)', rock: 0.5, paper: 0.25,  scissors: 0.25 },
    I: { name: 'I (偏爱布)',   rock: 0.25,paper: 0.5,   scissors: 0.25 },
    J: { name: 'J (偏爱剪刀)', rock: 0.25,paper: 0.25,  scissors: 0.5 },
    K: { name: 'K (石头主布次)', rock: 0.5, paper: 0.333, scissors: 0.167 },
    L: { name: 'L (石头主剪次)', rock: 0.5, paper: 0.167, scissors: 0.333 },
    M: { name: 'M (布主石次)',   rock: 0.333,paper: 0.5,   scissors: 0.167 },
    N: { name: 'N (布主剪次)',   rock: 0.167,paper: 0.5,   scissors: 0.333 },
    O: { name: 'O (剪主石次)',   rock: 0.333,paper: 0.167, scissors: 0.5   },
    P: { name: 'P (剪主布次)',   rock: 0.167,paper: 0.333, scissors: 0.5   },
  };

  // --- 动态策略 X/Y/Z ---
  const strategies = {
    ...baseStrategies,
    X: { name: 'X (赢前一拳)' },
    Y: { name: 'Y (输前一拳)' },
    Z: { name: 'Z (跟前一拳)' },
  };
  const keys = Object.keys(strategies);

  // --- State hooks ---
  const [infoKey, setInfoKey]   = useState(keys[0]);
  const [actualA, setActualA]   = useState(keys[0]);
  const [actualB, setActualB]   = useState(keys[1]);
  const [predA, setPredA]       = useState(keys[0]);
  const [predB, setPredB]       = useState(keys[1]);

  // --- Helper functions ---
  const resolveDist = (key, oppDist) => {
    if (baseStrategies[key]) return baseStrategies[key];
    if (key === 'X') return { rock: oppDist.scissors, paper: oppDist.rock,   scissors: oppDist.paper };
    if (key === 'Y') return { rock: oppDist.paper,    paper: oppDist.scissors, scissors: oppDist.rock };
    if (key === 'Z') return { rock: oppDist.rock,     paper: oppDist.paper,    scissors: oppDist.scissors };
    return { rock: 0, paper: 0, scissors: 0 };
  };

  const calculateMatchup = (k1, k2) => {
    const opp1 = baseStrategies[k2] || { rock:1/3, paper:1/3, scissors:1/3 };
    const opp2 = baseStrategies[k1] || { rock:1/3, paper:1/3, scissors:1/3 };
    const s1 = resolveDist(k1, opp1);
    const s2 = resolveDist(k2, opp2);
    let wins=0, losses=0, draws=0;
    wins   += s1.rock     * s2.scissors;
    wins   += s1.scissors * s2.paper;
    wins   += s1.paper    * s2.rock;
    losses += s1.scissors * s2.rock;
    losses += s1.paper    * s2.scissors;
    losses += s1.rock     * s2.paper;
    draws  += s1.rock     * s2.rock;
    draws  += s1.paper    * s2.paper;
    draws  += s1.scissors * s2.scissors;
    return { wins:wins*100, losses:losses*100, draws:draws*100 };
  };

  const allMatchups = useMemo(() => {
    const table = {};
    keys.forEach(k1 => {
      table[k1] = {};
      keys.forEach(k2 => {
        table[k1][k2] = calculateMatchup(k1, k2);
      });
    });
    return table;
  }, [keys]);

  const toProb = d => ({ win:d.wins/100, draw:d.draws/100, loss:d.losses/100 });

  const computeCELoss = (t, p) =>
    - (t.win  * Math.log(p.win  + 1e-12)
      + t.draw * Math.log(p.draw + 1e-12)
      + t.loss * Math.log(p.loss + 1e-12));

  const computeBrier = (t, p) =>
    (p.win - t.win)**2 + (p.draw - t.draw)**2 + (p.loss - t.loss)**2;

  const computeEV    = d => (d.wins - d.losses)/100;
  const computeEVLoss = (tDist, pDist) =>
    Math.pow(computeEV(tDist) - computeEV(pDist), 2);

  // --- Compute current distributions & losses ---
  const trueDist  = allMatchups[actualA][actualB];
  const predDist  = allMatchups[predA][predB];
  const tProb     = toProb(trueDist);
  const pProb     = toProb(predDist);

  const ceLoss    = computeCELoss(tProb, pProb);
  const brierLoss = computeBrier(tProb, pProb);
  const evLoss    = computeEVLoss(trueDist, predDist);
  const unionLoss = (ceLoss + brierLoss + evLoss) / 3;

  const fmt = v => `${v.toFixed(1)}%`;

  return (
    <div className="max-w-7xl mx-auto p-6 bg-white shadow-lg rounded-lg">
      <h1 className="text-3xl font-bold text-center mb-6 text-gray-800">
        🪨📄✂️ Tom 4 AI Evaluation on Gaming
      </h1>

      {/* 策略说明 + 图标 */}
      <div className="mb-6 flex items-center space-x-4">
        <label className="block text-sm font-medium">Strategy Dictionary:</label>
        <select
          className="mt-1 rounded border-gray-300"
          value={infoKey}
          onChange={e => setInfoKey(e.target.value)}
        >
          {keys.map(k => <option key={k} value={k}>{k}</option>)}
        </select>
        <div className="flex items-center space-x-2">
          <img src={doraemonIcon} alt="Doraemon" className="w-8 h-8" />
          <span className="text-base font-medium">{strategies[infoKey].name}</span>
        </div>
      </div>

      {/* Actual / Pred 选择 */}
      <div className="mb-6 grid grid-cols-2 md:grid-cols-4 gap-4">
        {['Actual A','Actual B','Pred A','Pred B'].map((label, idx) => (
          <div key={label}>
            <label className="block text-sm font-medium">{label}</label>
            <select
              className="mt-1 block w-full rounded border-gray-300"
              value={[actualA, actualB, predA, predB][idx]}
              onChange={e =>
                [setActualA, setActualB, setPredA, setPredB][idx](e.target.value)
              }
            >
              {keys.map(k => <option key={k} value={k}>{k}</option>)}
            </select>
          </div>
        ))}
      </div>

      {/* 结果展示 */}
      <div className="mb-8 p-6 bg-gray-50 rounded-lg text-center">
        <p className="text-lg">
          Win Rate: <span className="font-semibold">{fmt(trueDist.wins)}</span> /
          Lose Rate: <span className="font-semibold">{fmt(trueDist.losses)}</span> /
          Even: <span className="font-semibold">{fmt(trueDist.draws)}</span>
        </p>
        <p className="mt-2 text-lg">
          Pred Win: <span className="font-semibold">{fmt(predDist.wins)}</span> /
          Lose: <span className="font-semibold">{fmt(predDist.losses)}</span> /
          Even: <span className="font-semibold">{fmt(predDist.draws)}</span>
        </p>
        <div className="mt-4 space-y-1">
          <p>Cross‐Entropy Loss: <span className="font-semibold">{ceLoss.toFixed(4)}</span></p>
          <p>Brier Score:          <span className="font-semibold">{brierLoss.toFixed(4)}</span></p>
          <p>EV Loss:              <span className="font-semibold">{evLoss.toFixed(4)}</span></p>
          <p className="text-2xl font-bold text-red-600">
            Union Loss:           {unionLoss.toFixed(4)}
          </p>
        </div>
      </div>

      {/* 全矩阵对战 */}
      <div className="overflow-x-auto shadow-md rounded-lg">
        <table className="min-w-full divide-y divide-gray-200 table-auto text-sm">
          <thead className="sticky top-0 bg-blue-600">
            <tr>
              <th className="px-4 py-3 text-left text-white font-medium uppercase sticky left-0 bg-blue-600 z-10">
                Strategy
              </th>
              {keys.map(k => (
                <th key={k} className="px-4 py-3 text-center text-white font-medium uppercase">
                  {k}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {keys.map(k1 => (
              <tr key={k1} className="hover:bg-gray-100 even:bg-gray-50">
                <td className="px-4 py-2 font-semibold bg-gray-50 sticky left-0 z-10 whitespace-nowrap">
                  {k1}
                </td>
                {keys.map(k2 => {
                  const t    = allMatchups[k1][k2];
                  const tP   = toProb(t);
                  const pP   = pProb;
                  const loss = ((computeCELoss(tP,pP)
                                + computeBrier(tP,pP)
                                + computeEVLoss(t,predDist)) / 3).toFixed(2);
                  const hue  = Math.round((1 - t.wins/100) * 120);
                  const bg   = `hsl(${hue},70%,90%)`;
                  return (
                    <td
                      key={k2}
                      className="px-4 py-2 text-center whitespace-nowrap"
                      style={{ background: bg }}
                    >
                      <div className="font-semibold text-xs">{fmt(t.wins)}</div>
                      <div className="text-gray-600 text-xs">{fmt(t.losses)}</div>
                      <div className="text-gray-500 text-xs">{fmt(t.draws)}</div>
                      <div className="mt-1 text-[9px] text-red-600">L {loss}</div>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default RPSCalculator;
