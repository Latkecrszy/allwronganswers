async function renderInfo(answers, host) {
    console.log(answers)
    for (let x = 1; x < 5; x++) {
        let i = document.getElementById("answer_"+x.toString())
        console.log("question_"+x.toString())
        console.log(i)
        i.children[0].innerText = answers[x-1]
        i.addEventListener("click", () => {
            i.classList.add("selected")
        })
    }
    let timer = document.getElementById("timer")
    let seconds = 10
    let time = setInterval(async () => {
        seconds--
        timer.innerText = seconds.toString()
        if (seconds === 0) {clearInterval(time)}
    }, 1000)
    leaderboard()
}

