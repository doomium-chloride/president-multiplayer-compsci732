import React, {Component, createRef} from "react";
import Card from './cards/Card';
import './styles/Selection.css';
import {front2back} from './utils/card-code-translator';

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
            selectedCards: selected
        };
        this.updateSelected = this.updateSelected.bind(this);
        this.playSelected = this.playSelected.bind(this);
        this.skip = this.skip.bind(this);
        

    }

    //When the player selects or unselects a card, this method updates the states.

    updateSelected(selected, index) {    

        if(index < 0){
            alert("error, index is " + index);
        }

        let copy = [...this.state.selectedCards];

        //This is to enforce only 1 can be selected
        //check if any other except for index is selected
        for(let i = 0; i < copy.length; i++){
            if(i == index){
                continue;
            }
            if(copy[i]){
                copy[i] = false;
            }
        }

        //flip truth
        copy[index] = !selected;

        this.setState({
            selectedCards: copy
        });

    }

    //This removes the selected cards from the hand

    playSelected() {
        if(this.props.freeze){
            return
        }
        let length = this.props.cards.length;

        let codes = [...this.props.cards];
        let selected = [...this.state.selectedCards];

        let newCodes = [];
        let sendArray = [];

        for(let i = 0; i < length; i++){
            if (selected[i]){
                sendArray.push(codes[i]);
            } else {
                newCodes.push(codes[i]);
            }
        }

        //If no card has been selected do nothing
        if(sendArray.length <= 0){
            return
        }
        if(sendArray[0] == ""){
            return
        }


        this.sendMoves(sendArray);

        this.setState({
            //codes: newCodes,
            selectedCards: arrayF(newCodes.length)
        });
        

    }

    sendMoves(cards){
        const card = cards[0]
        const msg = {
            type: "game_move",
            move: front2back(card)
        }
        this.props.ws.send(JSON.stringify(msg));
    }


    skip(){
        if(this.props.freeze){
            return
        }
        const msg = {
            type: "game_move",
            move: "skip"
        }
        this.props.ws.send(JSON.stringify(msg));
    }


    render() {

        let codes = this.props.cards;
        let selected = this.state.selectedCards
        let cards = []
        for(let i = 0; i < codes.length; i++){
            cards.push(<Card key={"card"+i} card={codes[i]} onClick={(o,s) => this.updateSelected(s,i) } position={i} selected={selected[i]}/>)
        }

        return (
            <div className="hand">
                
                <div>
                    {cards}
                </div>
                <div className="handButtons">
                    <PlayButton activate={this.playSelected}/>
                    <button className="skipButton" onClick={this.skip} type="button">Skip</button>
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
            <button className="playButton" onClick={this.func} type="button">Play</button>
        );
    }
}

export default Hand;