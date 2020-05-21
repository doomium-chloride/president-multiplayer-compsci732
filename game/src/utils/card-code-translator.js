export function front2back(card){
    if(card == "skip"){
        return "skip";
    }
    if(card == ""){
        console.log("empty string in card translater. Is this ok?");
        return "skip";
    }
    if(card == "jb" || card == "jr"){
        return "X0";
    }
    const house = card.charAt(0).toUpperCase();
    const number = card.slice(1);
    let rank = number + "";
    switch(number){
        case 10:
            rank = "0";
            break;
        case 11:
            rank = "J";
            break;
        case 12:
            rank = "Q";
            break;
        case 13:
            rank = "K";
            break;
        case 1:
            rank = "A";
    }
    return house + rank;
}