import React, {Component} from "react";
import Player from './Player';
import Hand from './Hand';
import axios from 'axios';
import Card from './cards/Card';


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
            otherPlayers: {}
        }
        this.wsURL = wsBase + type + "/" + code

        this.start = this.start.bind(this);
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
                case "game_move":
                    this.gameMove(data.player, data.move, data.special);
                    break;
                case "results":
                    this.scoreBoard(data.results);
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

        this.getName()
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

    handout(playerCards, otherCards){
        this.setState({
            cards: playerCards,
            otherPlayers: otherCards
        });
    }

    gameMove(playerID, card, special){

    }

    start(){
        let msg = {
            type: "start"
        }
        this.ws.send(JSON.stringify(msg));
    }

    render(){
        return(
            <div>
                <button onClick={this.connect}>Test websocket</button>
                <button onClick={this.start}>Start</button>
                {Object.keys(this.state.otherPlayers).forEach(
                    key => <Player number={key} cards={this.state.otherPlayers[key]}/>
                )}

                <div>
                    <field card={this.state.fieldCard}/>
                </div>

                <Hand cards={this.state.cards} ws={this.ws}/>
            </div>
        );
    }
}

function field(card){
    if(card){
        return(<Card card={card}/>);
    }else{
        return(null);
    }
}

/** The prompt content component */
class Prompt extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            value: this.props.defaultValue
        };

        this.onChange = (e) => this._onChange(e);
    }

    componentDidUpdate(prevProps, prevState) {
        if (prevState.value !== this.state.value) {
            this.props.onChange(this.state.value);
        }
    }

    _onChange(e) {
        let value = e.target.value;

        this.setState({value: value});
    }

    render() {
        return <input type="text" placeholder={this.props.placeholder} className="mm-popup__input" value={this.state.value} onChange={this.onChange} />;
    }
}



export default Game;