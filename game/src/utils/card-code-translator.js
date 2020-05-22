/**
 * This translate frontend card notation to backend's notation
 *
 * @param {string}   card           frontend card code
 *
 * @return {string} code for card that is compatible with backend
 */
export function front2back(card){
    if(!card){
        return "skip";
    }
    if(card == "skip"){
        return "skip";
    }
    if(card == ""){
        console.log("empty string in card translater. Is this ok?");
        return "skip";
    }
    if(card == "jb" || card == "jr"){
        return "XX";
    }
    const house = card.charAt(0).toUpperCase();
    const number = card.slice(1);
    let rank = number + "";
    switch(number){
        case "10":
            rank = "0";
            break;
        case "11":
            rank = "J";
            break;
        case "12":
            rank = "Q";
            break;
        case "13":
            rank = "K";
            break;
        case "1":
            rank = "A";
    }
    return house + rank;
}

/**
 * This translate backend card notation to  frontend's notation
 *
 * @param {string}   card           backend card code
 *
 * @return {string} code for card that is compatible with frontend
 */
export function back2front(card){
    if(card == "skip"){
        return "skip";
    }
    card = card.toLowerCase();
    const house = card.charAt(0);
    const number = card.slice(1);
    let rank = number;
    if(house == "x"){
        return "jb";
    }
    switch(number){
        case "a":
            rank = "1";
            break;
        case "0":
            rank = "10";
            break;
        case "j":
            rank = "11";
            break;
        case "q":
            rank = "12";
            break;
        case "k":
            rank = "13";
            break;
    }
    return house + rank;
}