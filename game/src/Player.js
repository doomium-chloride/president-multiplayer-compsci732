import React from "react";
import './styles/Player.css';
import cardBack from './cards/card-back-star.png';

function Player(props){
    const player = props.name ? props.name : "no name";
    const cards = props.cards;
    const currentTurn = props.currentTurn ? "thisTurn" : "notThisTurn";
    const classes = ["cardback", currentTurn].join(' ');
    return(
        <div className="player">
            <div className="number">
                {player}
            </div>
            <div className={classes}>
                <img src={cardBack}/>
                <div>{cards}</div>
            </div>
        </div>
    );
}

export default Player;