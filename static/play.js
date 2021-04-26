async function renderInfo(answers) {
    console.log(answers)
    for (let x = 1; x < 5; x++) {document.getElementById("question_"+x.toString()).innerText = answers[x-1]}
}