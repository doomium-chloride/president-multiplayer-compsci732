import React, {Component} from "react";
import './Player.css';

function Player(props){
    let player = "Player:" + props.number;
    let cards = "Cards:" + props.cards;
    return(
        <div className="player">
            <div className="number">
                {player}
            </div>
            <div>
                {cards}
            </div>
        </div>
    );
}

export default Player;