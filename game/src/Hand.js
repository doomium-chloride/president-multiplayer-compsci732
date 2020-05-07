import React, {Component, createRef} from "react";
import Card from './cards/Card';
import {render} from 'react-dom';
import './Selection.css';

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

        this.state = {
            codes: props.cards,
            selectedCards: selected
        };
        this.updateSelected = this.updateSelected.bind(this);
        this.playSelected = this.playSelected.bind(this);
        this.addCard = this.addCard.bind(this);

        //testing
        this.reset = this.reset.bind(this);
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

        this.setState({
            codes: newCodes,
            cards: newCards,
            selectedCards: arrayF(newCodes.length)
        }, this.resetSelected);
        

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


    render() {

        let codes = this.state.codes;
        let selected = this.state.selectedCards
        let cards = []
        for(let i = 0; i < codes.length; i++){
            cards.push(<Card card={codes[i]} onClick={(o,s) => this.updateSelected(s,i) } position={i} selected={selected[i]}/>)
        }

        return (
            <div style={{position: "absolute"}}>
                
                <div>
                    {cards}
                </div>
                <div style={{position: "relative", top: "400px"}}>
                    <PlayButton activate={this.playSelected}/>
                    <button onClick={this.addCard}>Add Card</button>
                    <button onClick={this.reset}>Reset</button>
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