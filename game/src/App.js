import React from "react";
import Hand from './Hand';

function App() {
  var cardlist = [];
  for(let i = 13; i > 0; i--){
    cardlist.push("c"+i);
  }
  return (
    <div>
      <Hand cards={cardlist}/>
    </div>
  );
}

export default App;
