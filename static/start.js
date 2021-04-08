function showPlayers(id) {
    let players;
    let newPlayers;
    let insert = document.getElementById("players")
    setInterval(() => {
        //let start_json = await fetch(`https://allwronganswers.com/players?id=${id}`)
        //newPlayers = await start_json.json()
        newPlayers = [{'login_info': {'username': 'test'}}]
        if (newPlayers !== players) {
            players = newPlayers
            newPlayers.innerHTML = null
            for (player in players) {
                let newPlayer = document.createElement('div')
                let username = document.createElement('p')
                let x = document.createElement('div')
                username.innerText = player['login_info']['username']
                x.innerText = "×"
                newPlayer.appendChild(username)
                newPlayer.appendChild(x)
                insert.appendChild(newPlayer)
            }
        }
    }, 100)
}