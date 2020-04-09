import React, {Component, createRef} from "react";
import Hand from './Hand';
import {render} from 'react-dom';

class Controls extends Component {

    constructor(props){
        super(props);
        this.state = {
            cardlist: props.cards
        }
        this.hand = React.createRef();
        this.playSelected = this.playSelected.bind(this);
    }

    playSelected(){
        alert("here");
        alert(this.hand.state.selectedCards[0])
        let selected = this.hand.playSelected();
        alert("clicked");
        let outStr = "";
        for(let card of selected.values()){
            outStr += card + " ";
        }
        alert(outStr);
    }

    render(){
        return (
            <div>
              <Hand cards={this.state.cardlist} ref={this.hand}/>
              <PlayButton activate={this.playSelected}/>
            </div>
          );
    }
  
}

class PlayButton extends Component {
    constructor(props){
        super(props);
        this.func = props.activate;
    }

    render(){
        return(
            <button onClick={this.func} type="button">Play</button>
        );
    }
}

export default Controls;
