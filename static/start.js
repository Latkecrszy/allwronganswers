async function showPlayers(id) {
    let players;
    let newPlayers;
    let insert = document.getElementById("players")
    setInterval(async () => {
        let start_json = await fetch(`https://allwronganswers.com/players?id=${id}`)
        newPlayers = await start_json.json()
        //newPlayers = [{'info': {'username': 'test'}}, {'info': {'username': 'test123'}}]
        if (JSON.stringify(newPlayers) != JSON.stringify(players)) {
            insert.innerHTML = null
            for (player of newPlayers) {
                let newPlayer = document.createElement('div')
                let username = document.createElement('p')
                let x = document.createElement('div')
                console.log("doing")
                username.innerText = player['info']['username']
                x.innerText = "×"
                x.style.opacity = "0"
                newPlayer.addEventListener("hover", () => {x.style.opacity = "1"})
                //x.addEventListener("click", () => {})
                newPlayer.appendChild(username)
                newPlayer.appendChild(x)
                newPlayer.classList.add("container")
                insert.appendChild(newPlayer)
            }
            players = newPlayers
        }
    }, 100)
}