import React from "react";
import Hand from './Hand';

var cardlist = [];
  for(let i = 13; i > 0; i--){
    cardlist.push("c"+i);
  }
  cardlist.push("h4");

function App() {
  
  return (
    <div>
      <Hand cards={cardlist}/>
    </div>
  );
}

export default App;
