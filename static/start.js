async function showPlayers(id) {
    let players;
    let newPlayers;
    let insert = document.getElementById("players")
    console.log(insert)
    setInterval(async () => {
        let start_json = await fetch(`https://allwronganswers.com/players?id=${id}`)
        newPlayers = await start_json.json()
        if (JSON.stringify(newPlayers) !== JSON.stringify(players)) {
            insert.innerHTML = null
            for (let player of newPlayers) {
                let newPlayer = document.createElement('div')
                let username = document.createElement('p')
                let x = document.createElement('div')
                username.innerText = player['info']['username']
                x.innerText = "×"
                x.style.opacity = "0"
                newPlayer.addEventListener("mouseout", () => {x.style.opacity = "0"})
                newPlayer.appendChild(username)
                newPlayer.appendChild(x)
                newPlayer.classList.add("container")
                if (player['host'] === 'true') {newPlayer.style.backgroundColor = "#0026ff"}
                else {
                        newPlayer.addEventListener("mouseover", () => {x.style.opacity = "1"})
                        x.addEventListener("click", async () => {await fetch(`https://allwronganswers.com/remove_player?username=${player['info']['username']}&id=${id}&player_id=${player['info']['id']}`)})
                }
                insert.appendChild(newPlayer)
            }
            players = newPlayers
        }
    }, 100)
}

function start(id) {location.replace(`/play?id=${id}`)}


async function leave(id, player_id) {
    await fetch(`https://allwronganswers.com/remove_player?id=${id}&player_id=${player_id}`)
    location.replace("/join")
}


async function awaitStart(id) {
    setInterval(async () => {
        let started = await fetch(`https://allwronganswers.com/started?id=${id}`)
        started = await started.json()
        if (started['started'] === 'true') {
            location.replace(`/play?id=${id}`)
        }
    }, 500)
}