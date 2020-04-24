import React, { Component } from "react";
import { render } from 'react-dom';
import { Redirect } from 'react-router-dom';
import axios from 'axios';

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
        this.handleChangeGame = this.handleChangeGame.bind(this);
        this.handleChangeMaxPlayers = this.handleChangeMaxPlayers.bind(this);
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
        alert('A name was submitted: ' + this.getRoomLink());
        if(this.state.roomCode){
            window.open(this.getRoomLink(), "_blank");
        }
    }

    makeGame(event){
        if(this.state.gameCode && this.state.maxPlayers){
            var self = this;
            let payload = {
                max_players: parseInt(this.state.maxPlayers),   
                game: this.state.gameCode
            };
            axios.post("http://localhost:8000/", payload)
                .then(function (response) {
                    // response is a JSON object. not a string
                    let data = response.data
                    // success is the attribute of the room code
                    self.setState({
                        newRoomCode: data.success
                    });
                })
                .catch(function (error) {
                    alert(error);
                });
            alert(this.state.maxPlayers);
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
                    <button onClick={this.joinGame}>Join Game</button>
                </form>
                <form>
                    <label>
                        Game code:
                        <input type="text" name="game" onChange={this.handleChangeGame}/>
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