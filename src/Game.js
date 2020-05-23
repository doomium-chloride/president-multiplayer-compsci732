import React, {Component} from "react";
import Rodal from 'rodal';

import Player from './Player';
import Hand from './Hand';
import axios from 'axios';
import Chat from './Chat';
import Results from './Results';

import {FieldCard} from './cards/Card';
import {back2front} from './utils/card-code-translator';
import {comparePresidentCard} from './utils/card-order';

import './styles/PlayerNameForm.css';
import './styles/Game.css';
import 'rodal/lib/rodal.css';

//websockets

let wsBase = "ws://localhost:8000/";

let serverBase = "http://localhost:8000/";

//for testing
var cardlist = [];
  for(let i = 13; i > 0; i--){
    cardlist.push("c"+i);
  }
  cardlist.push("h4");

class Game extends Component {
    constructor(props){
        super(props);
        let type = "president";
        let code = props.gameCode;
        this.state = {
            gameType: type,
            gameCode: code,
            cards: [],
            otherPlayers: [],
            chatLog: [],
            freeze: false,
            wsOpen: false,
            showResults: false,
            results: ""
        };
        this.wsURL = wsBase + type + "/" + code
    }

    componentDidMount(){

        //cache this object into that
        let that = this;

        //Get request to join room

        axios.get(serverBase + this.state.gameCode)
            .then(function (response) {
                let message = response.data;
                if(message.success){
                    if(message.success = "president")
                        that.connect();
                    else{
                        that.setState({
                            freeze: true
                        });
                        alert("message should be president: " + message.success);
                    }
                        
                }else{
                    that.setState({
                        freeze: true
                    });
                    alert(message.error);
                }
            })
    }

    connect(){
        // cache this object into that
        let that = this;

        //websocket part

        this.ws = new WebSocket(this.wsURL);    

        this.ws.onopen = () => {
            //test line
            that.setState({
                wsOpen: true
            })
            that.forceUpdate();
        }

        this.ws.onConnect = e => {

        }

        this.ws.onmessage = e => {
            // listen to data sent from the websocket server
            const data = JSON.parse(e.data)
            switch(data.type){
                case "room_message":
                that.setState(prevState => ({
                        chatLog: [...prevState.chatLog, data.message]
                    }));
                    break;
                case "game_command":
                    that.parseCommand(data.command);
                    break;
                case "handout":
                    that.handout(data.handout);
                    break;
                case "results":
                    that.scoreBoard(data.results);
                    break;
                case "move_response":
                    that.gameMove(data.move);
                    break;
                case "game_frame":
                    that.gameFrame(data.players, data.current_card);
                    break;
                case "name_response":
                    that.nameAccepted();
                    break;
                case "player_join":
                    console.log(data);
                    break;
                case "player_leave":
                    console.log(data);
                    break;
                case "freeze_game":
                    that.setState({freeze: true});
                    break;
                default:
                    console.log(data);
                    alert("Check console log");
            }

        }

        this.ws.onDisconnect = e => {
            alert("disconnect");
        }

        this.ws.onclose = e => {
            //test line
            alert("Websocket closed");
            that.setState({
                wsOpen: false
            });
        }

        this.ws.onerror = err => {
            //test line
            alert("Websocket error: " + err.message);
            console.error("WebSocket error observed:", err);
            that.ws.close();
        }
    }

    parseCommand(command){
        switch(command){
            case "close":
                this.ws.close();
                break;
        }
    }

    scoreBoard(results){
        const content = Results(results, this.ws);
        this.setState({
            showResults: true,
            results: content
        });
    }
    hideScoreBoard(){
        this.setState({
            showResults: false
        });
    }

    gameFrame(players, currentCard){
        const playerArray = parsePlayers(players, this.state.playerName);
        const current = currentCard ? back2front(currentCard) : "";
        this.setState({
            otherPlayers: playerArray,
            currentCard: current
        });
    }

    handout(playerCards){
        let translatedCards = playerCards.map((x) => back2front(x));
        translatedCards.sort(comparePresidentCard);
        this.setState({
            cards: translatedCards
        });
        if(this.state.showResults){
            this.hideScoreBoard();
        }
    }

    //move_response
    gameMove(card){
        if("skip" == card){
            return //dunno what to do yet
        }
        const cardCode = back2front(card);
        let newCards = [...this.state.cards];
        //search for index
        let index = undefined;
        for(let i = 0; i < newCards.length; i++){
            if(cardCode == newCards[i]){
                index = i;
                break;
            }
        }
        if(index != undefined){
            newCards.splice(index,1);
            this.setState({
                cards: newCards
            });
        }
    }

    ready(){
        let msg = {
            type: "ready"
        }
        this.setState({ready: true});
        this.ws.send(JSON.stringify(msg));
    }

    //called then child (the chat) sends a message so own message is recorded
    //that is to cache this object to keep context
    newMessage(that ,message, oldLog){
        that.setState({
            chatLog: [...oldLog, message]
        });
    }

    onNameChangeHandler(event){
        this.setState({playerNameTemp: event.target.value});
    }

    getPlayerName(){
        if(!this.state.wsOpen){
            return
        }
        const name = this.state.playerNameTemp;
        this.nameCache = name;
        const msg = {
            type: "name",
            name: name
        }
        this.ws.send(JSON.stringify(msg));
    }

    nameAccepted(){
        this.setState({playerName: this.nameCache});
    }



    render(){

        return(
            <div className="gameField">

                {this.state.playerName && !this.state.ready && <button className="oldButton" onClick={this.ready.bind(this)}>Ready</button>}

                
                <div className="playerAndField">
                    <div className="playerDiv">
                        {this.state.playerName && this.state.otherPlayers.map(
                            (obj,i) => <Player key={"player" + i} currentTurn={obj.current_turn} name={obj.name} cards={obj.num_cards}/>
                        )}
                    </div>
                    <div className="fieldDiv">
                        {this.state.currentCard && <Field card={this.state.currentCard}/>}
                    </div>
                </div>

                <Chat freeze={this.state.freeze} log={this.state.chatLog} ws={this.ws} update={(msg, old) => this.newMessage(this, msg, old)}/>

                {!this.state.playerName && <GetPlayerName onNameChange={this.onNameChangeHandler.bind(this)} submitName={this.getPlayerName.bind(this)}/>}

                <Hand cards={this.state.cards} freeze={this.state.freeze} ws={this.ws}/>

                <Rodal visible={this.state.showResults} onClose={this.hideScoreBoard.bind(this)}>
                    {this.state.results}
                </Rodal>

            </div>
        );
    }
}

function Field({card}){
    if(card){
        return(
            <div className="singleCard">
                    <FieldCard card={card}/>
            </div>
        );
    }else{
        return(null);
    }
}

function GetPlayerName(props){
    return(
        <div className="singleForm">
            Player Name: 
            <input type="text" maxlength={13} name="player-name" onChange={props.onNameChange}/>
            <button className="oldButton" onClick={props.submitName}>Enter</button>
        </div>
    );
}
/*
{player1: {
    name: name,  
    ready: bool, 
    current_turn: bool, 
    skip_turn: bool, 
    role: role, 
    num_cards: int} *howmanymoreplayersthereare}
*/
function parsePlayers(players, myName){
    let outArray = [];
    for(let key in players){
        const data = players[key];
        if(data.name != myName){
            outArray.push(data);
        }
            
    }
    return outArray;
}



export default Game;