import React, {Component, createRef} from "react";
import Card from './cards/Card';
import {render} from 'react-dom';
import './styles/Selection.css';

//creates an array of false of length length
//for example arrayF(3) = [false,false,false]

function arrayF(length){
    let array = new Array(length);
    for(let i = 0; i < length; i++){
        array[i] = false;
    }
    return(array);
}

//class for the hand of a player
//a hand is the cards a player holds

class Hand extends Component {
    constructor(props){
        super(props);

        let selected = arrayF(props.cards.length);
        this.cards = createRef();

        this.ws = props.ws;

        this.state = {
            codes: props.cards,
            selectedCards: selected
        };
        this.updateSelected = this.updateSelected.bind(this);
        this.playSelected = this.playSelected.bind(this);
        this.skip = this.skip.bind(this);
        
        //testing
        this.reset = this.reset.bind(this);
        this.addCard = this.addCard.bind(this);

    }

    //When the player selects or unselects a card, this method updates the states.

    updateSelected(selected, index) {    

        if(index < 0){
            alert("error, index is " + index);
        }

        let copy = [...this.state.selectedCards];
        //flip truth
        copy[index] = !selected;

        this.setState({
            selectedCards: copy
        });

    }

    //This removes the selected cards from the hand

    playSelected() {
        let length = this.state.codes.length;

        let codes = [...this.state.codes];
        let selected = [...this.state.selectedCards];

        let newCodes = [];
        let newCards = [];
        let sendArray = [];

        for(let i = 0; i < length; i++){
            if (selected[i]){
                sendArray.push(codes[i]);
            } else {
                let p =newCodes.length
                newCodes.push(codes[i]);
            }
        }

        alert(sendArray);

        //this.sendMoves(sendArray);

        this.setState({
            codes: newCodes,
            cards: newCards,
            selectedCards: arrayF(newCodes.length)
        });
        

    }

    sendMoves(cards){
        const msg = {
            type: "game_move",
            player: "channel_id",
            move: cards,
            special: "does nothing"
        }

        this.ws.send(JSON.stringify(msg));
    }

    //Old testing method.
    //Can remove it later.

    addCard() {
        let newCards = [...this.state.codes];
        newCards.unshift("jr");

        this.setState({
            codes: newCards
        }, this.updateCards);

        
    }

    reset() {
        //for testing
        let cardlist = [];
        for(let i = 13; i > 0; i--){
            cardlist.push("c"+i);
        }
        cardlist.push("h4");
        this.setState({
            codes: cardlist,
            selectedCards: arrayF(cardlist.length)
        });
    }

    skip(){
        const msg = {
            type: "game_move",
            player: "channel_id",
            move: "skip",
            special: "does nothing"
        }
        this.ws.send(JSON.stringify(msg));
    }


    render() {

        let codes = this.state.codes;
        let selected = this.state.selectedCards
        let cards = []
        for(let i = 0; i < codes.length; i++){
            cards.push(<Card key={i} card={codes[i]} onClick={(o,s) => this.updateSelected(s,i) } position={i} selected={selected[i]}/>)
        }

        return (
            <div className="hand">
                
                <div>
                    {cards}
                </div>
                <div className="handButtons">
                    <PlayButton activate={this.playSelected}/>
                    <button onClick={this.skip} type="button">Skip</button>
                </div>
            </div>
          );
    }
}

//the button to play the selected cards

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

export default Hand;