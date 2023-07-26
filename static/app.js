$(document).ready(function () {
	const myModalElement = $('#myModal');
	const playlistForm = $('#playlist-form');
	const search = $('#search');
	const createPlaylistForm = $('#create-add-playlist');

	let currentTrackId = null;

	myModalElement.on('shown.bs.modal', function (e) {
		const button = $(e.relatedTarget);
		currentTrackId = button.data('track-id');
	});

	playlistForm.on('submit', async function (e) {
		e.preventDefault();
		const playlist_id = $('#playlist').val();

		if (!currentTrackId) {
			console.error('No track ID found');
			return;
		}

		const res = await axios.post(`/audio_analysis/${currentTrackId}`, {
			track_id: currentTrackId,
			playlist_id: playlist_id,
		});
	});

	search.on('submit', function (e) {
		e.preventDefault();
	});

	createPlaylistForm.on('submit', async function (e) {
		e.preventDefault();
		const playlistName = $('#name').val();
		const playlistDescription = $('#description').val();

		const dataToSend = {
			playlist_name: playlistName,
			playlist_description: playlistDescription,
			track_id: currentTrackId,
		};

		const response = await axios.post('/user/playlists/add', dataToSend);
		if (response.status === 200) {
			//append the newly created playlist to the dropdown
			let newPlaylistOption = $('<option></option>').val(response.data.id).text(response.data.name);
			playlistSelect.append(newPlaylistOption);
		}
	});
});

