document.addEventListener('DOMContentLoaded', () => {
  const myModalElement = document.querySelector('#myModal');
  // const myModalInstance = new bootstrap.Modal(myModalElement);
  const playlistForm = document.querySelector('#playlist-form');
  // const addTrack = document.querySelector('#add-track');
  const search = document.querySelector('#search');
  const createPlaylistForm = document.getElementById('create-playlist-modal');

  let currentTrackId = null;

  myModalElement.addEventListener('shown.bs.modal', (e) => {
    const button = e.relatedTarget;
    currentTrackId = button.getAttribute('data-track-id');
    playlistForm.setAttribute('action', `/audio_analysis/${currentTrackId}`);
    createPlaylistForm.setAttribute('action', `/user/playlists`);
    console.log(currentTrackId)
  });

  playlistForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const playlist_id = document.getElementById("playlist").value;

    if (!currentTrackId) {
      console.error("No track ID found");
      return;
    }

    axios.post(`/audio_analysis/${currentTrackId}`, {
      track_id: currentTrackId,
      playlist_id: playlist_id
    })
    .then((response) => {
      // console.log(response.data);
      // myModalInstance.hide(); // Close the modal
    })
    .catch((error) => {
      console.error(error);
    });
  });

  search.addEventListener('submit', (e) => {
    e.preventDefault();
  });

  createPlaylistForm.addEventListener('submit', async (e) => {
    console.log("Creating playlist")
    e.preventDefault();
    const button = e.relatedTarget;
    
    const trackId = button.getAttribute('data-track-id');
    const playlistName = document.getElementById("name").value;
    const playlistDescription = document.getElementById("description").value;

    const dataToSend = JSON.stringify({
      playlist_name: playlistName,
      playlist_description: playlistDescription,
      track_id: currentTrackId
    });
  
    console.log("Sending data:", dataToSend);

    try {
        const response = await axios.post('/user/playlists/add', JSON.stringify( {
            playlist_name: playlistName,
            playlist_description: playlistDescription,
            track_id: trackId
          }),{
            headers: {
              'Content-Type': 'application/json'
            }
          });
        // debugger;
        console.log(response.data);
        const playlist_id = response.data.id; // Get the newly created playlist ID

        // Add the song to the newly created playlist
        // const addSongResponse = await axios.post(`/audio_analysis/${currentTrackId}`, {
        //     track_id: currentTrackId,
        //     playlist_id: playlist_id
        // });

        console.log(addSongResponse.data);
    } catch (error) {
        console.error(error);
    }
});
});

