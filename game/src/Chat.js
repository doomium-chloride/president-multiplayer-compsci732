import React, {Component} from "react";

class Chat extends Component {
    //Props will be
    //log, which is what the chat displays
    //log will be a list of text
    constructor(props){
        super(props);
        this.ws = props.ws;
        this.state = {
            log: props.log,
            sendText: ""
        }
        this.sendMessage = this.sendMessage.bind(this);
        this.handleChangeText = this.handleChangeText.bind(this);
    }

    handleChangeText(event){
        this.setState({
            sendText: event.target.value
        });
    }

    sendMessage(){
        const text = this.state.sendText;
        const oldLog = this.state.log;
        let msg = {
            type: "game_message",
            message: text
        }
        
        if(this.ws){
        this.ws.send(JSON.stringify(msg));
        } else{
            alert(JSON.stringify(msg));
        }
        this.setState({
            log: [...oldLog, text],
            sendText: ""
        });
    }

    render(){
        return(
            <div className="chatBox">
                <div className="chat">
                    {this.state.log.map((tex, i) => <ChatLine order={i} text={tex}/>)}
                </div>
                <div className="chatInput">
                    <input type="text" value={this.state.sendText} name="chatText" onChange={this.handleChangeText}/>
                    <button onClick={this.sendMessage}>Send</button>
                </div>
            </div>

        );
    }
}

function ChatLine(props){
    const odd = props.order & 1;
    const lineClass = odd ? "chatLineOdd" : "chatLineEven";
    return(
        <div className={lineClass}>
            {props.text}
        </div>
    );
}

export default Chat;