
/*
 * this is to order from strongest to weakest
 * this means if card1 is stronger than card 2
 * card2 - card1 < 0
 */
export function comparePresidentCard(card1, card2){
    //this will be the value of the card
    let card1value;
    let card2value;

    //convert card1
    if(card1.charAt(0) == "j"){
        card1value = 9001;//over 9000!!!
    } else{
        //get str of the number
        const cardStr = card1.substring(1);
        card1value = presidentStr2Int(cardStr);
    }

    //convert card2
    if(card2.charAt(0) == "j"){
        card2value = 9001;//over 9000!!!
    } else{
        //get str of the number
        const cardStr = card2.substring(1);
        card2value = presidentStr2Int(cardStr);
    }
    
    return card2value - card1value;
}

function presidentStr2Int(cardStr){
    const cardValue = parseInt(cardStr);
    return presidentConverter(cardValue);
}

/*
 * in president 2 > Ace > King
 * this means that if king=13, then ace>13 and 2>ace
 * so we'll change 1 into 14
 * and 2 into 15
 */
function presidentConverter(value){
    switch(value){
        case 1://ace
            return 14;
        case 2://2
            return 15;
        default:
            return value;
    }
}