async function renderInfo(answers) {
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
}

