import React from "react";
import {
    BrowserRouter as Router,
    Switch,
    Route
} from "react-router-dom";
import Home from './Home';
import Game from './Game';





function App() {

    return (
        <Router>
            <div>

                <Switch>
                    <Route exact path="/">
                        <Home />
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
