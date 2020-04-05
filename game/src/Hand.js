import React, {Component} from "react";
import Card from './cards/Card';
import {render} from 'react-dom';

class Hand extends Component {
    constructor(props){
        super(props)
        this.state = {
            cards: [],
            codes: props.cards,
            selectedCards: []
        };
        this.updateSelected = this.updateSelected.bind(this);
        this.state.codes.map((x,i) => this.state.cards.push(<Card card={x} onClick={(obj,s) => this.updateSelected(obj,s) } position={i}/>));
       
    }

    updateSelected(card, selected) {
        

        if(selected){
            this.state.selectedCards.push(card);
        } else{
            let index = this.state.selectedCards.indexOf(card);
            if (index > -1) {
                this.state.selectedCards.splice(index, 1);
              }
        }

    }

    render() {


        return (
            <div>
              {this.state.cards.map((x) => x)}
            </div>
          );
    }
}

export default Hand;