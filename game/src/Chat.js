import React, {Component} from "react";
import './styles/Chat.css';

class Chat extends Component {

    constructor(props){
        super(props);
        this.state = {
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
        if(this.props.freeze){
            //don't do anything if frozen
            return
        }
        const text = this.state.sendText;
        const oldLog = this.props.log;
        let msg = {
            type: "chat",
            message: text
        }
        
        if(this.props.ws){
            this.props.ws.send(JSON.stringify(msg));
        } else{
            alert(JSON.stringify(msg));
            this.props.update(text, oldLog);
        }
        this.setState({
            sendText: ""
        });
        
    }

    scrollToBottom = () => {
        this.messagesEnd.scrollIntoView({ behavior: "smooth" });
    }
      
    componentDidMount() {
        this.scrollToBottom();
    }
      
    componentDidUpdate() {
        this.scrollToBottom();
    }

    render(){
        return(
            <div className="chatBox">
                <div className="chat">
                    {this.props.log.map((tex, i) => <ChatLine order={i} key={i} text={tex}/>)}
                    <div style={{ float:"left", clear: "both" }}
                        ref={(el) => { this.messagesEnd = el; }}>
                    </div>
                </div>
                <div className="chatInput">
                    <textarea key="chatinputtext" value={this.state.sendText} name="chatText" onChange={this.handleChangeText}/>
                    <button key="sentchatbutton" onClick={this.sendMessage}>Send</button>
                </div>
            </div>

        );
    }
}

function ChatLine(props){
    const odd = props.order & 1;
    const key = props.id ? "cl" + props.key : "cl" + Math.random();
    const lineClass = odd ? "chatLineOdd" : "chatLineEven";
    return(
        <div className={lineClass} key={key}  >
            {props.text}
        </div>
    );
}

export default Chat;