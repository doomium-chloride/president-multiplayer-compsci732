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
import './styles/Popup.css';
import 'rodal/lib/rodal.css';

//websockets

let wsBase = "ws://localhost:8000/";

let serverBase = "http://localhost:8000/";

//for testing
var cardlist = [];
  for(let i = 13; i > 0; i--){
    cardlist.push("h"+i);
  }
  for(let i = 13; i > 0; i--){
    cardlist.push("s"+i);
  }

class Game extends Component {
    constructor(props){
        super(props);
        let type = "president";
        let code = props.gameCode;
        this.state = {
            gameType: type,
            gameCode: code,
            cards: cardlist,
            otherPlayers: [{
                name: "bob the builder",
                current_turn: true,
                num_cards: 50
            },
            {
                name: "spongebob",
                current_turn: false,
                num_cards: 5
                }],
            chatLog: [],
            freeze: false,
            wsOpen: false,
            showResults: false,
            results: "",
            currentCard: "jr",
            chatLog: ["blah blah", "Please make this page pretty"],
            playerName: "squarepants",//making this false will display the get name form
            ready: true//making this false will display the ready button
        };
        this.wsURL = wsBase + type + "/" + code

        //test
        this.testChat = this.testChat.bind(this);
    }

    componentDidMount(){

        

        
    }



    scoreBoard(results){
        const content = Results(results);
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
        if(!this.state.wsOpen){
            return
        }
        const name = this.state.playerNameTemp;
        this.nameCache = name;
        const msg = {
            type: "name",
            name: name
        }
    }

    nameAccepted(){
        this.setState({playerName: this.nameCache});
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

                {this.state.playerName && !this.state.ready && <button onClick={this.ready.bind(this)}>Ready</button>}

                
                {this.state.playerName && this.state.otherPlayers.map(
                    (obj,i) => <Player key={"player" + i} currentTurn={obj.current_turn} name={obj.name} cards={obj.num_cards}/>
                )}
                

                {this.state.currentCard && <Field card={this.state.currentCard}/>}

                <Chat log={this.state.chatLog} update={(msg, old) => this.newMessage(this, msg, old)}/>

                {!this.state.playerName && <GetPlayerName onNameChange={this.onNameChangeHandler.bind(this)} submitName={this.getPlayerName.bind(this)}/>}

                <Hand cards={this.state.cards} freeze={this.state.freeze} />

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