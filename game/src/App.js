import React from "react";
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link,
  useParams
} from "react-router-dom";
import Hand from './Hand';
import Home from './Home';
import Game from './Game';
import Chat from './Chat';

var cardlist = [];
  for(let i = 13; i > 0; i--){
    cardlist.push("c"+i);
  }
  cardlist.push("h4");


{/* <ul>
          <li>
            <Link to="/">Home</Link>
          </li>
          <li>
            <Link to="/game">Game</Link>
          </li>
          <li>
            <Link to="/chat">Chat</Link>
          </li>
        </ul>

        <hr /> */}

function App() {
  
  return (
    <Router>
      <div>
        

        {/*
          A <Switch> looks through all its children <Route>
          elements and renders the first one whose path
          matches the current URL. Use a <Switch> any time
          you have multiple routes, but you want only one
          of them to render at a time
        */}
        <Switch>
          <Route exact path="/">
            <Home />
          </Route>
          <Route path="/chat">
            <Chat log={[]}/>
          </Route>
          <Route path="/game">
          <div>
            <Game/>
          </div>
          </Route>
          <Route path="/:room" component={room}>
          </Route>
          
        </Switch>
      </div>
    </Router>
    
  );
}

const room = ({ match }) => (

  <Game gameType="PRES" gameCode={match.params.room}/>

)

export default App;
