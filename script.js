let display = document.getElementById("display");

function addToDisplay(value) {
    display.value += value;
}

function clearDisplay() {
    display.value = "";
}

function deleteLast() {
    display.value = display.value.slice(0, -1);
}

function calculate() {
    try {
        let answer = eval(display.value);
        display.value = answer;
    } catch (error) {
        display.value = "Error";
    }
}

function calculatePercentage() {
    try {
        let answer = eval(display.value);
        display.value = answer / 100;
    } catch (error) {
        display.value = "Error";
    }
}

function squareRoot() {
    try {
        let number = eval(display.value);
        display.value = Math.sqrt(number);
    } catch (error) {
        display.value = "Error";
    }
}

function squareNumber() {
    try {
        let number = eval(display.value);
        display.value = number * number;
    } catch (error) {
        display.value = "Error";
    }
}

