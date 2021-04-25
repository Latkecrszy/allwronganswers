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
                console.log("doing")
                username.innerText = player['info']['username']
                x.innerText = "×"
                x.style.opacity = "0"
                newPlayer.addEventListener("mouseover", () => {x.style.opacity = "1"})
                newPlayer.addEventListener("mouseout", () => {x.style.opacity = "0"})
                x.addEventListener("click", async () => {await fetch(`https://allwronganswers.com/remove_player?username=${player['info']['username']}&id=${id}&player_id=${player['info']['id']}`)})
                newPlayer.appendChild(username)
                newPlayer.appendChild(x)
                newPlayer.classList.add("container")
                insert.appendChild(newPlayer)
            }
            players = newPlayers
        }
    }, 100)
}

function start(id) {
    location.replace(`/play?id=${id}&host=true`)
}

async function leave(id, player_id) {
    await fetch(`https://allwronganswers.com/remove_player?id=${id}&player_id=${player_id}`)
    location.replace("/join")
}


async function awaitStart(id) {
    setInterval(async () => {
        let started = await fetch(`http://localhost:5001/started?id=${id}`)
        console.log(started)
        started = await started.json()
        if (started['started'] === 'true') {
            location.replace(`/play?id=${id}&host=false`)
        }
    }, 500)
}