import React from "react";

function Results(data){
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

export default Results;