import React, { Component } from "react";
import { render } from 'react-dom'
import { Redirect } from 'react-router-dom'

class Home extends Component {
    constructor() {
        super()
        this.state = {
            roomCode: undefined,
            gameCode: undefined,
            maxPlayers: undefined,
            newRoomCode: undefined
        };

        this.handleChangeRoom = this.handleChangeRoom.bind(this);
        this.joinGame = this.joinGame.bind(this);
        this.makeGame = this.makeGame.bind(this);
    }

    handleChangeRoom(event){
        this.setState({roomCode: event.target.value});
    }

    handleChangeGame(event){
        this.setState({gameCode: event.target.value});
    }

    handleChangeMaxPlayers(event){
        this.setState({maxPlayers: event.target.value});
    }

    getRoomLink(){
        if(this.state.roomCode){
            return "/" + this.state.roomCode;
        }
    }

    joinGame(event) {
        alert('A name was submitted: ' + this.state.value);
        if(this.state.roomCode){
            return <Redirect to={this.getRoomLink()} />
        }
    }

    makeGame(event){
        if(this.state.gameCode && this.state.maxPlayers){
            let payload = {
                max_players:4, 
                game_type:1
            };
            let xhttp = new XMLHttpRequest(); 
            xhttp.onreadystatechange = function() {
                if (this.readyState == 4 && this.status == 200) {
                    this.setState({
                        newRoomCode: this.responseText
                    });
                }
            };
            xhttp.open("POST", "/", true);
            xhttp.send(payload); 
        }
    }


    render(){
        return(
            <div>
                <form>
                    <label>
                        Room Code:
                        <input type="text" name="room-code" onChange={this.handleChangeRoom}/>
                    </label>
                    <button onClick={this.handleSubmit}>Join Game</button>
                </form>
                <form  action="/" method="post">
                    <label>
                        Game code:
                        <input type="number" name="game" onChange={this.handleChangeGame}/>
                        Max number of players:
                        <input type="number" name="max_players" onChange={this.handleChangeMaxPlayers}/>
                    </label>
                    <button onClick={this.makeGame}>Start Game</button>
                    <p>{this.state.newRoomCode}</p>
                </form>
            </div>
        );
    }
    
}

export default Home;