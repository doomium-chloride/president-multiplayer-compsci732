import React from "react";
import './styles/Popup.css';

function Results(data, ws){
    let roles = [];
    let players = [];
    for(let i = 0; i < data.length; i++){
        const info = data[i];
        const role = info[0];
        const player = info[1];
        roles.push(role);
        players.push(player);
    }
    return(

        <div className="results">
            {data.map( x => mapper(x))}
            <button className="playAgainButton" onClick={() => playAgain(ws)}>Play Again?</button>
        </div>
    )
}

function mapper(data){
    return(
        <div>
            {data[0]} : {data[1]}
        </div>
    )
}

function playAgain(ws){
    let msg = {
        type: "ready"
    }
    ws.send(JSON.stringify(msg));
}

export default Results;