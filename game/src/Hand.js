import React, {Component, createRef} from "react";
import Card from './cards/Card';
import {render} from 'react-dom';
import './Selection.css';

function arrayF(length){
    let array = new Array(length);
    for(let i = 0; i < length; i++){
        array[i] = false;
    }
    return(array);
}

var selectShiftHeight = "30px";

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

        
    }

    updateSelected(card, selected, index) {    

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


    addCard() {
        let newCards = [...this.state.codes];
        newCards.unshift("jr");

        this.setState({
            codes: newCards
        }, this.updateCards);

        
    }



    


    render() {

        let codes = this.state.codes;
        let selected = this.state.selectedCards
        let cards = []
        for(let i = 0; i < codes.length; i++){
            cards.push(<Card card={codes[i]} onClick={(o,s) => this.updateSelected(o,s,i) } position={i} selected={selected[i]}/>)
        }

        return (
            <div style={{position: "absolute"}}>
                
                <div>
                    {cards}
                </div>
                <div style={{position: "relative", top: "400px"}}>
                    <PlayButton activate={this.playSelected}/>
                    <button onClick={this.addCard}>Add Card</button>
                    <button onClick={this.resetSelected}>Reset</button>
                    <button onClick={this.forceUpdate}>Update</button>
                </div>
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

export default Hand;