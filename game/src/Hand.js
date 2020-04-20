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
            cards: props.cards.map((x,i) => <Card card={x} onClick={(o,s) => this.updateSelected(o,s,i) } position={i} ref={this.cards}/>),
            selectedCards: selected
        };
        this.updateSelected = this.updateSelected.bind(this);
        this.playSelected = this.playSelected.bind(this);
        this.addCard = this.addCard.bind(this);
        this.updateCards = this.updateCards.bind(this);
        this.resetSelected = this.resetSelected.bind(this);

        
    }

    updateSelected(card, selected, index) {    

        if(index < 0){
            alert("error, index is " + index);
        }

        let copy = [...this.state.selectedCards];

        copy[index] = selected == true;

        this.setState({
            selectedCards: copy
        });

        this.checkSelected();

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
                let newCard = <Card card={codes[i]} onClick={(o,s) => this.updateSelected(o,s,p) } position={p} ref={this.cards} selected={false}/>;
                newCards.push(newCard);
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

    updateCards() {
        let codes = this.state.codes;
        let newCards = codes.map((x,i) => <Card card={x} onClick={(o,s) => this.updateSelected(o,s,i) } position={i} />);
        this.setState({
            cards: newCards
        });
        
    }

    resetSelected() {
        // let codes = [...this.state.codes];
        // let newCards = codes.map((x,i) => <Card card={x} onClick={(o,s) => this.updateSelected(o,s,i) } position={i} selected={false}/>);
        // this.setState({
        //     cards: newCards,
        //     selectedCards: arrayF(newCards.length)
        // }, alert(this.state.selectedCards));
        console.log(this.cards);
    }

    checkSelected(){
        var list = this.state.cards.map((x) => x.props.selected);
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