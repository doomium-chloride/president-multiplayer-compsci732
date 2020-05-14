import React, {Component} from "react";
import Player from './Player';
import Hand from './Hand';
import axios from 'axios';

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
            cards: []
        }
        this.wsURL = wsBase + type + "/" + code

        this.connect = this.connect.bind(this);
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
                    alert(data.message);
                    break;
                case "game_command":
                    this.parseCommand(data.command);
                    break;
                case "handout":
                    this.handout(data.handout, data.player_cardnums);
                    break;
                case "results":
                    this.scoreBoard(data.results);
                    break;
                case "player_join":
                    break;
                case "player_leave":
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
    }

    connect(){

        alert(this.wsURL);
        
        this.ws = new WebSocket(this.wsURL);   

        
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

    handout(playerCards, otherCards){
        this.setState({
            cards: playerCards
        });
    }

    render(){
        return(
            <div>
                <button onClick={this.connect}>Test websocket</button>
                <Player number={0} cards={10}/>
                <Player number={1} cards={20}/>
                <Player number={2} cards={30}/>
                <Hand cards={this.state.cards}/>
            </div>
        );
    }
}

export default Game;