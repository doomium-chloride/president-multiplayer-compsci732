export function front2back(card){
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

export function back2front(card){
    let card = card.toLowerCase();
    const house = card.charAt(0);
    const number = card.slice(1);
    let rank = number;
    if(house == "x"){
        const chance = Math.random() < 0.5;
        return chance ? "jb" : "jr";
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
}