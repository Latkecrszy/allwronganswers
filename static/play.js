async function leave(id, player_id) {
    await fetch(`https://allwronganswers.com/remove_player?id=${id}&player_id=${player_id}`)
    location.replace("/join")
}