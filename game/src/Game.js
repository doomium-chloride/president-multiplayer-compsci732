import React, {Component} from "react";
import Player from './Player';
import Hand from './Hand';

//for testing
var cardlist = [];
  for(let i = 13; i > 0; i--){
    cardlist.push("c"+i);
  }
  cardlist.push("h4");

class Game extends Component {
    constructor(props){
        super(props);

    }

    render(){
        return(
            <div>
                <Player number={0} cards={10}/>
                <Player number={1} cards={20}/>
                <Player number={2} cards={30}/>
                <Hand cards={cardlist}/>
            </div>
        );
    }
}

export default Game;