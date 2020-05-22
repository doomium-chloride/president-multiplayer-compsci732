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
                    console.log("everything seems fine");
                    //expect president
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
                case "move_response":
                    this.gameMove(data.move);
                    break;
                case "game_frame":
                    this.gameFrame(data.players, data.current_card);
                    break;
                case "name_response":
                    this.nameAccepted();
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
        const playerArray = parsePlayers(players, this.state.playerName);
        const current = currentCard ? back2front(currentCard) : "";
        this.setState({
            otherPlayers: playerArray,
            currentCard: current
        });
    }

    handout(playerCards){
        const translatedCards = playerCards.map((x) => back2front(x));
        this.setState({
            cards: translatedCards
        });
    }

    gameMove(card){
        if("skip" == card){
            return //dunno what to do yet
        }
        alert(card);
        const cardCode = back2front(card);
        let newCards = [...this.state.cards];
        //search for index
        let index;
        for(let i = 0; i < newCards.length; i++){
            if(cardCode == newCards[0]){
                index = i;
                break;
            }
        }
        if(index){
            newCards.splice(index,1);
            alert(newCards);
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

    //test

    testChat(){
        this.newMessage(this, "bob", this.state.chatLog);

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

    setCurrentCard(){
        alert(this.state.currentCard);
        this.setState({currentCard: "jr"});
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
        //<Player name={obj.name} cards={obj.num_cards}/>
        return(
            <div className="gameField">

                <button onClick={this.setCurrentCard.bind(this)}>Joker</button>

                {this.state.playerName && !this.state.ready && <button onClick={this.ready.bind(this)}>Ready</button>}

                
                {this.state.playerName && this.state.otherPlayers.map(
                    (obj,i) => <Player key={"player" + i} name={obj.name} cards={obj.num_cards}/>
                )}
                

                {this.state.currentCard && <Field card={this.state.currentCard}/>}

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