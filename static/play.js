async function renderInfo(answers) {
    console.log(answers)
    for (let x = 1; x < 5; x++) {
        let i = document.getElementById("question_"+x.toString())
        i.innerText = answers[x-1]
        i.addEventListener("click", () => {i.classList.add("selected")})
    }
}

