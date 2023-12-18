import React, { useState, useEffect } from "react";

function App() {
  const [ws, setWs] = useState(null);
  const [inputValue, setInputValue] = useState(0);
  const [response, setResponse] = useState({});
  const [isWebSocketOpen, setIsWebSocketOpen] = useState(false);

  const handleInputChange = (event) => {
    const value = parseInt(event.target.value, 10);
    setInputValue(value);
  };

  const initiateRequest = () => {
    if (inputValue > 20) {
      alert("Input value cannot be greater than 20");
      return;
    }
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.close();
    }
    const newWs = new WebSocket("ws://localhost:8000/ws");

    newWs.onopen = () => {
      console.log("WebSocket connection opened");
      setWs(newWs);
      setIsWebSocketOpen(true);
      newWs.send(inputValue.toString());
    };
  };

  useEffect(() => {
    if (!ws) return;

    ws.onmessage = (event) => {
      const responseData = JSON.parse(event.data);
      setResponse((prevResponse) => ({ ...prevResponse, ...responseData }));
    };

    ws.onclose = (event) => {
      console.log("WebSocket connection closed:", event);
      setIsWebSocketOpen(false);
    };
  }, [ws]);

  return (
    <div className="App">
      <label>
        Enter the number of stocks (not more than 20):
        <input type="number" value={inputValue} onChange={handleInputChange} />
      </label>
      <button onClick={initiateRequest}>Initiate Request</button>
      <div>
        {isWebSocketOpen &&
          Object.entries(response).map(([ticker, price]) => (
            <div key={ticker}>
              {ticker}: {price}
            </div>
          ))}
      </div>
    </div>
  );
}

export default App;
