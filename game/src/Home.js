import React, { Component } from "react";
import { render } from 'react-dom'
import { Redirect } from 'react-router-dom'

class Home extends Component {
    constructor() {
        super()
        this.state = {roomCode: undefined};

        this.handleChange = this.handleChange.bind(this);
        this.joinGame = this.joinGame.bind(this);
        this.makeGame = this.makeGame.bind(this);
    }

    handleChange(event){
        this.setState({value: event.target.value});
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

    }


    render(){
        return(
            <div>
                <form>
                    <label>
                        Room Code:
                        <input type="text" name="room-code" onChange={this.handleChange}/>
                    </label>
                    <button onClick={this.handleSubmit}>Join Game</button>
                </form>
                <form  action="/" method="post">
                    <label>
                        Game code:
                        <input type="number" name="game"/>
                        Max number of players:
                        <input type="number" name="max_players"/>
                    </label>
                    <button onClick={this.makeGame}>Start Game</button>
                </form>
            </div>
        );
    }
    
}

export default Home;