import React, { Component } from "react";
import axios from 'axios';
import './styles/Home.css';

let serverBase = "http://localhost:8000/";

class Home extends Component {
    constructor() {
        super()
        this.state = {
            roomCode: "",
            //gameCode: undefined,
            gameCode: 0,//0 = president(scum)
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

    joinGame() {
        if(this.state.roomCode){
            window.open(this.getRoomLink(), "_blank");
        }
    }

    makeGame(){
        if(this.state.maxPlayers){
            //cache this into self
            var self = this;
            //verify num of players is 2-4
            const players = parseInt(this.state.maxPlayers);
            if(players < 2 || players > 4){
                alert("only 2 to 4 players allowed");
                return null;//cancel make game
            }

            //create payload and send to server
            let payload = {
                max_players: players,   
                game_type: this.state.gameCode
            };
            axios.post(serverBase, payload)
                .then(function (response) {
                    // response is a JSON object. not a string
                    let data = response.data
                    // success is the attribute of the room code
                    self.setState({
                        newRoomCode: data.success,
                        roomCode: data.success
                    });
                })
                .catch(function (error) {
                    alert(error);
                });
        }
    }


    render(){
        return(
            <div className="homePage">
                <div className="joinGame">
                    <label>
                        Room Code:
                        <input type="text" value={this.state.roomCode} name="room-code" onChange={this.handleChangeRoom}/>
                    </label>
                    <button  className="joinGameBtn" onClick={this.joinGame}>Join Game</button>
                </div>
                <div className="startGame">
                    <label>                        
                        Number of players:
                        <input className="playerNum" type="number" min={2} max={4} name="max_players" onChange={this.handleChangeMaxPlayers}/>
                    </label>
                    <button className="startGameBtn" onClick={this.makeGame}>Start Game</button>
                    <p>{this.state.newRoomCode}</p>
                </div>
            </div>
        );
    }
    
}

export default Home;