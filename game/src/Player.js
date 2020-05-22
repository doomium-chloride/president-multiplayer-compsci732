import React from "react";
import './styles/Player.css';
import cardBack from './cards/card-back-star.png';

function Player(props){
    let player = props.name ? props.name : "no name";
    let cards = props.cards;
    return(
        <div className="player">
            <div className="number">
                {player}
            </div>
            <div className="cardback">
                <img src={cardBack}/>
                <div>{cards}</div>
            </div>
        </div>
    );
}

export default Player;