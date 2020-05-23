import React from "react";

import jr from './red_joker.svg';
import jb from './black_joker.svg';
import c1 from './ace_of_clubs.svg';
import d1 from './ace_of_diamonds.svg';
import h1 from './ace_of_hearts.svg';
import s1 from './ace_of_spades.svg';
import c2 from './2_of_clubs.svg';
import d2 from './2_of_diamonds.svg';
import h2 from './2_of_hearts.svg';
import s2 from './2_of_spades.svg';
import c3 from './3_of_clubs.svg';
import d3 from './3_of_diamonds.svg';
import h3 from './3_of_hearts.svg';
import s3 from './3_of_spades.svg';
import c4 from './4_of_clubs.svg';
import d4 from './4_of_diamonds.svg';
import h4 from './4_of_hearts.svg';
import s4 from './4_of_spades.svg';
import c5 from './5_of_clubs.svg';
import d5 from './5_of_diamonds.svg';
import h5 from './5_of_hearts.svg';
import s5 from './5_of_spades.svg';
import c6 from './6_of_clubs.svg';
import d6 from './6_of_diamonds.svg';
import h6 from './6_of_hearts.svg';
import s6 from './6_of_spades.svg';
import c7 from './7_of_clubs.svg';
import d7 from './7_of_diamonds.svg';
import h7 from './7_of_hearts.svg';
import s7 from './7_of_spades.svg';
import c8 from './8_of_clubs.svg';
import d8 from './8_of_diamonds.svg';
import h8 from './8_of_hearts.svg';
import s8 from './8_of_spades.svg';
import c9 from './9_of_clubs.svg';
import d9 from './9_of_diamonds.svg';
import h9 from './9_of_hearts.svg';
import s9 from './9_of_spades.svg';
import c10 from './10_of_clubs.svg';
import d10 from './10_of_diamonds.svg';
import h10 from './10_of_hearts.svg';
import s10 from './10_of_spades.svg';
import c11 from './jack_of_clubs2.svg';
import d11 from './jack_of_diamonds2.svg';
import h11 from './jack_of_hearts2.svg';
import s11 from './jack_of_spades2.svg';
import c12 from './queen_of_clubs2.svg';
import d12 from './queen_of_diamonds2.svg';
import h12 from './queen_of_hearts2.svg';
import s12 from './queen_of_spades2.svg';
import c13 from './king_of_clubs2.svg';
import d13 from './king_of_diamonds2.svg';
import h13 from './king_of_hearts2.svg';
import s13 from './king_of_spades2.svg';

const selectShiftHeight = "30px";

const shiftRightLength = 30


function Card(props) {


    let left = 0;

    if (props.position){
        left = props.position * shiftRightLength;
    }

    let leftStr = left + "px";

    let normalStyle = {
        position: 'absolute',
        left: leftStr,
        top: selectShiftHeight
    };
    
    let selectedStyle = {
        position: 'absolute',
        left: leftStr,
        top: '0'
    };
    //get the correct image for the card
    let pic = decider(props.card);
    //select CSS for the selected state or unselected state
    let style = props.selected ? selectedStyle : normalStyle

    return(
    <div className="card" style={style} id={props.id} onClick={() => {props.onClick(0,props.selected,props.position)}}>
        <img src={pic} alt={props.card}/>
    </div>
    );
}

//unclickable card

export function FieldCard({card}){
    let pic = decider(card);
    return(
        <div className="card">
            <img alt={card} src={pic}/>
        </div>
    );
}

//function that returns the correct image
function decider(code){
    var pic;
    switch(code){
        case "c1":
            pic = c1;
            break;
        case "c2":
            pic = c2;
            break;
        case "c3":
            pic = c3;
            break;
        case "c4":
            pic = c4;
            break;
        case "c5":
            pic = c5;
            break;
        case "c6":
            pic = c6;
            break;
        case "c7":
            pic = c7;
            break;
        case "c8":
            pic = c8;
            break;
        case "c9":
            pic = c9;
            break;
        case "c10":
            pic = c10;
            break;
        case "c11":
            pic = c11;
            break;
        case "c12":
            pic = c12;
            break;
        case "c13":
            pic = c13;
            break;
        case "d1":
            pic = d1;
            break;
        case "d2":
            pic = d2;
            break;
        case "d3":
            pic = d3;
            break;
        case "d4":
            pic = d4;
            break;
        case "d5":
            pic = d5;
            break;
        case "d6":
            pic = d6;
            break;
        case "d7":
            pic = d7;
            break;
        case "d8":
            pic = d8;
            break;
        case "d9":
            pic = d9;
            break;
        case "d10":
            pic = d10;
            break;
        case "d11":
            pic = d11;
            break;
        case "d12":
            pic = d12;
            break;
        case "d13":
            pic = d13;
            break;
        case "h1":
            pic = h1;
            break;
        case "h2":
            pic = h2;
            break;
        case "h3":
            pic = h3;
            break;
        case "h4":
            pic = h4;
            break;
        case "h5":
            pic = h5;
            break;
        case "h6":
            pic = h6;
            break;
        case "h7":
            pic = h7;
            break;
        case "h8":
            pic = h8;
            break;
        case "h9":
            pic = h9;
            break;
        case "h10":
            pic = h10;
            break;
        case "h11":
            pic = h11;
            break;
        case "h12":
            pic = h12;
            break;
        case "h13":
            pic = h13;
            break;
        case "s1":
            pic = s1;
            break;
        case "s2":
            pic = s2;
            break;
        case "s3":
            pic = s3;
            break;
        case "s4":
            pic = s4;
            break;
        case "s5":
            pic = s5;
            break;
        case "s6":
            pic = s6;
            break;
        case "s7":
            pic = s7;
            break;
        case "s8":
            pic = s8;
            break;
        case "s9":
            pic = s9;
            break;
        case "s10":
            pic = s10;
            break;
        case "s11":
            pic = s11;
            break;
        case "s12":
            pic = s12;
            break;
        case "s13":
            pic = s13;
            break;
        case "jr":
            pic = jr;
            break;
        case "jb":
            pic = jb;
            break;
        default:
            pic = "";
    }
    return pic;
}

export default Card;