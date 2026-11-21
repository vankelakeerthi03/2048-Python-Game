
const SIZE = 4;

const COLORS = {
    0: ["#cdc1b4", "#776e65"],
    2: ["#eee4da", "#776e65"],
    4: ["#ede0c8", "#776e65"],
    8: ["#f2b179", "white"],
    16: ["#f59563", "white"],
    32: ["#f67c5f", "white"],
    64: ["#f65e3b", "white"],
    128: ["#edcf72", "white"],
    256: ["#edcc61", "white"],
    512: ["#edc850", "white"],
    1024: ["#edc53f", "white"],
    2048: ["#edc22e", "white"]
};

let board = [];
let score = 0;
let best = Number(localStorage.getItem("best2048")) || 0;
let won = false;
let gameOver = false;

const boardElement = document.getElementById("board");
const scoreElement = document.getElementById("score");
const bestElement = document.getElementById("best");
const messageElement = document.getElementById("message");
const restartButton = document.getElementById("restart");

function restart() {
    board = Array.from(
        { length: SIZE },
        () => Array(SIZE).fill(0)
    );

    score = 0;
    won = false;
    gameOver = false;

    messageElement.textContent = "Use arrow keys or swipe to play";

    addTile();
    addTile();

    updateDisplay();
}

function addTile() {
    const empty = [];

    for (let r = 0; r < SIZE; r++) {
        for (let c = 0; c < SIZE; c++) {
            if (board[r][c] === 0) {
                empty.push([r, c]);
            }
        }
    }

    if (empty.length === 0) return;

    const [r, c] = empty[
        Math.floor(Math.random() * empty.length)
    ];

    board[r][c] = Math.random() < 0.9 ? 2 : 4;
}

function slide(row) {
    const numbers = row.filter(n => n !== 0);
    const result = [];

    let i = 0;

    while (i < numbers.length) {
        if (
            i + 1 < numbers.length &&
            numbers[i] === numbers[i + 1]
        ) {
            const value = numbers[i] * 2;

            result.push(value);
            score += value;
            i += 2;
        } else {
            result.push(numbers[i]);
            i++;
        }
    }

    while (result.length < SIZE) {
        result.push(0);
    }

    return result;
}

function move(direction) {
    if (gameOver || won) return;

    const oldBoard = board.map(row => [...row]);

    if (direction === "left") {
        board = board.map(row => slide(row));
    }

    if (direction === "right") {
        board = board.map(row =>
            slide([...row].reverse()).reverse()
        );
    }

    if (direction === "up" || direction === "down") {
        let transposed = board[0].map((_, c) =>
            board.map(row => row[c])
        );

        transposed = transposed.map(row =>
            direction === "up"
                ? slide(row)
                : slide([...row].reverse()).reverse()
        );

        board = board[0].map((_, c) =>
            transposed.map(row => row[c])
        );
    }

    const changed = board.some((row, r) =>
        row.some((value, c) => value !== oldBoard[r][c])
    );

    if (changed) {
        addTile();
    }

    updateDisplay();
    checkGameStatus();
}

function updateDisplay() {
    boardElement.innerHTML = "";

    for (let r = 0; r < SIZE; r++) {
        for (let c = 0; c < SIZE; c++) {
            const value = board[r][c];

            const cell = document.createElement("div");
            cell.className = "cell";
            cell.textContent = value || "";

            const [bg, fg] = COLORS[value] || ["#3c3a32", "white"];

            cell.style.backgroundColor = bg;
            cell.style.color = fg;

            boardElement.appendChild(cell);
        }
    }

    scoreElement.textContent = score;

    if (score > best) {
        best = score;
        localStorage.setItem("best2048", best);
    }

    bestElement.textContent = best;
}

function checkGameStatus() {
    if (board.some(row => row.includes(2048))) {
        won = true;
        messageElement.textContent = "YOU WIN! You reached 2048!";
        return;
    }

    if (board.some(row => row.includes(0))) return;

    for (let r = 0; r < SIZE; r++) {
        for (let c = 0; c < SIZE; c++) {
            if (
                c + 1 < SIZE &&
                board[r][c] === board[r][c + 1]
            ) return;

            if (
                r + 1 < SIZE &&
                board[r][c] === board[r + 1][c]
            ) return;
        }
    }

    gameOver = true;
    messageElement.textContent = "GAME OVER! Click NEW GAME";
}

// Keyboard controls
document.addEventListener("keydown", event => {
    const directions = {
        ArrowLeft: "left",
        ArrowRight: "right",
        ArrowUp: "up",
        ArrowDown: "down"
    };

    if (directions[event.key]) {
        event.preventDefault();
        move(directions[event.key]);
    }
});

// Mobile swipe controls
let touchStartX = 0;
let touchStartY = 0;

boardElement.addEventListener("touchstart", event => {
    const touch = event.changedTouches[0];

    touchStartX = touch.clientX;
    touchStartY = touch.clientY;
}, { passive: true });

boardElement.addEventListener("touchend", event => {
    const touch = event.changedTouches[0];

    const diffX = touch.clientX - touchStartX;
    const diffY = touch.clientY - touchStartY;

    if (Math.max(Math.abs(diffX), Math.abs(diffY)) < 30) {
        return;
    }

    if (Math.abs(diffX) > Math.abs(diffY)) {
        move(diffX > 0 ? "right" : "left");
    } else {
        move(diffY > 0 ? "down" : "up");
    }
}, { passive: true });

restartButton.addEventListener("click", restart);

// Start game
restart();
