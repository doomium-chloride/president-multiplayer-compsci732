import React from "react";
import Card from './cards/Card';

function App() {
  var cardlist = [];
  for(let i = 13; i > 0; i--){
    cardlist.push("c"+i);
  }
  return (
    <div>
      {cardlist.map((x,i) => <Card card={x} position={i}/>)}
    </div>
  );
}

export default App;
