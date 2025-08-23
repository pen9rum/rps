import React from 'react';
import RPSCalculator from './components/RPSCalculator';

function App() {
  console.log('App component is rendering');
  return (
    <div className="min-h-screen bg-gray-100">
      <div className="p-4 bg-blue-100 text-blue-800">
        <h1>Debug: App is loading</h1>
      </div>
      <RPSCalculator />
    </div>
  );
}

export default App;
