import React, { Component } from "react";
import { render } from 'react-dom';
import { Redirect } from 'react-router-dom';
import axios from 'axios';
import './styles/Home.css';

let serverBase = "http://localhost:8000/";

class Home extends Component {
    constructor() {
        super()
        this.state = {
            roomCode: "",
            //gameCode: undefined,
            gameCode: "PRES",
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
        if(this.state.roomCode){
            window.open(this.getRoomLink(), "_blank");
        }
    }

    makeGame(event){
        if(this.state.gameCode && this.state.maxPlayers){
            var self = this;
            let payload = {
                max_players: parseInt(this.state.maxPlayers),   
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

    //old code
    //<input type="text" name="game_type" onChange={this.handleChangeGame}/>


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