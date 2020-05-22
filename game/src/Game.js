import React, {Component} from "react";
import Player from './Player';
import Hand from './Hand';
import axios from 'axios';
import {FieldCard} from './cards/Card';
import Chat from './Chat';
import './styles/PlayerNameForm.css';
import './styles/Game.css';
import {back2front} from './utils/card-code-translator';

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
            chatLog: []
        }
        this.wsURL = wsBase + type + "/" + code

        this.connect = this.connect.bind(this);

        //test
        this.testChat = this.testChat.bind(this);
    }

    componentDidMount(){

        //Get request to join room

        axios.get(serverBase + this.state.gameCode)
            .then(function (response) {
                let message = response.data;
                console.log(message);
                if(message.success){
                    alert(message.success);
                }else{
                    alert(message.error);
                }
            })

        //websocket part

        this.ws = new WebSocket(this.wsURL);    
        //cache this object into that
        let that = this;

        this.ws.onopen = () => {
            //test line
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
                    this.parseCommand(data.command);
                    break;
                case "handout":
                    this.handout(data.handout);
                    break;
                case "results":
                    this.scoreBoard(data.results);
                    break;
                case "game_frame":
                    this.gameFrame(data.players, data.current_card);
                    break;
                case "player_join":
                    console.log(data);
                    break;
                case "player_leave":
                    console.log(data);
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
        }

        this.ws.onerror = err => {
            //test line
            alert("Websocket error: " + err.message);
            console.error("WebSocket error observed:", err);
            this.ws.close();
        }

        //this.getName()
    }

    connect(){

        alert(this.wsURL);
        
        this.ws = new WebSocket(this.wsURL);   

        
    }

    getName(){
        const name = prompt("Please enter a name");
        this.setState({playerName: name});
        const msg = {
            type: "name",
            name: name
        }
        this.ws.send(JSON.stringify(msg));
    }

    parseCommand(command){
        switch(command){
            case "close":
                this.ws.close();
                break;
        }
    }

    scoreBoard(results){
        
    }

    gameFrame(players, currentCard){
        const playerArray = parsePlayers(players);
        this.setState({
            otherPlayers: playerArray,
            currentCard: currentCard
        });
    }

    handout(playerCards){
        const translatedCards = playerCards.map((x) => back2front(x));
        this.setState({
            cards: translatedCards
        });
    }

    gameMove(card){
        
    }

    ready(){
        let msg = {
            type: "ready"
        }
        this.setState({ready: true});
        this.ws.send(JSON.stringify(msg));
    }

    //test

    testChat(){
        this.newMessage(this, "bob", this.state.chatLog);

    }
    //called then child (the chat) sends a message so own message is recorded
    //that is to cache this object to keep context
    newMessage(that ,message, oldLog){
        alert(oldLog);
        that.setState({
            chatLog: [...oldLog, message]
        });
        that.forceUpdate();
    }

    onNameChangeHandler(event){
        this.setState({playerNameTemp: event.target.value});
    }

    getPlayerName(){
        const name = this.state.playerNameTemp;
        alert(name);
        this.setState({playerName: name});
        const msg = {
            type: "name",
            name: name
        }
        this.ws.send(JSON.stringify(msg));
    }


    render(){

        //<button onClick={this.connect}>Test websocket</button>
        //
        //<button onClick={this.testChat}>test chat</button>

        //<Hand cards={this.state.cards} ws={this.ws}/>
        //let testCards = ["c1","c2","jb","jr","h12"];

        /*
        <Player number={1} cards={20}/>
        <Player number={2} cards={10}/>
        <Player number={3} cards={30}/>
        */

        return(
            <div className="gameField">

                <button onClick={this.ready.bind(this)}>Start</button>

                
                {this.state.otherPlayers.forEach(
                    obj => <Player name={obj.name} cards={obj.num_cards}/>
                )}
                

                <Field card={this.state.currentCard}/>

                <Chat log={this.state.chatLog} ws={this.ws} update={(msg, old) => this.newMessage(this, msg, old)}/>

                {!this.state.playerName && <GetPlayerName onNameChange={this.onNameChangeHandler.bind(this)} submitName={this.getPlayerName.bind(this)}/>}

                
                

                <Hand cards={this.state.cards} ws={this.ws}/>
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
            <input type="text" name="player-name" onChange={props.onNameChange}/>
            <button onClick={props.submitName}>Enter</button>
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
function parsePlayers(players){
    let outArray = [];
    for(let i =1; i <= 4; i++){
        const playerKey = "player" + i;
        const exists = playerKey in players;
        if(!exists){
            break;
        }
        const data = players.playerKey;
        outArray.push(data);
    }
    return outArray;
}



export default Game;