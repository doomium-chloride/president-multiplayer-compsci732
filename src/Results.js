import React from "react";
import './styles/Popup.css';

function Results(data, ws){
    return(

        <div className="results">
            {data.map( x => mapper(x))}
            <button className="oldButton playAgainButton" onClick={() => playAgain(ws)}>Play Again?</button>
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