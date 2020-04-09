import React, {Component} from "react";
import Card from './cards/Card';
import {render} from 'react-dom';

function arrayF(length){
    let array = new Array(length);
    for(let i = 0; i < length; i++){
        array[i] = false;
    }
    return(array);
}

class Hand extends Component {
    constructor(props){
        super(props);

        let selected = arrayF(props.cards.length);

        this.state = {
            cards: props.cards.map((x,i) => <Card card={x} onClick={(o,s) => this.updateSelected(o,s,i) } position={i}/>),
            codes: props.cards,
            selectedCards: selected,
            test: [0,1,2,3,4,5,6,7]
        };
        this.updateSelected = this.updateSelected.bind(this);
        this.playSelected = this.playSelected.bind(this);
        this.addCard = this.addCard.bind(this);
        this.pop = this.pop.bind(this);
        this.add = this.add.bind(this);
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
                alert(codes[i]);
                sendArray.push(codes[i]);
            } else {
                let p =newCodes.length
                let newCard = <Card card={codes[i]} onClick={(o,s) => this.updateSelected(o,s,p) } position={p} selected={false}/>;
                newCards.push(newCard);
                newCodes.push(codes[i]);
            }
        }
        alert("nc"+newCards.length);
        alert("sa"+sendArray.length);

    


        this.setState({
            cards: newCards,
            codes: newCodes,
            selectedCards: arrayF(newCodes.length)
        }, () => alert(this.state.codes.toString(),"new state"));

        

        alert(this.state.codes.length);

        this.forceUpdate();
    }


    addCard() {
        let newCards = [...this.state.codes];
        newCards.unshift("jr");

        this.setState({
            codes: newCards
        });
    }
    

    pop() {
        let array = [...this.state.test];
        array.pop();
        this.setState({
            test: array
        });
        alert(this.state.test);
    }

    add() {
        let array = [...this.state.test];
        array.push(array.length);
        this.setState({
            test: array
        });
        alert(this.state.test);
    }

    render() {

        let cards = [...this.state.codes];

        return (
            <div>
                
                <div>
                    {this.state.cards.map((x) => x)}
                </div>
                <div>
                    <PlayButton activate={this.playSelected}/>
                    <button onClick={this.addCard}>Add Card</button>
                    <button onClick={this.pop}>pop</button>
                    <button onClick={this.add}>push</button>
                    
                </div>
                <div>
                    <p>x</p><p>x</p><p>x</p><p>x</p><p>x</p><p>x</p><p>x</p><p>x</p><p>x</p><p>x</p><p>x</p>
                    {cards.map( (x) => <p>{x}</p> )}
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